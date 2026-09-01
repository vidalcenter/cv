#!/usr/bin/env python3
"""Replace all questions/items in an existing Google Form from an activity JSON."""

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from create_forms import build_requests, get_google_service


def load_activity(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def has_file_upload(item: dict) -> bool:
    question = item.get("questionItem", {}).get("question", {})
    return "fileUploadQuestion" in question


def replace_form(
    form_id: str,
    activity: dict,
    drive_name: str | None,
    dry_run: bool = False,
    allow_file_upload_delete: bool = False,
):
    forms = get_google_service("forms", "v1")
    current = forms.forms().get(formId=form_id).execute()
    old_items = current.get("items", [])
    file_upload_count = sum(1 for item in old_items if has_file_upload(item))

    if file_upload_count and not allow_file_upload_delete:
        raise SystemExit(
            f"Refusing to replace form: found {file_upload_count} file-upload item(s). "
            "Google Forms API cannot recreate file-upload questions. "
            "Use --allow-file-upload-delete only if you intentionally want to remove them."
        )

    delete_requests = [
        {"deleteItem": {"location": {"index": 0}}}
        for _ in old_items
    ]

    requests = [
        {
            "updateFormInfo": {
                "info": {"title": activity["title"]},
                "updateMask": "title",
            }
        }
    ]
    requests.extend(delete_requests)
    requests.extend(build_requests(activity))

    new_question_count = sum(
        len(section.get("questions", []))
        for section in activity.get("sections", [])
    )

    print(f"Form ID: {form_id}")
    print(f"Existing items: {len(old_items)}")
    print(f"Existing file-upload items: {file_upload_count}")
    print(f"New questions: {new_question_count}")
    print(f"Batch requests: {len(requests)}")

    if dry_run:
        print("DRY-RUN: no changes applied")
        return

    forms.forms().batchUpdate(
        formId=form_id,
        body={"requests": requests},
    ).execute()

    if drive_name:
        drive = get_google_service("drive", "v3")
        drive.files().update(
            fileId=form_id,
            body={"name": drive_name},
            fields="id,name",
        ).execute()

    updated = forms.forms().get(formId=form_id).execute()
    print(f"Updated title: {updated.get('info', {}).get('title')}")
    print(f"Updated items: {len(updated.get('items', []))}")


def main():
    parser = argparse.ArgumentParser(
        description="Replace an existing Google Form with questions from an activity JSON."
    )
    parser.add_argument("form_id", help="Google Form ID to update")
    parser.add_argument("activity_json", help="Path to the activity JSON")
    parser.add_argument("--drive-name", default=None, help="Optional Drive file name")
    parser.add_argument("--dry-run", action="store_true", help="Show counts only")
    parser.add_argument(
        "--allow-file-upload-delete",
        action="store_true",
        help="Allow deleting file-upload questions. The Forms API cannot recreate them.",
    )
    args = parser.parse_args()

    activity = load_activity(Path(args.activity_json))
    replace_form(
        args.form_id,
        activity,
        args.drive_name,
        dry_run=args.dry_run,
        allow_file_upload_delete=args.allow_file_upload_delete,
    )


if __name__ == "__main__":
    main()
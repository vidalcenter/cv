#!/usr/bin/env python3
"""
update_forms.py — Atualiza a descrição de formulários Google Forms existentes.

Uso:
    python update_forms.py --discipline analise_paisagem
    python update_forms.py --discipline analise_paisagem --dry-run
    python update_forms.py --discipline bioengenharia

Lê os form IDs de formularios_organizados.json (ou formularios_organizados_{discipline}.json)
e aplica a descrição atualizada dos JSONs de atividade via batchUpdate.
"""

import json
import sys
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def get_forms_service():
    """Reutiliza a autenticação do create_forms.py."""
    from create_forms import get_google_service
    return get_google_service("forms", "v1")


def load_form_ids(discipline: str) -> list[dict]:
    """Carrega os IDs dos formulários já criados."""
    # Tenta primeiro o arquivo específico da disciplina
    specific = SCRIPT_DIR / f"formularios_organizados_{discipline}.json"
    generic = SCRIPT_DIR / "formularios_organizados.json"

    if specific.exists():
        path = specific
    elif generic.exists():
        path = generic
    else:
        print(f"❌ Nenhum arquivo de formulários encontrado para '{discipline}'")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    forms = data.get("formularios", [])
    print(f"📋 {len(forms)} formulário(s) encontrado(s) em {path.name}")
    return forms


def load_activity(json_path: Path) -> dict:
    """Carrega o JSON de atividade."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def update_form_description(forms_service, form_id: str, description: str, dry_run: bool = False):
    """Atualiza a descrição de um formulário via batchUpdate."""
    if dry_run:
        preview = description[:120].replace("\n", " ") + "..."
        print(f"     [DRY-RUN] Nova descrição: {preview}")
        return

    forms_service.forms().batchUpdate(
        formId=form_id,
        body={
            "requests": [{
                "updateFormInfo": {
                    "info": {"description": description},
                    "updateMask": "description"
                }
            }]
        }
    ).execute()


def main():
    parser = argparse.ArgumentParser(
        description="Atualiza descrições de Google Forms existentes."
    )
    parser.add_argument(
        "--discipline", type=str, required=True,
        help="Nome da disciplina (ex: analise_paisagem, bioengenharia)."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Mostra o que seria atualizado sem chamar a API."
    )
    args = parser.parse_args()

    # Carregar IDs dos forms existentes
    forms = load_form_ids(args.discipline)

    # Carregar JSONs de atividade
    activity_dir = SCRIPT_DIR / f"atividades_{args.discipline}"
    if not activity_dir.exists():
        print(f"❌ Diretório não encontrado: {activity_dir}")
        sys.exit(1)

    activity_files = sorted(activity_dir.glob("atividade_*.json"))
    if len(activity_files) != len(forms):
        print(f"⚠️  {len(activity_files)} JSONs × {len(forms)} forms — quantidades diferentes")

    # Conectar ao serviço (apenas se não for dry-run)
    forms_service = None
    if not args.dry_run:
        forms_service = get_forms_service()

    print(f"\n{'='*60}")
    print(f"  Atualizando descrições — {args.discipline}")
    print(f"{'='*60}\n")

    updated = 0
    for i, (activity_file, form_info) in enumerate(zip(activity_files, forms)):
        activity = load_activity(activity_file)
        description = activity.get("description", "")
        form_id = form_info["formId"]
        title = form_info.get("titulo", form_info.get("title", "?"))

        print(f"  [{i+1}/{len(forms)}] {title}")
        print(f"     ID: {form_id}")

        if not description:
            print("     ⚠️  Sem descrição no JSON — pulando")
            continue

        update_form_description(forms_service, form_id, description, dry_run=args.dry_run)

        if not args.dry_run:
            print("     ✅ Descrição atualizada")
        updated += 1

    print(f"\n{'='*60}")
    mode = "[DRY-RUN] " if args.dry_run else ""
    print(f"  {mode}{updated}/{len(forms)} formulário(s) atualizado(s)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
create_forms.py — Cria formulários do Google Forms via API a partir de arquivos JSON.

Uso:
    python create_forms.py                          # cria TODOS os formulários
    python create_forms.py atividades/atividade_01.json  # cria apenas 1
    python create_forms.py --list                   # lista atividades disponíveis
    python create_forms.py --dry-run                # mostra o que seria criado sem criar

Pré-requisitos:
    1. Ter um projeto no Google Cloud Console
    2. Ativar Google Forms API e Google Drive API
    3. Criar credenciais OAuth 2.0 (tipo "Desktop")
    4. Baixar o JSON de credenciais e salvar como credentials.json NESTA PASTA
    5. pip install -r requirements.txt

Na primeira execução, abrirá o navegador para autorizar o acesso.
O token será salvo em token.json para reusos futuros.
"""

import json
import os
import sys
import glob
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Autenticação Google
# ---------------------------------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive.file",
]

SCRIPT_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = SCRIPT_DIR / "credentials.json"
TOKEN_FILE = SCRIPT_DIR / "token.json"


def get_google_service(api_name: str, api_version: str):
    """Autentica e retorna o serviço Google API solicitado."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print(
                    "\n❌  Arquivo credentials.json não encontrado!"
                    f"\n   Esperado em: {CREDENTIALS_FILE}"
                    "\n\n   Siga as instruções do README.md para criar as credenciais."
                )
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())

    return build(api_name, api_version, credentials=creds)


# ---------------------------------------------------------------------------
# Builder de requisições para o Forms API
# ---------------------------------------------------------------------------

def _build_text_question(q: dict) -> dict:
    """Constrói textQuestion (SHORT_ANSWER ou PARAGRAPH)."""
    return {
        "textQuestion": {
            "paragraph": q["type"] == "PARAGRAPH"
        }
    }


def _build_choice_question(q: dict) -> dict:
    """Constrói choiceQuestion (MULTIPLE_CHOICE ou CHECKBOX)."""
    qtype = "RADIO" if q["type"] == "MULTIPLE_CHOICE" else "CHECKBOX"
    options = [{"value": opt} for opt in q["options"]]
    return {
        "choiceQuestion": {
            "type": qtype,
            "options": options,
        }
    }


def _build_scale_question(q: dict) -> dict:
    """Constrói scaleQuestion (SCALE)."""
    return {
        "scaleQuestion": {
            "low": q.get("scale_low", 1),
            "high": q.get("scale_high", 5),
            "lowLabel": q.get("scale_low_label", ""),
            "highLabel": q.get("scale_high_label", ""),
        }
    }


QUESTION_BUILDERS = {
    "SHORT_ANSWER": _build_text_question,
    "PARAGRAPH": _build_text_question,
    "MULTIPLE_CHOICE": _build_choice_question,
    "CHECKBOX": _build_choice_question,
    "SCALE": _build_scale_question,
}


def build_requests(activity: dict) -> list:
    """
    Converte a estrutura JSON da atividade em uma lista de requests
    para o Forms API batchUpdate.
    """
    requests = []
    item_index = 0

    # Descrição geral do formulário (update info)
    if activity.get("description"):
        requests.append({
            "updateFormInfo": {
                "info": {
                    "description": activity["description"]
                },
                "updateMask": "description"
            }
        })

    for section in activity.get("sections", []):
        # Adiciona quebra de página (seção) — exceto a primeira
        if item_index > 0:
            req = {
                "createItem": {
                    "item": {
                        "title": section.get("title", ""),
                        "description": section.get("description", ""),
                        "pageBreakItem": {}
                    },
                    "location": {"index": item_index}
                }
            }
            requests.append(req)
            item_index += 1

        for q in section.get("questions", []):
            qtype = q["type"]
            builder = QUESTION_BUILDERS.get(qtype)
            if not builder:
                print(f"  ⚠️  Tipo '{qtype}' não suportado, pulando: {q['title'][:50]}")
                continue

            question_body = builder(q)
            question_body["required"] = q.get("required", False)

            req = {
                "createItem": {
                    "item": {
                        "title": q["title"],
                        "description": q.get("description", ""),
                        "questionItem": {
                            "question": question_body
                        }
                    },
                    "location": {"index": item_index}
                }
            }
            requests.append(req)
            item_index += 1

    return requests


# ---------------------------------------------------------------------------
# Criação do formulário
# ---------------------------------------------------------------------------

def create_form(activity: dict, dry_run: bool = False) -> dict | None:
    """
    Cria um Google Form a partir da estrutura da atividade.
    Retorna dict com 'formId', 'responderUri', 'editUri'.
    """
    title = activity["title"]

    if dry_run:
        reqs = build_requests(activity)
        n_sections = sum(1 for r in reqs if "pageBreakItem" in str(r))
        n_questions = sum(1 for r in reqs if "questionItem" in str(r))
        print(f"  📝 [DRY-RUN] {title}")
        print(f"     {n_sections} seções, {n_questions} perguntas")
        return None

    forms_service = get_google_service("forms", "v1")

    # 1) Criar formulário vazio
    form_body = {"info": {"title": title}}
    result = forms_service.forms().create(body=form_body).execute()
    form_id = result["formId"]
    print(f"  ✅ Formulário criado: {title}")
    print(f"     ID: {form_id}")

    # 2) Adicionar perguntas via batchUpdate
    reqs = build_requests(activity)
    if reqs:
        forms_service.forms().batchUpdate(
            formId=form_id,
            body={"requests": reqs}
        ).execute()
        n_questions = sum(1 for r in reqs if "questionItem" in str(r))
        print(f"     {n_questions} perguntas adicionadas")

    # 3) URLs
    responder_url = f"https://docs.google.com/forms/d/{form_id}/viewform"
    edit_url = f"https://docs.google.com/forms/d/{form_id}/edit"
    print(f"     📋 Responder: {responder_url}")
    print(f"     ✏️  Editar:    {edit_url}")

    return {
        "formId": form_id,
        "responderUri": responder_url,
        "editUri": edit_url,
        "title": title,
    }


# ---------------------------------------------------------------------------
# Função auxiliar — mover para pasta do Drive
# ---------------------------------------------------------------------------

def move_to_drive_folder(form_id: str, folder_id: str):
    """Move o formulário para uma pasta específica do Google Drive."""
    drive_service = get_google_service("drive", "v3")
    file_info = drive_service.files().get(
        fileId=form_id, fields="parents"
    ).execute()
    old_parents = ",".join(file_info.get("parents", []))
    drive_service.files().update(
        fileId=form_id,
        addParents=folder_id,
        removeParents=old_parents,
        fields="id, parents"
    ).execute()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def find_activity_files(subdir: str = None) -> list[Path]:
    """Encontra todos os JSONs de atividade.
    
    Se subdir for informado, busca em atividades_{subdir}/.
    Caso contrário, busca em todas as pastas atividades_*/.
    """
    if subdir:
        pattern = str(SCRIPT_DIR / f"atividades_{subdir}" / "atividade_*.json")
    else:
        pattern = str(SCRIPT_DIR / "atividades_*" / "atividade_*.json")
    files = sorted(glob.glob(pattern))
    return [Path(f) for f in files]


def main():
    parser = argparse.ArgumentParser(
        description="Cria Google Forms a partir de arquivos JSON de atividades."
    )
    parser.add_argument(
        "files", nargs="*",
        help="Caminhos para arquivos JSON específicos. Se vazio, cria todos."
    )
    parser.add_argument(
        "--list", action="store_true",
        help="Lista atividades disponíveis sem criar."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Mostra o que seria criado sem chamar a API."
    )
    parser.add_argument(
        "--folder", type=str, default=None,
        help="ID da pasta do Google Drive para mover os formulários."
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Arquivo JSON para salvar os IDs/URLs dos formulários criados."
    )
    parser.add_argument(
        "--discipline", type=str, default=None,
        help="Subdiretório da disciplina (ex: bioengenharia, analise_paisagem)."
    )
    args = parser.parse_args()

    # Descobrir arquivos
    if args.files:
        files = [Path(f) for f in args.files]
    else:
        files = find_activity_files(args.discipline)

    if not files:
        search_dir = f"atividades_{args.discipline}" if args.discipline else "atividades_*"
        print(f"❌ Nenhum arquivo de atividade encontrado em {search_dir}/")
        print(f"   Diretório verificado: {SCRIPT_DIR}")
        sys.exit(1)

    # --list
    if args.list:
        print(f"\n📚 {len(files)} atividade(s) disponível(is):\n")
        for f in files:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            n_q = sum(len(s.get("questions", [])) for s in data.get("sections", []))
            print(f"  • {f.name}: {data['title']} ({n_q} perguntas)")
        print()
        return

    # Processar
    # Detectar nome da disciplina a partir dos arquivos
    discipline_name = files[0].parent.name.replace("atividades_", "").replace("_", " ").title()
    print(f"\n{'='*60}")
    print(f"  Google Forms Creator — {discipline_name} 2026.1")
    print(f"{'='*60}\n")
    print(f"  Formulários a criar: {len(files)}")
    if args.dry_run:
        print("  ⚠️  MODO DRY-RUN — nenhum formulário será criado\n")
    print()

    results = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            activity = json.load(fh)

        result = create_form(activity, dry_run=args.dry_run)

        if result:
            # Mover para pasta se especificada
            if args.folder:
                move_to_drive_folder(result["formId"], args.folder)
                print(f"     📁 Movido para pasta {args.folder}")

            results.append(result)

        print()

    # Salvar resultados
    if results and args.output:
        out_path = Path(args.output)
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2, ensure_ascii=False)
        print(f"💾 IDs e URLs salvos em: {out_path}\n")

    if results:
        print(f"{'='*60}")
        print(f"  RESUMO — {len(results)} formulário(s) criado(s)")
        print(f"{'='*60}\n")
        for r in results:
            print(f"  {r['title']}")
            print(f"    → {r['responderUri']}\n")

    if not args.dry_run and results:
        # Salvar automaticamente
        auto_output = SCRIPT_DIR / "formularios_criados.json"
        with open(auto_output, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2, ensure_ascii=False)
        print(f"💾 Backup salvo em: {auto_output}")


if __name__ == "__main__":
    main()

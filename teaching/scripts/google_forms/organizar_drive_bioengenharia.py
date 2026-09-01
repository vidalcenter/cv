#!/usr/bin/env python3
"""
organizar_drive_bioengenharia.py — Cria pasta no Drive e organiza os formulários
de Bioengenharia de Solos.

Uso:
    python organizar_drive_bioengenharia.py [--folder FOLDER_ID]

O que faz:
    1. Cria a pasta "Bioengenharia de Solos — 2026.1" no Google Drive
       (ou usa --folder se fornecido)
    2. Cria subpasta "Atividades (Formulários)"
    3. Cria subpasta "Respostas"
    4. Move todos os 10 formulários para a subpasta de atividades
    5. Salva os IDs atualizados em formularios_organizados_bioengenharia.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from create_forms import get_google_service

SCRIPT_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# IDs dos 10 formulários criados
# ---------------------------------------------------------------------------
FORMULARIOS_JSON = SCRIPT_DIR / "formularios_bioengenharia.json"


def carregar_formularios():
    """Carrega os formulários do JSON gerado pelo create_forms.py."""
    with open(FORMULARIOS_JSON, "r", encoding="utf-8") as fh:
        return json.load(fh)


def criar_pasta(drive, nome: str, parent_id: str = None) -> str:
    """Cria uma pasta no Google Drive e retorna o ID."""
    metadata = {
        "name": nome,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]
    pasta = drive.files().create(body=metadata, fields="id").execute()
    return pasta["id"]


def mover_para_pasta(drive, file_id: str, folder_id: str):
    """Move um arquivo para uma pasta no Drive."""
    file_info = drive.files().get(fileId=file_id, fields="parents").execute()
    old_parents = ",".join(file_info.get("parents", []))
    drive.files().update(
        fileId=file_id,
        addParents=folder_id,
        removeParents=old_parents,
        fields="id, parents",
    ).execute()


def renomear_no_drive(drive, file_id: str, novo_nome: str):
    """Renomeia um arquivo no Google Drive."""
    drive.files().update(
        fileId=file_id,
        body={"name": novo_nome},
        fields="id, name",
    ).execute()


def main():
    parser = argparse.ArgumentParser(
        description="Organiza formulários de Bioengenharia de Solos no Google Drive"
    )
    parser.add_argument(
        "--folder",
        help="ID de uma pasta existente no Drive (pula criação da pasta principal)",
    )
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  Organizador de Drive — Bioengenharia de Solos 2026.1")
    print("=" * 60 + "\n")

    formularios = carregar_formularios()
    print(f"  📄 {len(formularios)} formulários carregados de {FORMULARIOS_JSON.name}\n")

    drive = get_google_service("drive", "v3")

    # 1) Pasta principal
    if args.folder:
        pasta_principal_id = args.folder
        print(f"📁 Usando pasta existente: https://drive.google.com/drive/folders/{pasta_principal_id}\n")
    else:
        print("📁 Criando pasta principal no Drive...")
        pasta_principal_id = criar_pasta(drive, "Bioengenharia de Solos — 2026.1")
        print(f"   ✅ Pasta criada: https://drive.google.com/drive/folders/{pasta_principal_id}\n")

    # 2) Subpasta de atividades
    print("📁 Criando subpasta 'Atividades (Formulários)'...")
    pasta_atividades_id = criar_pasta(drive, "Atividades (Formulários)", pasta_principal_id)
    print(f"   ✅ Subpasta criada: https://drive.google.com/drive/folders/{pasta_atividades_id}\n")

    # 3) Subpasta de respostas
    print("📁 Criando subpasta 'Respostas'...")
    pasta_respostas_id = criar_pasta(drive, "Respostas", pasta_principal_id)
    print(f"   ✅ Subpasta criada: https://drive.google.com/drive/folders/{pasta_respostas_id}\n")

    # 4) Mover cada formulário para a subpasta
    print("📝 Movendo formulários para a pasta de atividades...\n")
    resultados = []

    for f in formularios:
        fid = f["formId"]
        titulo = f["title"]

        try:
            # Renomear o arquivo no Drive para manter consistência
            renomear_no_drive(drive, fid, titulo)
            # Mover para subpasta de atividades
            mover_para_pasta(drive, fid, pasta_atividades_id)

            print(f"   ✅ {titulo}")
            resultados.append({
                "formId": fid,
                "titulo": titulo,
                "responderUri": f["responderUri"],
                "editUri": f["editUri"],
            })
        except Exception as e:
            print(f"   ❌ Erro em {fid}: {e}")

    # 5) Salvar resultado
    output = {
        "pasta_principal": {
            "id": pasta_principal_id,
            "url": f"https://drive.google.com/drive/folders/{pasta_principal_id}",
            "nome": "Bioengenharia de Solos — 2026.1",
        },
        "subpastas": {
            "atividades": {
                "id": pasta_atividades_id,
                "url": f"https://drive.google.com/drive/folders/{pasta_atividades_id}",
            },
            "respostas": {
                "id": pasta_respostas_id,
                "url": f"https://drive.google.com/drive/folders/{pasta_respostas_id}",
            },
        },
        "formularios": resultados,
    }

    out_path = SCRIPT_DIR / "formularios_organizados_bioengenharia.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultado salvo em: {out_path}")
    print(f"\n{'=' * 60}")
    print(f"  RESUMO")
    print(f"{'=' * 60}")
    print(f"  📁 Pasta principal: {output['pasta_principal']['url']}")
    print(f"  📁 Atividades:      {output['subpastas']['atividades']['url']}")
    print(f"  📁 Respostas:       {output['subpastas']['respostas']['url']}")
    print(f"  📝 Formulários:     {len(resultados)} organizados")
    print()


if __name__ == "__main__":
    main()

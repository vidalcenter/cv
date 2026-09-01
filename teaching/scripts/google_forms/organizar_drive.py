#!/usr/bin/env python3
"""
organizar_drive.py — Cria pasta no Drive e organiza os formulários da disciplina.

Uso:
    python organizar_drive.py

O que faz:
    1. Cria a pasta "Análise da Paisagem — 2026.1" no Google Drive
    2. Cria subpasta "Atividades (Formulários)"
    3. Move todos os 8 formulários para a subpasta
    4. Renomeia cada formulário com prefixo padronizado
    5. Salva os IDs atualizados em formularios_organizados.json
"""

import json
import sys
from pathlib import Path

# Reutiliza autenticação do create_forms.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
from create_forms import get_google_service

SCRIPT_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# IDs dos 8 formulários criados (execuções anteriores)
# ---------------------------------------------------------------------------
FORMULARIOS = [
    {
        "formId": "1jsgmExs6KHEp8WlJgix1eBDi6IhGWFyjz3JmodDPj78",
        "titulo_atual": "Atividade 01 — Leitura Perceptiva da Paisagem Local",
        "novo_nome": "[AP 2026.1] Atividade 01 — Leitura Perceptiva da Paisagem Local",
    },
    {
        "formId": "1SL0g-hBGbrWQQw2EgVMFoaYiTp7Y5-QvZRIk57-GsHc",
        "titulo_atual": "Atividade 03 — Resenhas: Ecologia da Paisagem",
        "novo_nome": "[AP 2026.1] Atividade 03 — Resenhas: Ecologia da Paisagem",
    },
    {
        "formId": "1l8oOX1VOS76NAi-AOzSOpvVNlLn36COWnpStqTDRDZ0",
        "titulo_atual": "Atividade 04 — Geossistema, ECL e Modelo MCM",
        "novo_nome": "[AP 2026.1] Atividade 04 — Geossistema, ECL e Modelo MCM",
    },
    {
        "formId": "1wfO176DLftksxDUGtpyDWHQo1fYUdcX_5WkoAI1kREc",
        "titulo_atual": "Atividade 05 — Escalas, Fragmentação e Resiliência da Paisagem",
        "novo_nome": "[AP 2026.1] Atividade 05 — Escalas, Fragmentação e Resiliência",
    },
    {
        "formId": "1hBynSWyQWyMA-HfuajzQ0ZewSFFM5FKFB0w3alpCNOE",
        "titulo_atual": "Atividade 06 — Leitura Cartográfica e Interpretação Visual da Paisagem",
        "novo_nome": "[AP 2026.1] Atividade 06 — Cartografia e Interpretação Visual",
    },
    {
        "formId": "1bMcN_dboUmwu2he7T6DMPoRk121iLE1sy6PF3XRTGS0",
        "titulo_atual": "Atividade 07 — Sensoriamento Remoto: do Pixel à Paisagem",
        "novo_nome": "[AP 2026.1] Atividade 07 — Sensoriamento Remoto: do Pixel à Paisagem",
    },
    {
        "formId": "1XRZlXYvekKgVqJE4MWtW_HvOZIm0ouAWJO1ErUjLHE8",
        "titulo_atual": "Atividade 08 — FRAGSTATS, Grafos e Conectividade",
        "novo_nome": "[AP 2026.1] Atividade 08 — FRAGSTATS, Grafos e Conectividade",
    },
    {
        "formId": "1ldpBU-oTivThjYkHIxIewHsQnEIOmTzp1laEgoWUIL4",
        "titulo_atual": "Atividade 09 — Do Diagnóstico à Ação",
        "novo_nome": "[AP 2026.1] Atividade 09 — Diagnóstico, Zoneamento e Diretrizes",
    },
]

# Formulário 06 vazio (criado antes do erro) — será deletado
FORM_VAZIO_ID = "1CxVOq6Xh87OlZrfuFhgmQchLA9mpoMJGmY--4G_sk94"


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


def renomear_formulario(forms, form_id: str, novo_titulo: str):
    """Atualiza o título do formulário via Forms API."""
    forms.forms().batchUpdate(
        formId=form_id,
        body={
            "requests": [
                {
                    "updateFormInfo": {
                        "info": {"title": novo_titulo},
                        "updateMask": "title",
                    }
                }
            ]
        },
    ).execute()


def main():
    print("\n" + "=" * 60)
    print("  Organizador de Drive — Análise da Paisagem 2026.1")
    print("=" * 60 + "\n")

    drive = get_google_service("drive", "v3")
    forms = get_google_service("forms", "v1")

    # 1) Criar pasta principal
    print("📁 Criando pasta principal no Drive...")
    pasta_principal_id = criar_pasta(drive, "Análise da Paisagem — 2026.1")
    print(f"   ✅ Pasta criada: https://drive.google.com/drive/folders/{pasta_principal_id}\n")

    # 2) Criar subpasta de atividades
    print("📁 Criando subpasta 'Atividades (Formulários)'...")
    pasta_atividades_id = criar_pasta(drive, "Atividades (Formulários)", pasta_principal_id)
    print(f"   ✅ Subpasta criada: https://drive.google.com/drive/folders/{pasta_atividades_id}\n")

    # 3) Criar subpasta de respostas
    print("📁 Criando subpasta 'Respostas'...")
    pasta_respostas_id = criar_pasta(drive, "Respostas", pasta_principal_id)
    print(f"   ✅ Subpasta criada: https://drive.google.com/drive/folders/{pasta_respostas_id}\n")

    # 4) Renomear e mover cada formulário
    print("📝 Renomeando e movendo formulários...\n")
    resultados = []

    for f in FORMULARIOS:
        fid = f["formId"]
        novo = f["novo_nome"]

        try:
            # Renomear título interno do formulário
            renomear_formulario(forms, fid, novo)
            # Renomear no Drive (nome do arquivo)
            renomear_no_drive(drive, fid, novo)
            # Mover para subpasta
            mover_para_pasta(drive, fid, pasta_atividades_id)

            print(f"   ✅ {novo}")
            resultados.append({
                "formId": fid,
                "titulo": novo,
                "responderUri": f"https://docs.google.com/forms/d/{fid}/viewform",
                "editUri": f"https://docs.google.com/forms/d/{fid}/edit",
            })
        except Exception as e:
            print(f"   ❌ Erro em {fid}: {e}")

    # 5) Deletar formulário vazio (06 com erro)
    print(f"\n🗑️  Deletando formulário 06 vazio (ID: {FORM_VAZIO_ID})...")
    try:
        drive.files().delete(fileId=FORM_VAZIO_ID).execute()
        print("   ✅ Deletado com sucesso.")
    except Exception as e:
        print(f"   ⚠️  Não foi possível deletar: {e}")

    # 6) Salvar resultado
    output = {
        "pasta_principal": {
            "id": pasta_principal_id,
            "url": f"https://drive.google.com/drive/folders/{pasta_principal_id}",
            "nome": "Análise da Paisagem — 2026.1",
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

    out_path = SCRIPT_DIR / "formularios_organizados.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultado salvo em: {out_path}")
    print(f"\n{'='*60}")
    print(f"  RESUMO")
    print(f"{'='*60}")
    print(f"  📁 Pasta principal: {output['pasta_principal']['url']}")
    print(f"  📁 Atividades:      {output['subpastas']['atividades']['url']}")
    print(f"  📁 Respostas:       {output['subpastas']['respostas']['url']}")
    print(f"  📝 Formulários:     {len(resultados)} organizados")
    print()


if __name__ == "__main__":
    main()

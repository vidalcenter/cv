#!/usr/bin/env python3
"""Fix mojibake/replacement characters in Atividade 03 Google Form text."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from create_forms import get_google_service


FORM_ID = "1SL0g-hBGbrWQQw2EgVMFoaYiTp7Y5-QvZRIk57-GsHc"


TEXT = {
    "title": "[AP 2026.1] Atividade 03 \u2014 Resenhas: Ecologia da Paisagem",
    "description": (
        "Esta atividade corresponde \u00e0 Aula 3.1 \u2014 Ecologia da Paisagem: "
        "matriz, mancha e corredor.\n\n"
        "Leia os dois artigos em PDF disponibilizados na pasta da aula:\n"
        "- METZGER, J. P. (2001). O que \u00e9 ecologia de paisagens?\n"
        "- CASIMIRO, P. C. (2009). Estrutura, composi\u00e7\u00e3o e "
        "configura\u00e7\u00e3o da paisagem: conceitos e princ\u00edpios para a sua "
        "quantifica\u00e7\u00e3o no \u00e2mbito da ecologia da paisagem.\n\n"
        "Antes de responder \u00e0s quest\u00f5es, envie no formul\u00e1rio os "
        "resumos/resenhas em PDF: um arquivo para o artigo de Metzger e um "
        "arquivo para o artigo de Casimiro. Depois, responda \u00e0s 3 quest\u00f5es "
        "de compreens\u00e3o e aplica\u00e7\u00e3o.\n\n"
        "Prazo de entrega: at\u00e9 o in\u00edcio da pr\u00f3xima aula, salvo orienta\u00e7\u00e3o em sala."
    ),
    "name": "Nome completo",
    "matricula": "Matr\u00edcula",
    "upload_section_title": "Envio dos resumos em PDF",
    "upload_section_description": (
        "Antes de responder \u00e0s quest\u00f5es, envie dois arquivos em PDF: um "
        "resumo/resenha do artigo de Metzger (2001) e um resumo/resenha do "
        "artigo de Casimiro (2009)."
    ),
    "metzger_upload_title": "Resumo/resenha em PDF \u2014 Metzger (2001)",
    "metzger_upload_description": (
        "Envie aqui o arquivo PDF com seu resumo/resenha do artigo de Metzger. "
        "Identifique o arquivo com seu nome e o autor do texto."
    ),
    "casimiro_upload_title": "Resumo/resenha em PDF \u2014 Casimiro (2009)",
    "casimiro_upload_description": (
        "Envie aqui o arquivo PDF com seu resumo/resenha do artigo de Casimiro. "
        "Identifique o arquivo com seu nome e o autor do texto."
    ),
    "questions_section_title": "Quest\u00f5es de compreens\u00e3o e aplica\u00e7\u00e3o",
    "questions_section_description": "Ap\u00f3s enviar os PDFs, responda \u00e0s tr\u00eas quest\u00f5es abaixo.",
    "q1_title": (
        "Quest\u00e3o 1 \u2014 Em Metzger (2001), por que a paisagem depende do "
        "observador e da escala de observa\u00e7\u00e3o? D\u00ea um exemplo."
    ),
    "q1_description": (
        "M\u00ednimo 5 linhas. Relacione sua resposta \u00e0 ideia de mosaico "
        "heterog\u00eaneo e \u00e0s abordagens geogr\u00e1fica/ecol\u00f3gica."
    ),
    "q2_title": (
        "Quest\u00e3o 2 \u2014 Em Casimiro (2009), diferencie composi\u00e7\u00e3o e "
        "configura\u00e7\u00e3o da paisagem e cite um exemplo de m\u00e9trica ou "
        "atributo para cada dimens\u00e3o."
    ),
    "q2_description": (
        "M\u00ednimo 5 linhas. Use exemplos como classes de uso/cobertura, \u00e1rea "
        "de manchas, forma, borda, isolamento ou conectividade."
    ),
    "q3_title": (
        "Quest\u00e3o 3 \u2014 Como os dois artigos ajudam a aplicar o modelo "
        "matriz-mancha-corredor a uma paisagem real?"
    ),
    "q3_description": (
        "M\u00ednimo 6 linhas. Relacione Metzger e Casimiro aos conceitos de "
        "mosaico, matriz, manchas, corredores, escala, estrutura, composi\u00e7\u00e3o "
        "e configura\u00e7\u00e3o."
    ),
}


def update_item_request(item: dict, index: int, title: str, description: str = "") -> dict:
    updated_item = dict(item)
    updated_item["title"] = title
    if description:
        updated_item["description"] = description
        mask = "title,description"
    else:
        updated_item.pop("description", None)
        mask = "title"
    return {
        "updateItem": {
            "item": updated_item,
            "location": {"index": index},
            "updateMask": mask,
        }
    }


def question_kind(item: dict) -> str:
    question = item.get("questionItem", {}).get("question", {})
    if "fileUploadQuestion" in question:
        return "upload"
    if "textQuestion" in question:
        return "text"
    if "questionItem" in item:
        return "question"
    if "pageBreakItem" in item:
        return "section"
    return "other"


def main():
    forms = get_google_service("forms", "v1")
    form = forms.forms().get(formId=FORM_ID).execute()
    items = form.get("items", [])

    requests = [
        {
            "updateFormInfo": {
                "info": {"title": TEXT["title"], "description": TEXT["description"]},
                "updateMask": "title,description",
            }
        }
    ]

    text_question_number = 0
    upload_number = 0
    section_number = 0

    for index, item in enumerate(items):
        kind = question_kind(item)
        if kind == "section":
            section_number += 1
            if section_number == 1:
                requests.append(
                    update_item_request(
                        item,
                        index,
                        TEXT["upload_section_title"],
                        TEXT["upload_section_description"],
                    )
                )
            elif section_number == 2:
                requests.append(
                    update_item_request(
                        item,
                        index,
                        TEXT["questions_section_title"],
                        TEXT["questions_section_description"],
                    )
                )
        elif kind == "upload":
            upload_number += 1
            if upload_number == 1:
                requests.append(
                    update_item_request(
                        item,
                        index,
                        TEXT["metzger_upload_title"],
                        TEXT["metzger_upload_description"],
                    )
                )
            elif upload_number == 2:
                requests.append(
                    update_item_request(
                        item,
                        index,
                        TEXT["casimiro_upload_title"],
                        TEXT["casimiro_upload_description"],
                    )
                )
        elif kind == "text":
            text_question_number += 1
            if text_question_number == 1:
                requests.append(update_item_request(item, index, TEXT["name"]))
            elif text_question_number == 2:
                requests.append(update_item_request(item, index, TEXT["matricula"]))
            elif text_question_number == 3:
                requests.append(update_item_request(item, index, TEXT["q1_title"], TEXT["q1_description"]))
            elif text_question_number == 4:
                requests.append(update_item_request(item, index, TEXT["q2_title"], TEXT["q2_description"]))
            elif text_question_number == 5:
                requests.append(update_item_request(item, index, TEXT["q3_title"], TEXT["q3_description"]))

    forms.forms().batchUpdate(formId=FORM_ID, body={"requests": requests}).execute()

    updated = forms.forms().get(formId=FORM_ID).execute()
    updated_items = updated.get("items", [])
    print(updated.get("info", {}).get("title"))
    print(updated.get("info", {}).get("description"))
    for index, item in enumerate(updated_items):
        print(index, question_kind(item), "|", item.get("title", ""))
    print("upload_count", sum(1 for item in updated_items if question_kind(item) == "upload"))
    print("text_question_count", sum(1 for item in updated_items if question_kind(item) == "text"))


if __name__ == "__main__":
    main()
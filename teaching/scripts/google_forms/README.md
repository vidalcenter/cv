# Google Forms Creator — Análise da Paisagem (2026.1)

Script Python que cria automaticamente os formulários de atividades da disciplina **Análise da Paisagem** via [Google Forms API v1](https://developers.google.com/forms/api).

## Estrutura

```
scripts/google_forms/
├── create_forms.py          # Script principal
├── requirements.txt         # Dependências Python
├── credentials.json         # ← Você cria (ver abaixo)
├── token.json               # Gerado automaticamente após 1ª autenticação
├── formularios_criados.json # Gerado após execução (IDs e URLs)
├── README.md                # Este arquivo
└── atividades/
    ├── atividade_01.json    # Aula 01: Percepção de paisagem
    ├── atividade_02.json    # Atividade 03: resenhas sobre Ecologia da Paisagem
    ├── atividade_03.json    # Atividade 04: geossistema, ECL, MCM
    ├── atividade_04.json    # Atividade 05: escala, fragmentação
    ├── atividade_05.json    # Atividade 06: cartografia + interpretação
    ├── atividade_06.json    # Atividade 07: sensoriamento remoto
    ├── atividade_07.json    # Atividade 08: FRAGSTATS, grafos
    └── atividade_08.json    # Atividade 09: diagnóstico, zoneamento
```

## Pré-requisitos

### 1. Criar projeto no Google Cloud Console

1. Acesse [console.cloud.google.com](https://console.cloud.google.com/)
2. Crie um novo projeto (ex.: `analise-paisagem-forms`)
3. No menu lateral, vá em **APIs e Serviços → Biblioteca**
4. Ative:
   - **Google Forms API**
   - **Google Drive API**

### 2. Criar credenciais OAuth 2.0

1. Vá em **APIs e Serviços → Credenciais**
2. Clique em **Criar credenciais → ID do cliente OAuth**
3. Tipo de aplicativo: **App para computador**
4. Baixe o JSON e salve como `credentials.json` **nesta pasta**

> **Nota:** Na primeira execução, o script abrirá o navegador para que você autorize o acesso à sua conta Google. O token será salvo em `token.json` para usos futuros.

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

## Uso

### Criar todos os formulários

```bash
python create_forms.py
```

### Criar apenas um formulário específico

```bash
python create_forms.py atividades/atividade_01.json
```

### Listar atividades disponíveis

```bash
python create_forms.py --list
```

### Dry-run (sem criar nada)

```bash
python create_forms.py --dry-run
```

### Mover formulários para uma pasta do Drive

```bash
python create_forms.py --folder ID_DA_PASTA_NO_DRIVE
```

### Salvar IDs/URLs em arquivo específico

```bash
python create_forms.py --output meus_forms.json
```

## Saída

Após a execução, o script:

1. Imprime URLs de cada formulário criado (para responder e para editar)
2. Salva automaticamente `formularios_criados.json` com todos os IDs e URLs

## Limitações da API

A Google Forms API **NÃO** permite configurar via código:

| Recurso | Solução |
|---------|---------|
| Coletar e-mails | Configurar manualmente em ⚙️ Configurações |
| Limitar a 1 resposta | Configurar manualmente em ⚙️ Configurações |
| Mensagem de confirmação | Configurar manualmente em ⚙️ Configurações |
| Tema/cores | Configurar manualmente na interface |
| Perguntas de upload de arquivo/PDF | Criar e manter manualmente na interface |
| Inserir imagens nas perguntas | Upload manual ou via Google Drive API |

**Após criar os formulários, abra cada um e configure esses itens manualmente.**

## Tipos de pergunta suportados

| Tipo no JSON | Tipo no Google Forms |
|-------------|---------------------|
| `SHORT_ANSWER` | Resposta curta |
| `PARAGRAPH` | Parágrafo |
| `MULTIPLE_CHOICE` | Múltipla escolha (radio) |
| `CHECKBOX` | Caixas de seleção |
| `SCALE` | Escala linear |

## Formato do JSON de atividade

```json
{
  "title": "Título do formulário",
  "description": "Descrição geral",
  "sections": [
    {
      "title": "Nome da seção",
      "description": "Descrição da seção",
      "questions": [
        {
          "title": "Texto da pergunta",
          "description": "Texto de ajuda (opcional)",
          "type": "MULTIPLE_CHOICE",
          "required": true,
          "options": ["Opção A", "Opção B", "Opção C"]
        },
        {
          "title": "Pergunta de escala",
          "type": "SCALE",
          "required": true,
          "scale_low": 1,
          "scale_high": 5,
          "scale_low_label": "Nada confiante",
          "scale_high_label": "Muito confiante"
        }
      ]
    }
  ]
}
```

## Segurança

- **Nunca faça commit** de `credentials.json` ou `token.json`
- Adicione ao `.gitignore`:
  ```
  scripts/google_forms/credentials.json
  scripts/google_forms/token.json
  ```

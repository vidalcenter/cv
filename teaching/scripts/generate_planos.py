#!/usr/bin/env python3
"""
Convert plano-pdf.qmd files to the new LaTeX template (plano-pdf.tex).
Uses tcolorbox, tabularx+booktabs, multicols, and UEFS institutional branding.
"""
import re, os

WORKSPACE = r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\meu_site"

# ═══════════════════════════════════════════════════════════
# PREAMBLE (shared by all disciplines)
# ═══════════════════════════════════════════════════════════
PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[portuguese]{babel}
\usepackage{geometry}
\usepackage{helvet}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage[table]{xcolor}
\usepackage{hyperref}
\usepackage{tabularx}
\usepackage{booktabs}
\usepackage{fancyhdr}
\usepackage[most]{tcolorbox}
\usepackage{multicol}
\usepackage{ragged2e}
\usepackage{graphicx}
\usepackage{lastpage}

\geometry{margin=2.2cm, top=2.8cm, bottom=2.5cm}
\setlength{\headheight}{15pt}
\renewcommand{\familydefault}{\sfdefault}

% ── Paleta de cores ──
\definecolor{uefsdark}{RGB}{0,51,102}
\definecolor{uefsblue}{RGB}{25,84,150}
\definecolor{uefslight}{RGB}{232,241,250}
\definecolor{uefsgray}{RGB}{110,110,110}
\definecolor{uefsaccent}{RGB}{180,60,40}

% ── Seções ──
\titleformat{\section}
  {\normalfont\large\bfseries\color{uefsdark}\scshape}{}{0em}{}%%
  [\vspace{2pt}{\color{uefsdark}\titlerule}]
\titlespacing{\section}{0pt}{20pt}{8pt}

\titleformat{\subsection}
  {\normalfont\normalsize\bfseries\color{uefsblue}}{}{0em}{}
\titlespacing{\subsection}{0pt}{12pt}{4pt}

% ── Listas ──
\setlist[itemize]{leftmargin=1.5em,topsep=4pt,itemsep=2pt,parsep=0pt}
\setlist[enumerate]{leftmargin=2em,topsep=4pt,itemsep=4pt,parsep=0pt}

% ── tcolorbox ──
\tcbset{
  uefsbox/.style={
    colback=uefslight, colframe=uefsdark,
    boxrule=0.4pt, arc=3pt,
    left=8pt, right=8pt, top=6pt, bottom=6pt,
    fontupper=\small
  },
  ementabox/.style={
    colback=white, colframe=uefsdark,
    boxrule=0.8pt, arc=0pt,
    left=10pt, right=10pt, top=8pt, bottom=8pt,
    title={\scshape\bfseries Ementa},
    fonttitle=\large\color{white},
    coltitle=white, colbacktitle=uefsdark,
    attach boxed title to top left={yshift=-2mm,xshift=2mm},
    boxed title style={arc=2pt,boxrule=0pt}
  }
}
"""

def make_header_footer(header_left, header_right="Plano de Ensino 2026.1"):
    return rf"""
% ── Cabeçalho / Rodapé ──
\pagestyle{{fancy}}
\fancyhf{{}}
\renewcommand{{\headrulewidth}}{{0.4pt}}
\renewcommand{{\headrule}}{{\hbox to\headwidth{{\color{{uefsdark}}\leaders\hrule height \headrulewidth\hfill}}}}
\fancyhead[L]{{\small\color{{uefsgray}}{header_left}}}
\fancyhead[R]{{\small\color{{uefsgray}}{header_right}}}
\fancyfoot[C]{{\small\color{{uefsgray}}Página \thepage\ de \pageref{{LastPage}}}}

\hypersetup{{colorlinks=true,linkcolor=uefsblue,urlcolor=uefsblue}}
"""

def make_cover_uefs(department, course, title, subtitle, info_rows, has_logo=True):
    """Generate cover block. info_rows = list of (label, value) tuples."""
    logo_path = "../../aulas/assets/logo-uefs.png"
    
    if has_logo:
        header_block = rf"""
\begin{{center}}
\color{{uefsdark}}\rule{{\textwidth}}{{1.2pt}}\\[0.30cm]
\begin{{minipage}}{{0.12\textwidth}}
\includegraphics[width=\linewidth]{{{logo_path}}}
\end{{minipage}}\hfill
\begin{{minipage}}{{0.84\textwidth}}
\begin{{center}}
{{\Large\bfseries UNIVERSIDADE ESTADUAL DE FEIRA DE SANTANA}}\\[0.15cm]
{{\normalsize {department}}}\\[0.06cm]
{{\normalsize {course}}}
\end{{center}}
\end{{minipage}}\\[0.30cm]
\color{{uefsdark}}\rule{{\textwidth}}{{1.2pt}}
\end{{center}}
"""
    else:
        # UNIVASF - no logo
        header_block = rf"""
\begin{{center}}
\color{{uefsdark}}\rule{{\textwidth}}{{1.2pt}}\\[0.30cm]
{{\Large\bfseries UNIVERSIDADE FEDERAL DO VALE DO SÃO FRANCISCO}}\\[0.15cm]
{{\normalsize {department}}}\\[0.06cm]
{{\normalsize {course}}}\\[0.30cm]
\color{{uefsdark}}\rule{{\textwidth}}{{1.2pt}}
\end{{center}}
"""

    # Build info table rows
    info_tex = ""
    for label, value in info_rows:
        info_tex += rf"\textbf{{{label}:}} & {value} \\" + "\n"

    body = rf"""
\vspace{{0.6cm}}

\begin{{center}}
{{\LARGE\bfseries\color{{uefsdark}} {title}}}\\[0.30cm]
{{\large\bfseries {subtitle}}}
\end{{center}}

\vspace{{0.4cm}}

% ── Identificação ──
\begin{{tcolorbox}}[uefsbox]
\renewcommand{{\arraystretch}}{{1.25}}
\begin{{tabularx}}{{\textwidth}}{{@{{}}l X@{{}}}}
{info_tex}\end{{tabularx}}
\end{{tcolorbox}}

\vspace{{0.3cm}}
"""
    return header_block + body


def make_ementabox(ementa_text):
    return rf"""
\begin{{tcolorbox}}[ementabox]
{ementa_text}
\end{{tcolorbox}}
"""


def make_avaliacao_box(items):
    """items = list of strings like 'Description\\,\\dotfill\\,\\textbf{25\\,\\%}'"""
    item_tex = "\n".join(rf"\item {it}" for it in items)
    return rf"""
\begin{{tcolorbox}}[uefsbox, colframe=uefsaccent, colback=white, title={{\bfseries\color{{white}}\scshape Avaliação}}, fonttitle=\normalsize, coltitle=white, colbacktitle=uefsaccent, attach boxed title to top left={{yshift=-2mm,xshift=2mm}}, boxed title style={{arc=2pt,boxrule=0pt}}]
\begin{{itemize}}[leftmargin=1.2em]
{item_tex}
\end{{itemize}}
\vspace{{4pt}}
{{\footnotesize Cada avaliação vale até 10,0 pontos. Média final = média aritmética simples.}}
\end{{tcolorbox}}
"""


def make_cronograma_tabularx(rows, note=""):
    """rows = list of tuples (enc, data_or_sem, tema, is_highlight, is_feriado)"""
    body_lines = []
    for enc, dt, tema, is_highlight, is_feriado in rows:
        if is_feriado:
            body_lines.append(rf"\rowcolor{{uefslight}}")
            body_lines.append(rf"{enc} & {dt} & \textit{{{tema}}} \\")
        elif is_highlight:
            body_lines.append(rf"\rowcolor{{uefslight!70!white}}")
            body_lines.append(rf"\textbf{{{enc}}} & \textbf{{{dt}}} & \textbf{{{tema}}} \\")
        else:
            body_lines.append(rf"{enc} & {dt} & {tema} \\")
    
    body_tex = "\n".join(body_lines)
    
    result = rf"""
\begin{{small}}
\renewcommand{{\arraystretch}}{{1.35}}
\begin{{tabularx}}{{\textwidth}}{{@{{}}c c X@{{}}}}
\toprule
\textbf{{Enc.}} & \textbf{{Sem.}} & \textbf{{Tema}} \\
\midrule
{body_tex}
\bottomrule
\end{{tabularx}}
\end{{small}}
"""
    if note:
        result += rf"""
\begin{{tcolorbox}}[uefsbox]
{note}
\end{{tcolorbox}}
"""
    return result


def make_bibliography(basica_items, complementar_items):
    def format_items(items):
        return "\n\n".join(rf"\hangindent=1.5em\hangafter=1" + "\n" + it + r"\par\medskip" for it in items)
    
    return rf"""
\section*{{Referências}}

\subsection*{{Básica}}

\begin{{small}}
{format_items(basica_items)}
\end{{small}}

\subsection*{{Complementar}}

\begin{{small}}
{format_items(complementar_items)}
\end{{small}}
"""


def make_signature(name="Prof.\\,Dr.\\,Luiz Diego Vidal Santos", location="Feira de Santana\\,--\\,BA, fevereiro de 2026."):
    return rf"""
\vfill

\begin{{center}}
\noindent\rule{{6cm}}{{0.4pt}}\\[6pt]
\textbf{{{name}}}\\
Docente Responsável\\[4pt]
{{\small {location}}}
\end{{center}}

\end{{document}}
"""


# ═══════════════════════════════════════════════════════════
# DISCIPLINE DEFINITIONS
# ═══════════════════════════════════════════════════════════

disciplines = {}

# ─── 1. BIOENGENHARIA DE SOLOS ───
disciplines["bioengenharia-de-solos"] = {
    "header_left": r"UEFS\,--\,Bioengenharia de Solos",
    "department": "Departamento de Tecnologia\\,(DTEC)",
    "course": "Curso de Engenharia Agronômica",
    "title": "Bioengenharia de Solos",
    "subtitle": r"Plano de Ensino\,--\,2026.1",
    "has_logo": True,
    "info": [
        ("Carga Horária", r"60\,h\,--\,21 encontros (teoria + prática)"),
        ("Horário", "A definir"),
        ("Período", "2026.1"),
        ("Modalidade", "Presencial"),
        ("Docente", r"Prof.\,Dr.\,Luiz Diego Vidal Santos"),
        ("Contato", r"\href{mailto:ldvsantos@uefs.br}{ldvsantos@uefs.br}\enspace·\enspace\href{https://orcid.org/0000-0001-8659-8557}{ORCID: 0000-0001-8659-8557}"),
    ],
    "ementa": r"Formação dos solos tropicais; intemperismo e transformação do solo; classificação e propriedades dos solos; processos erosivos; declividade e equipamentos; controle de erosão hídrica e terraceamento; canais escoadouros (teoria e prática); modelagem 3D de sistemas radiculares; paliçadas para controle de ravinas; bacias de captação (barraginhas); feixes vivos e drenos verdes; hidrossemeadura; biomantas e geossintéticos biodegradáveis; enrocamento vegetado; cordões vegetativos e fascinas; gabião vivo; parede Krainer e riprap; bioengenharia fluvial avançada; canaleta verde (\textit{vegetated swale}); projeto integrador.",
    "objetivo_geral": r"Capacitar o(a) discente a compreender os processos de formação, degradação e erosão dos solos tropicais, dominando os fundamentos e as técnicas de bioengenharia de solos para estabilização de encostas, controle de erosão e restauração de áreas degradadas, integrando engenharia geotécnica e ecológica.",
    "objetivos_especificos": [
        "Compreender os processos de formação, intemperismo e transformação dos solos tropicais.",
        "Identificar e classificar processos erosivos e os fatores condicionantes associados.",
        "Dimensionar e projetar estruturas de controle de erosão hídrica, incluindo terraços e canais escoadouros.",
        r"Aplicar técnicas de bioengenharia vegetal (paliçadas, feixes vivos, hidrossemeadura, biomantas) em cenários reais de degradação.",
        "Projetar e avaliar estruturas combinadas de engenharia natural (gabiões vivos, paredes Krainer, enrocamento vegetado).",
        "Utilizar ferramentas de modelagem 3D para análise de sistemas radiculares e sua contribuição na estabilização de taludes.",
        "Integrar múltiplas técnicas de bioengenharia em projetos completos de estabilização e restauração ambiental.",
    ],
    "competencias_cols": [
        (r"Competências Técnicas", [
            "Diagnosticar processos erosivos e identificar fatores condicionantes em diferentes contextos geomorfológicos",
            "Selecionar e dimensionar técnicas de bioengenharia adequadas (tipo de solo, declividade, regime hídrico, vegetação)",
            "Projetar canais escoadouros, terraços e sistemas de drenagem com fundamentação hidráulica",
        ]),
        (r"Competências de Projeto", [
            "Elaborar projetos integrados de estabilização de encostas e margens fluviais",
            "Combinar técnicas vegetativas e estruturais em soluções de engenharia natural",
            "Utilizar modelagem 3D para análise de sistemas radiculares",
        ]),
        (r"Competências de Campo", [
            "Realizar monitoramento e avaliação de desempenho de intervenções de bioengenharia",
            "Conduzir implantação de técnicas em campo com controle de qualidade",
            "Identificar espécies vegetais adequadas para cada técnica e contexto",
        ]),
        (r"Competências Comunicativas", [
            "Comunicar resultados técnicos em relatórios, plantas e memoriais descritivos",
            "Defender projetos integradores com fundamentação técnico-científica",
            "Articular saberes de pedologia, hidráulica e ecologia em soluções integradas",
        ]),
    ],
    "cronograma": [
        ("01", r"1\textsuperscript{a}", "Formação dos Solos Tropicais: do clima à química, dinâmica dos solos.", False, False),
        ("02", r"2\textsuperscript{a}", "Intemperismo e Transformação do Solo: processos físicos e químicos.", False, False),
        ("03", r"3\textsuperscript{a}", "O Solo: classificação, propriedades físicas, químicas e mecânicas (SiBCS).", False, False),
        ("04", r"4\textsuperscript{a}", "Solo e Erosão: processos erosivos, erodibilidade, erosividade, RUSLE.", False, False),
        ("05", r"5\textsuperscript{a}", "Declividade e Equipamentos: clinômetro, GPS, aplicativos móveis.", False, False),
        ("06", r"6\textsuperscript{a}", "Controle de Erosão Hídrica: terraceamento, práticas conservacionistas.", False, False),
        ("07", r"7\textsuperscript{a}", "Canal Escoadouro (Teoria): dimensionamento hidráulico, Manning.", False, False),
        ("08", r"8\textsuperscript{a}", "Canal Escoadouro (Prática): implantação em campo, gramíneas.", False, False),
        ("09", r"9\textsuperscript{a}", "Modelagem 3D de Raízes: fotogrametria, CloudCompare, ancoragem.", False, False),
        ("10", r"10\textsuperscript{a}", r"Paliçadas: check dams de bambu, dimensionamento, biodegradação.", False, False),
        ("11", r"11\textsuperscript{a}", "Bacias de Captação (Barraginhas): projeto, infiltração, recarga.", False, False),
        ("12", r"12\textsuperscript{a}", "Feixes Vivos e Drenos Verdes: estacas vivas, espécies indicadas.", False, False),
        ("13", r"13\textsuperscript{a}", "Hidrossemeadura: projeção hidráulica, sementes, fixadores, mulch.", False, False),
        ("14", r"14\textsuperscript{a}", "Biomantas e Geossintéticos Biodegradáveis: tipos, propriedades, vida útil.", False, False),
        ("15", r"15\textsuperscript{a}", "Enrocamento Vegetado: riprap com plantio intersticial, gabiões.", False, False),
        ("16", r"16\textsuperscript{a}", "Cordões Vegetativos e Fascinas: construção, espécies, aplicações.", False, False),
        ("17", r"17\textsuperscript{a}", "Gabião Vivo: estrutura, ancoragem, vegetação, manutenção.", False, False),
        ("18", r"18\textsuperscript{a}", r"Parede Krainer e Riprap: log-crib wall, enchimento, revegetação.", False, False),
        ("19", r"19\textsuperscript{a}", "Bioengenharia Fluvial Avançada: técnicas combinadas, restauração de margens.", False, False),
        ("20", r"20\textsuperscript{a}", r"Canaleta Verde (\textit{Vegetated Swale}): dimensionamento e monitoramento.", False, False),
        ("21", r"21\textsuperscript{a}", r"\textsf{PROJETO INTEGRADOR}: desenvolvimento, apresentação e avaliação.", True, False),
    ],
    "cronograma_note": r"\textbf{Estrutura geral:}\enspace Enc.\,01--06 → Pedologia e Erosão\enspace|\enspace Enc.\,07--08 → Hidráulica Aplicada\enspace|\enspace Enc.\,09--20 → Técnicas de Bioengenharia\enspace|\enspace Enc.\,21 → Projeto Integrador.",
    "metodologia": r"""A disciplina será desenvolvida ao longo de 21 encontros, com carga horária total de 60 horas (teoria + prática). O componente é de forte caráter aplicado, combinando aulas teóricas expositivas dialogadas com atividades práticas de campo e laboratório.

As aulas teóricas abordarão fundamentos de pedologia, processos erosivos, princípios de dimensionamento hidráulico e as bases conceituais de cada técnica de bioengenharia. Serão utilizados recursos audiovisuais, estudos de caso nacionais e internacionais e análise de normas técnicas.

As atividades práticas incluirão exercícios de cálculo e dimensionamento, visitas técnicas a obras de bioengenharia, atividades de campo para reconhecimento de processos erosivos e implantação de técnicas, além de sessões de modelagem 3D em laboratório de informática.""",
    "avaliacao": [
        r"1\textsuperscript{a}\,Avaliação (Teórica\,I\,--\,individual): formação dos solos, erosão, declividade, controle hídrico\,\dotfill\,\textbf{25\,\%}",
        r"2\textsuperscript{a}\,Avaliação (Prática\,--\,individual/dupla): dimensionamento de canal e terraço\,\dotfill\,\textbf{25\,\%}",
        r"3\textsuperscript{a}\,Avaliação (Teórica\,II\,--\,individual): técnicas de bioengenharia vegetal e estrutural\,\dotfill\,\textbf{25\,\%}",
        r"4\textsuperscript{a}\,Avaliação (Projeto Integrador\,--\,em grupo): projeto completo de estabilização\,\dotfill\,\textbf{25\,\%}",
    ],
    "significado": r"""O componente curricular \textit{Bioengenharia de Solos} é fundamental para a formação de profissionais capacitados a enfrentar um dos maiores desafios ambientais do Brasil: a erosão e a degradação dos solos. A disciplina fornece bases conceituais em pedologia e processos erosivos, articuladas ao domínio técnico de soluções de engenharia natural que combinam elementos vegetativos e estruturais para a estabilização de encostas, controle de erosão e restauração de áreas degradadas.

Ao integrar conhecimentos de geotecnia, ecologia e hidráulica, o(a) discente desenvolve competências para diagnosticar processos erosivos, selecionar técnicas adequadas ao contexto local e projetar intervenções sustentáveis de baixo custo e alto desempenho ambiental.""",
    "ref_basica": [
        r"USDA-NRCS. \textbf{Streambank and Shoreline Protection}. Engineering Field Handbook, Part 650, Chapter 16. Washington: USDA, 1996.",
        r"USDA-NRCS. \textbf{Streambank Soil Bioengineering}. National Engineering Handbook, Part 654. Washington: USDA, 2007.",
        r"GRAY, D.\,H.; SOTIR, R.\,B. \textbf{Biotechnical and soil bioengineering slope stabilization}: a practical guide for erosion control. New York: Wiley, 1996.",
        r"MORGAN, R.\,P.\,C. \textbf{Soil erosion and conservation}. 3.\,ed. Oxford: Blackwell, 2005.",
        r"GUERRA, A.\,J.\,T.; SILVA, A.\,S.; BOTELHO, R.\,G.\,M. (org.). \textbf{Erosão e conservação dos solos}: conceitos, temas e aplicações. 10.\,ed. Rio de Janeiro: Bertrand Brasil, 2014.",
    ],
    "ref_complementar": [
        r"EMBRAPA. \textbf{Sistema Brasileiro de Classificação de Solos}. 5.\,ed. Brasília: Embrapa, 2018.",
        r"LEPSCH, I.\,F. \textbf{Formação e conservação dos solos}. 2.\,ed. São Paulo: Oficina de Textos, 2010.",
        r"SCHIECHTL, H.\,M.; STERN, R. \textbf{Ground bioengineering techniques for slope protection and erosion control}. Oxford: Blackwell Science, 1996.",
        r"BERTONI, J.; LOMBARDI NETO, F. \textbf{Conservação do solo}. 10.\,ed. São Paulo: Ícone, 2017.",
        r"PRUSKI, F.\,F. \textbf{Conservação de solo e água}: práticas mecânicas para o controle da erosão hídrica. 2.\,ed. Viçosa: UFV, 2009.",
    ],
}

# ─── 2. BRANDING AGRO ───
disciplines["branding-agro"] = {
    "header_left": r"UEFS\,--\,Branding no Agronegócio",
    "department": "Departamento de Tecnologia\\,(DTEC)",
    "course": "Curso de Engenharia Agronômica",
    "title": "Gestão de Branding no Agronegócio",
    "subtitle": r"Plano de Ensino\,--\,2026.1",
    "has_logo": True,
    "info": [
        ("Carga Horária", "14 encontros"),
        ("Horário", "A definir"),
        ("Período", "2026.1"),
        ("Modalidade", "Presencial"),
        ("Docente", r"Prof.\,Dr.\,Luiz Diego Vidal Santos"),
        ("Contato", r"\href{mailto:ldvsantos@uefs.br}{ldvsantos@uefs.br}\enspace·\enspace\href{https://orcid.org/0000-0001-8659-8557}{ORCID: 0000-0001-8659-8557}"),
    ],
    "ementa": r"Transformações no mercado agropecuário e a necessidade de branding; conceito e evolução do branding; marca como ativo estratégico; branding para pequenos e médios produtores e agroindústrias; estratégia de diferenciação no agro; ideias diferenciadoras e suporte à diferenciação; benefícios como diferenciais de marca; estratégia de produtos e portfólio; público ideal e segmentação; branding B2B no agronegócio; posicionamento de marca; plataforma de marca (propósito, valores, personalidade, tom de voz, narrativa e mapa sensorial); cases de branding no agro brasileiro.",
    "objetivo_geral": r"Capacitar o(a) discente a compreender e aplicar os fundamentos do branding ao contexto do agronegócio brasileiro, desenvolvendo competências para criar, gerenciar e posicionar marcas de produtos e serviços agropecuários, com foco em diferenciação, valor percebido e construção de identidade.",
    "objetivos_especificos": [
        "Compreender as transformações do mercado agropecuário e a crescente importância da gestão de marcas.",
        r"Analisar o conceito de marca como ativo estratégico e os pilares do \textit{brand equity}.",
        "Desenvolver estratégias de diferenciação aplicadas ao agronegócio, identificando diferenciais competitivos reais.",
        "Construir plataformas de marca completas (propósito, valores, personalidade, tom de voz e narrativa).",
        "Aplicar técnicas de segmentação, definição de persona e mapeamento de jornada de compra.",
        r"Compreender as especificidades do branding B2B no agronegócio (\textit{ingredient branding}, reputação institucional).",
        "Analisar criticamente cases reais de branding no agro brasileiro e propor soluções de marca.",
    ],
    "competencias_cols": [
        ("Competências Estratégicas", [
            "Diagnosticar oportunidades de branding em empreendimentos agropecuários",
            "Construir plataformas de marca coerentes e diferenciadas",
            "Definir estratégias de posicionamento e comunicação para produtos do agro",
        ]),
        ("Competências Analíticas", [
            "Elaborar arquiteturas de portfólio e extensões de linha",
            "Analisar criticamente cases de branding no agronegócio",
            "Avaliar brand equity e valor percebido de marcas agro",
        ]),
        ("Competências Práticas", [
            "Construir personas e mapear jornadas de compra no agro",
            "Utilizar ferramentas (canvas, mapa perceptual) para posicionamento",
            "Desenvolver narrativas de marca autênticas e diferenciadoras",
        ]),
        ("Competências Comunicativas", [
            "Comunicar propostas de marca com clareza técnica e visão de mercado",
            "Apresentar e defender projetos de marca com fundamentação estratégica",
            "Articular identidade visual, tom de voz e narrativa de forma integrada",
        ]),
    ],
    "cronograma": [
        ("01", r"1\textsuperscript{a}", r"Transformações no Mercado Agro: \textit{commodity} vs.\ marca, nova demanda.", False, False),
        ("02", r"2\textsuperscript{a}", "Introdução ao Branding: conceito, evolução e pilares fundamentais.", False, False),
        ("03", r"3\textsuperscript{a}", r"Marca como Ativo Estratégico: \textit{brand equity}, valor percebido, proteção.", False, False),
        ("04", r"4\textsuperscript{a}", "Branding para PMEs do Agro: desafios específicos e caminhos práticos.", False, False),
        ("05", r"5\textsuperscript{a}", "Estratégia de Diferenciação: princípios, eixos e armadilhas.", False, False),
        ("06", r"6\textsuperscript{a}", r"Ideias Diferenciadoras no Agro: \textit{terroir}, método, história, certificação.", False, False),
        ("07", r"7\textsuperscript{a}", "Suporte e Reforço da Diferenciação: evidências tangíveis e intangíveis.", False, False),
        ("08", r"8\textsuperscript{a}", "Benefícios como Diferenciais: funcionais, emocionais, sociais, autoexpressão.", False, False),
        ("09", r"9\textsuperscript{a}", "Estratégia de Produtos e Portfólio: arquitetura de marca e extensão de linha.", False, False),
        ("10", r"10\textsuperscript{a}", "Público Ideal no Agro: persona, segmentação e jornada de compra.", False, False),
        ("11", r"11\textsuperscript{a}", r"Branding B2B no Agronegócio: \textit{ingredient branding}, confiança, reputação.", False, False),
        ("12", r"12\textsuperscript{a}", "Posicionamento de Marca: declaração, mapa perceptual, mensagens-chave.", False, False),
        ("13", r"13\textsuperscript{a}", "Plataforma de Marca: propósito, valores, personalidade, tom de voz, narrativa.", False, False),
        ("14", r"14\textsuperscript{a}", r"\textsf{CASES DE BRANDING}: análise crítica, padrões de sucesso, avaliação final.", True, False),
    ],
    "cronograma_note": r"\textbf{Estrutura geral:}\enspace Enc.\,01--04 → Fundamentos de Branding\enspace|\enspace Enc.\,05--08 → Diferenciação\enspace|\enspace Enc.\,09--13 → Estratégia e Plataforma\enspace|\enspace Enc.\,14 → Cases e Avaliação.",
    "metodologia": r"""A disciplina será desenvolvida ao longo de 14 encontros. Cada aula combinará exposição dialogada dos fundamentos conceituais com atividades práticas e exercícios de construção progressiva de marca.

As aulas teóricas utilizarão casos reais do agronegócio brasileiro e internacional como fio condutor, estimulando a análise crítica e a reflexão sobre estratégias de branding. Materiais complementares (artigos, vídeos, guias setoriais) serão disponibilizados em formato digital.

As atividades práticas incluirão exercícios individuais e em grupo de construção de marca, análise de concorrência, definição de persona, elaboração de plataforma de marca e simulações de posicionamento. Ao longo do semestre, cada aluno(a) desenvolverá progressivamente a marca de um produto ou empreendimento agropecuário.""",
    "avaliacao": [
        r"1\textsuperscript{a}\,Avaliação (Teórica\,--\,individual): fundamentos, marca como ativo, diferenciação\,\dotfill\,\textbf{25\,\%}",
        r"2\textsuperscript{a}\,Avaliação (Prática\,--\,individual): entrega parcial do projeto de marca\,\dotfill\,\textbf{25\,\%}",
        r"3\textsuperscript{a}\,Avaliação (Teórica\,--\,individual): B2B, portfólio, plataforma e cases\,\dotfill\,\textbf{25\,\%}",
        r"4\textsuperscript{a}\,Avaliação (Projeto Final\,--\,individual): plataforma de marca completa\,\dotfill\,\textbf{25\,\%}",
    ],
    "significado": r"""O componente curricular \textit{Gestão de Branding no Agronegócio} contribui para a formação de profissionais capacitados a agregar valor a produtos e serviços do setor agropecuário por meio da gestão estratégica de marcas. Em um mercado cada vez mais competitivo e orientado por percepção de valor, a capacidade de diferenciar, posicionar e comunicar marcas é competência essencial para engenheiros(as) agrônomos(as), técnicos(as) em agronegócio e gestores(as) rurais.

A disciplina prepara o(a) discente para atuar na interface entre produção e mercado, identificando oportunidades de branding em diferentes escalas (do produtor familiar a grandes agroindústrias), construindo narrativas de valor e contribuindo para a competitividade e sustentabilidade do agronegócio brasileiro.""",
    "ref_basica": [
        r"AAKER, D.\,A. \textbf{Construindo marcas fortes}. Porto Alegre: Bookman, 2007.",
        r"KELLER, K.\,L. \textbf{Gestão estratégica de marcas}. 3.\,ed. São Paulo: Pearson, 2006.",
        r"TROUT, J.; RIVKIN, S. \textbf{Diferenciar ou morrer}: sobrevivendo em nossa era de competição mortal. São Paulo: Futura, 2000.",
        r"RIES, A.; TROUT, J. \textbf{Posicionamento}: a batalha por sua mente. São Paulo: M.\,Books, 2009.",
        r"SEBRAE. \textbf{Marca no Agronegócio}: guia prático para produtores rurais. Brasília: SEBRAE, 2022.",
    ],
    "ref_complementar": [
        r"KOTLER, P.; KELLER, K.\,L. \textbf{Administração de marketing}. 15.\,ed. São Paulo: Pearson, 2018.",
        r"WHEELER, A. \textbf{Design de identidade da marca}: guia essencial para toda a equipe de gestão de marcas. 5.\,ed. Porto Alegre: Bookman, 2019.",
        r"CNA. \textbf{Panorama do Agronegócio Brasileiro}. Brasília: Confederação da Agricultura e Pecuária do Brasil.",
        r"EMBRAPA. \textbf{Publicações sobre inovação, tecnologia e mercado agropecuário}. Brasília: EMBRAPA.",
        r"MAPA. \textbf{Indicações geográficas e selos de qualidade}. Brasília: Ministério da Agricultura.",
    ],
}

# Helper: generate full .tex from a discipline dict
def generate_tex(d):
    parts = []
    
    # Preamble
    parts.append(PREAMBLE)
    parts.append(make_header_footer(d["header_left"]))
    
    # Begin document
    parts.append(r"\begin{document}")
    parts.append(r"\thispagestyle{empty}")
    parts.append("")
    
    # Cover
    parts.append(make_cover_uefs(
        d["department"], d["course"], d["title"], d["subtitle"],
        d["info"], d.get("has_logo", True)
    ))
    
    # Ementa
    parts.append(make_ementabox(d["ementa"]))
    
    # Objetivo Geral
    parts.append(r"\section*{Objetivo Geral}")
    parts.append(d["objetivo_geral"])
    
    # Objetivos Especificos
    parts.append(r"\section*{Objetivos Específicos}")
    parts.append(r"\begin{enumerate}")
    for obj in d["objetivos_especificos"]:
        parts.append(rf"\item {obj}")
    parts.append(r"\end{enumerate}")
    
    # Competências
    parts.append(r"\section*{Habilidades e Competências}")
    parts.append(r"\begin{multicols}{2}")
    for i, (title, items) in enumerate(d["competencias_cols"]):
        if i == 2:
            parts.append(r"\columnbreak")
        parts.append(rf"\subsection*{{{title}}}")
        parts.append(r"\begin{itemize}")
        for it in items:
            parts.append(rf"\item {it}")
        parts.append(r"\end{itemize}")
    parts.append(r"\end{multicols}")
    
    # Significado
    parts.append(r"\section*{Significado do Componente para a Formação Profissional}")
    parts.append(d["significado"])
    
    # Cronograma
    parts.append(r"\section*{Cronograma}")
    parts.append(make_cronograma_tabularx(d["cronograma"], d.get("cronograma_note", "")))
    
    # Metodologia
    parts.append(r"\section*{Metodologia}")
    parts.append(d["metodologia"])
    
    # Avaliação
    parts.append(make_avaliacao_box(d["avaliacao"]))
    
    # Bibliografia
    parts.append(make_bibliography(d["ref_basica"], d["ref_complementar"]))
    
    # Signature
    parts.append(make_signature())
    
    return "\n\n".join(parts)


# ═══════════════════════════════════════════════════════════
# Add remaining disciplines (abbreviated - same structure)
# ═══════════════════════════════════════════════════════════

# 3. ESTATÍSTICA APLICADA
disciplines["estatistica-aplicada"] = {
    "header_left": r"UEFS\,--\,Estatística Aplicada",
    "department": "Departamento de Tecnologia\\,(DTEC)",
    "course": "Curso de Engenharia Agronômica",
    "title": "Estatística Aplicada à Engenharia Agronômica",
    "subtitle": r"Plano de Ensino\,--\,2026.1",
    "has_logo": True,
    "info": [
        ("Carga Horária", "7 encontros"),
        ("Horário", "A definir"),
        ("Período", "2026.1"),
        ("Modalidade", "Presencial"),
        ("Docente", r"Prof.\,Dr.\,Luiz Diego Vidal Santos"),
        ("Contato", r"\href{mailto:ldvsantos@uefs.br}{ldvsantos@uefs.br}\enspace·\enspace\href{https://orcid.org/0000-0001-8659-8557}{ORCID: 0000-0001-8659-8557}"),
    ],
    "ementa": r"Estatística aplicada à Engenharia Agronômica; introdução ao R para ciências agrárias; testes paramétricos e não-paramétricos; ANOVA e pressupostos; regressão e correlação; análise multivariada; séries temporais ambientais.",
    "objetivo_geral": r"Capacitar o(a) discente a aplicar métodos estatísticos fundamentais e intermediários na análise de dados agronômicos, utilizando o ambiente R como ferramenta computacional, com ênfase na interpretação de resultados e na tomada de decisão em experimentação agrícola e estudos ambientais.",
    "objetivos_especificos": [
        "Compreender os fundamentos da estatística descritiva e inferencial aplicada às ciências agrárias.",
        "Utilizar o ambiente R para importação, manipulação, visualização e análise de dados agronômicos.",
        "Aplicar testes paramétricos (t-Student, Tukey) e não-paramétricos (Wilcoxon, Kruskal-Wallis, Mann-Whitney).",
        "Realizar análises de variância (ANOVA) com verificação de pressupostos e interpretação de resultados.",
        "Construir e interpretar modelos de regressão linear simples e múltipla, e coeficientes de correlação.",
        "Aplicar técnicas de análise multivariada (PCA, agrupamento e discriminante) a dados agrícolas.",
        "Analisar séries temporais de dados climáticos e agronômicos, incluindo decomposição e modelos ARIMA.",
    ],
    "competencias_cols": [
        ("Competências Metodológicas", [
            "Planejar coletas de dados e delineamentos experimentais com rigor estatístico",
            "Selecionar métodos estatísticos adequados a diferentes problemas agronômicos",
            "Verificar pressupostos e avaliar adequação de modelos",
        ]),
        ("Competências Computacionais", [
            "Executar análises estatísticas no R com autonomia",
            "Importar, manipular e visualizar dados com tidyverse",
            "Interpretar saídas de testes e modelos de forma crítica",
        ]),
        ("Competências Analíticas", [
            "Aplicar ANOVA, regressão e correlação a dados experimentais",
            "Utilizar PCA e análise de agrupamento para redução de dimensionalidade",
            "Decompor e modelar séries temporais ambientais",
        ]),
        ("Competências Comunicativas", [
            "Comunicar resultados estatísticos em relatórios técnicos e artigos",
            "Produzir visualizações claras e informativas",
            "Fundamentar decisões agronômicas com evidências estatísticas",
        ]),
    ],
    "cronograma": [
        ("01", r"1\textsuperscript{a}", "Estatística Aplicada: visão geral, importância, descritiva, medidas de posição e dispersão.", False, False),
        ("02", r"2\textsuperscript{a}", "Introdução ao R: instalação, RStudio, R base, tidyverse, primeiro experimento no R.", False, False),
        ("03", r"3\textsuperscript{a}", "Testes Paramétricos e Não-Paramétricos: t-Student, Tukey, Wilcoxon, Kruskal-Wallis.", False, False),
        ("04", r"4\textsuperscript{a}", r"ANOVA e Pressupostos: \textit{one-way}, \textit{two-way}, fatorial, medidas repetidas no R.", False, False),
        ("05", r"5\textsuperscript{a}", "Regressão e Correlação: linear simples/múltipla, Pearson, Spearman, diagnóstico de resíduos.", False, False),
        ("06", r"6\textsuperscript{a}", "Análise Multivariada: PCA, agrupamento (k-means, hierárquico), discriminante no R.", False, False),
        ("07", r"7\textsuperscript{a}", "Séries Temporais Ambientais: decomposição, ARIMA, sazonalidade de dados climáticos.", False, False),
    ],
    "cronograma_note": r"\textbf{Estrutura geral:}\enspace Enc.\,01--02 → Fundamentos e R\enspace|\enspace Enc.\,03--05 → Inferência e Modelagem\enspace|\enspace Enc.\,06--07 → Multivariada e Séries Temporais.",
    "metodologia": r"""A disciplina será desenvolvida ao longo de 7 encontros, combinando exposição teórica dos fundamentos estatísticos com sessões práticas no ambiente R. Cada encontro contemplará uma parte conceitual (pressupostos, formulação e interpretação) e uma parte aplicada (exercícios com datasets agronômicos reais no R).

Os materiais de apoio (scripts, datasets, tutoriais) serão disponibilizados em formato digital. As atividades práticas incluirão exercícios orientados de análise, interpretação de saídas do R e elaboração de relatórios com resultados estatísticos.""",
    "avaliacao": [
        r"1\textsuperscript{a}\,Avaliação (Teórica\,--\,individual): descritiva, testes de hipóteses, ANOVA\,\dotfill\,\textbf{40\,\%}",
        r"2\textsuperscript{a}\,Avaliação (Prática\,--\,individual): análise de dataset no R com relatório\,\dotfill\,\textbf{40\,\%}",
        r"Avaliação Contínua: participação nas atividades práticas\,\dotfill\,\textbf{20\,\%}",
    ],
    "significado": r"""O componente curricular \textit{Estatística Aplicada à Engenharia Agronômica} é essencial para a formação do(a) engenheiro(a) agrônomo(a), pois fornece ferramentas quantitativas indispensáveis ao planejamento experimental, à análise de resultados de campo e à tomada de decisão baseada em evidências. A capacidade de coletar, organizar, analisar e interpretar dados com rigor estatístico é competência transversal exigida em todas as áreas de atuação do profissional de agronomia.

A utilização do R como ferramenta computacional prepara o(a) discente para atuar com softwares de código aberto, amplamente adotados pela comunidade científica e técnica, promovendo autonomia, reprodutibilidade e alinhamento com as práticas da ciência aberta.""",
    "ref_basica": [
        r"BANZATTO, D.\,A.; KRONKA, S.\,N. \textbf{Experimentação agrícola}. 4.\,ed. Jaboticabal: FUNEP, 2006.",
        r"PIMENTEL-GOMES, F. \textbf{Curso de estatística experimental}. 15.\,ed. Piracicaba: FEALQ, 2009.",
        r"FERREIRA, D.\,F. \textbf{Estatística básica}. 2.\,ed. Lavras: UFLA, 2009.",
        r"ZAR, J.\,H. \textbf{Biostatistical analysis}. 5.\,ed. Upper Saddle River: Prentice Hall, 2010.",
        r"R CORE TEAM. \textbf{R: A language and environment for statistical computing}. Vienna: R Foundation, 2024.",
    ],
    "ref_complementar": [
        r"VIEIRA, S. \textbf{Análise de variância (ANOVA)}. São Paulo: Atlas, 2006.",
        r"FERREIRA, D.\,F. \textbf{Estatística multivariada}. 3.\,ed. Lavras: UFLA, 2018.",
        r"WICKHAM, H.; GROLEMUND, G. \textbf{R for Data Science}. 2.\,ed. Sebastopol: O'Reilly, 2023.",
        r"MORETTIN, P.\,A.; TOLOI, C.\,M.\,C. \textbf{Análise de séries temporais}. 3.\,ed. São Paulo: Blucher, 2018.",
        r"STORCK, L. \textit{et al.} \textbf{Experimentação vegetal}. 3.\,ed. Santa Maria: UFSM, 2011.",
    ],
}

# 4. EXTENSÃO RURAL
disciplines["extensao-rural"] = {
    "header_left": r"UEFS\,--\,Extensão Rural",
    "department": "Departamento de Tecnologia\\,(DTEC)",
    "course": "Curso de Engenharia Agronômica",
    "title": "Extensão Rural",
    "subtitle": r"Plano de Ensino\,--\,2026.1",
    "has_logo": True,
    "info": [
        ("Carga Horária", "12 encontros"),
        ("Horário", "A definir"),
        ("Período", "2026.1"),
        ("Modalidade", "Presencial"),
        ("Docente", r"Prof.\,Dr.\,Luiz Diego Vidal Santos"),
        ("Contato", r"\href{mailto:ldvsantos@uefs.br}{ldvsantos@uefs.br}\enspace·\enspace\href{https://orcid.org/0000-0001-8659-8557}{ORCID: 0000-0001-8659-8557}"),
    ],
    "ementa": r"Fundamentos teórico-conceituais e históricos da extensão rural; objetos de mediação (conhecimento cotidiano, ciência, técnica e tecnologia social); teoria pedagógica e extensão rural; institucionalização da ER no Brasil (difusionismo, FSR, participativo, agroecológico); PNATER e ATER digital; comunicação rural e metodologias participativas (DRP, andragogia); ATER pública e privada; agroecologia e transição agroecológica; segurança alimentar, certificação e indicações geográficas; elaboração de projetos de extensão rural; produção de material didático; avaliação participativa de impacto.",
    "objetivo_geral": r"Capacitar o(a) discente a compreender os fundamentos teóricos, históricos e metodológicos da extensão rural, desenvolvendo competências para planejar, executar e avaliar ações de assistência técnica e extensão rural (ATER) em diferentes contextos socioambientais e produtivos, com ênfase em comunicação dialógica, metodologias participativas e agroecologia.",
    "objetivos_especificos": [
        "Analisar a evolução histórica da extensão rural no Brasil, identificando os principais paradigmas.",
        "Compreender os objetos de mediação da extensão rural: conhecimento cotidiano, ciência, técnica e tecnologia social.",
        "Discutir as teorias pedagógicas aplicadas à extensão rural e suas implicações metodológicas.",
        "Aplicar ferramentas de comunicação rural e metodologias participativas (DRP, andragogia).",
        "Analisar os modelos institucionais de ATER pública e privada e os marcos legais (PNATER).",
        "Compreender os princípios da agroecologia e da transição agroecológica no contexto extensionista.",
        "Elaborar projetos de extensão rural, materiais didáticos e instrumentos de avaliação participativa.",
    ],
    "competencias_cols": [
        ("Competências Conceituais", [
            "Diagnosticar demandas de comunidades rurais com ferramentas participativas",
            "Planejar e conduzir ações de extensão com abordagem dialógica",
            "Articular saberes técnicos e tradicionais no desenvolvimento rural",
        ]),
        ("Competências Metodológicas", [
            "Aplicar DRP e metodologias participativas em diagnósticos territoriais",
            "Avaliar criticamente políticas públicas de extensão rural",
            "Compreender diferentes paradigmas (difusionismo, participativo, agroecológico)",
        ]),
        ("Competências de Projeto", [
            "Elaborar projetos de ATER com marco lógico, orçamento e indicadores",
            "Planejar processos de transição agroecológica com comunidades",
            "Articular conhecimento técnico-científico e saberes locais",
        ]),
        ("Competências Comunicativas", [
            "Produzir materiais didáticos e de divulgação para públicos rurais",
            "Comunicar resultados de intervenções de forma acessível",
            "Utilizar mídias digitais para ATER e comunicação rural",
        ]),
    ],
    "cronograma": [
        ("01", r"1\textsuperscript{a}", "Políticas de Extensão Rural: PNATER, princípios, diretrizes, andragogia.", False, False),
        ("02", r"2\textsuperscript{a}", "ATER Digital e Difusão Tecnológica: inovação, plataformas digitais, apps.", False, False),
        ("03", r"3\textsuperscript{a}", "Comunicação Rural e Metodologias Participativas: DRP, Paulo Freire.", False, False),
        ("04", r"4\textsuperscript{a}", "ATER Pública e Privada: Emater, cooperativas, ONGs, consultorias.", False, False),
        ("05", r"5\textsuperscript{a}", "Casos Práticos de Extensão Rural: experiências brasileiras, lições.", False, False),
        ("06", r"6\textsuperscript{a}", "Avaliação Participativa de Impacto: indicadores, cisternas, quintais produtivos.", False, False),
        ("07", r"7\textsuperscript{a}", "Objetos de Mediação: conhecimento cotidiano, ciência, técnica, tecnologia social.", False, False),
        ("08", r"8\textsuperscript{a}", "Teoria Pedagógica e Extensão: tradicional, nova, tecnicista, crítico-social.", False, False),
        ("09", r"9\textsuperscript{a}", "Agroecologia e Transição Agroecológica: princípios, PNAPO/PLANAPO.", False, False),
        ("10", r"10\textsuperscript{a}", "Segurança Alimentar e Certificação: SAN, soberania, SPG, IGs.", False, False),
        ("11", r"11\textsuperscript{a}", r"\textsf{PROJETO}: elaboração de projeto de extensão (diagnóstico, marco lógico).", True, False),
        ("12", r"12\textsuperscript{a}", r"\textsf{MATERIAL DIDÁTICO}: cartilhas, vídeos, mídias digitais para ATER.", True, False),
    ],
    "cronograma_note": r"\textbf{Estrutura geral:}\enspace Enc.\,01--06 → Políticas, Comunicação e Casos\enspace|\enspace Enc.\,07--10 → Fundamentos e Agroecologia\enspace|\enspace Enc.\,11--12 → Projetos e Materiais.",
    "metodologia": r"""A disciplina será desenvolvida ao longo de 12 encontros. As atividades combinarão exposição dialogada, leitura e discussão de textos, análise de casos práticos, dinâmicas de grupo, simulações de DRP (Diagnóstico Rural Participativo) e produção de materiais didáticos.

Serão utilizados textos acadêmicos, documentos de políticas públicas (PNATER), relatos de experiências extensionistas e materiais audiovisuais. A disciplina enfatiza a práxis extensionista, articulando teoria e prática por meio de metodologias ativas e participativas, coerentes com os princípios pedagógicos freireanos.""",
    "avaliacao": [
        r"1\textsuperscript{a}\,Avaliação (Teórica\,--\,individual): fundamentos, pedagogia, políticas\,\dotfill\,\textbf{25\,\%}",
        r"2\textsuperscript{a}\,Avaliação (Prática\,--\,em grupo): exercício de DRP simulado\,\dotfill\,\textbf{25\,\%}",
        r"3\textsuperscript{a}\,Avaliação (Projeto\,--\,individual/grupo): projeto de extensão rural completo\,\dotfill\,\textbf{25\,\%}",
        r"4\textsuperscript{a}\,Avaliação (Produção\,--\,individual): material didático para ATER\,\dotfill\,\textbf{25\,\%}",
    ],
    "significado": r"""O componente curricular \textit{Extensão Rural} é estruturante na formação do(a) engenheiro(a) agrônomo(a), por articular conhecimentos técnicos com habilidades de comunicação, mediação e planejamento voltados ao desenvolvimento rural sustentável. A extensão rural é o elo entre a pesquisa agropecuária e a realidade do campo, e o profissional que domina seus fundamentos está preparado para atuar como agente de transformação social, promovendo a adoção de tecnologias apropriadas, a valorização dos saberes locais e a construção coletiva de soluções.""",
    "ref_basica": [
        r"FREIRE, P. \textbf{Extensão ou comunicação?} 18.\,ed. Rio de Janeiro: Paz e Terra, 2017.",
        r"BRASIL. \textbf{Política Nacional de Assistência Técnica e Extensão Rural (PNATER)}. Brasília: MDA, 2010.",
        r"CAPORAL, F.\,R.; COSTABEBER, J.\,A. \textbf{Agroecologia e extensão rural}: contribuições para o desenvolvimento rural sustentável. Porto Alegre: EMATER/RS, 2004.",
        r"FONSECA, M.\,T.\,L. \textbf{A extensão rural no Brasil}: um projeto educativo para o capital. São Paulo: Loyola, 1985.",
        r"CALLOU, A.\,B.\,F. \textit{et al.} Extensão rural: estado da arte e novos desafios. \textit{Extensão Rural}, v.\,15, n.\,16, p.\,5--32, 2008.",
    ],
    "ref_complementar": [
        r"ALVES, R. \textbf{Filosofia da ciência}: introdução ao jogo e a suas regras. São Paulo: Loyola, 2000.",
        r"KUMMER, L. \textbf{Metodologia participativa no meio rural}: uma visão interdisciplinar. Salvador: GTNM-GTZ, 2007.",
        r"OLIVEIRA, M.\,M. As circunstâncias da criação da extensão rural no Brasil. \textit{Cadernos de Ciência \& Tecnologia}, v.\,16, n.\,2, p.\,97--134, 1999.",
        r"CHAMBERS, R. \textbf{Rural development}: putting the last first. London: Longman, 1983.",
        r"GONÇALVES, L.\,C. \textbf{Extensão rural e conexões}. Lavras: UFLA, 2020.",
    ],
}

# 5. GEOTECNOLOGIAS E SIG (UNIVASF)
disciplines["geotecnologias-sig"] = {
    "header_left": r"UNIVASF\,--\,Geotecnologias e SIG",
    "department": "Colegiado de Geografia",
    "course": "",
    "title": "Geotecnologias e SIG",
    "subtitle": r"Plano de Ensino\,--\,2026.1",
    "has_logo": False,
    "info": [
        ("Carga Horária", "11 encontros"),
        ("Horário", "A definir"),
        ("Período", "2026.1"),
        ("Modalidade", "Presencial"),
        ("Docente", r"Prof.\,Dr.\,Luiz Diego Vidal Santos"),
        ("Contato", r"\href{mailto:ldvsantos@uefs.br}{ldvsantos@uefs.br}\enspace·\enspace\href{https://orcid.org/0000-0001-8659-8557}{ORCID: 0000-0001-8659-8557}"),
    ],
    "ementa": r"Fundamentos do geoprocessamento e análise espacial; estruturas de dados; análise de incerteza e acurácia; geotecnologias aplicadas a recursos hídricos e seca; SIG na exploração de recursos minerais; intemperismo, erosão e formação de solos; degradação, desertificação e mudanças climáticas; recursos hídricos e gestão por bacia hidrográfica; monitoramento hidrológico; impactos ambientais da mineração; sensoriamento remoto e mudanças de cobertura vegetal; inteligência artificial e qualidade da pesquisa ambiental (princípios FAIR).",
    "objetivo_geral": r"Capacitar o(a) discente a aplicar geotecnologias (SIG, sensoriamento remoto, modelagem espacial e inteligência artificial) na análise, monitoramento e gestão de recursos naturais, com ênfase em rigor metodológico, validação de resultados e suporte à tomada de decisão.",
    "objetivos_especificos": [
        "Dominar os fundamentos do geoprocessamento, incluindo estruturas de dados vetoriais e matriciais.",
        "Avaliar incerteza e acurácia em produtos de classificação (matriz de confusão, Kappa, validação espacial).",
        "Aplicar geotecnologias ao monitoramento de recursos hídricos, seca e evapotranspiração.",
        "Utilizar análise multicriterial (AHP, Fuzzy) em SIG para exploração mineral e tomada de decisão.",
        "Analisar processos de intemperismo, erosão, formação e degradação de solos com geotecnologias.",
        "Delimitar e caracterizar bacias hidrográficas com análise morfométrica.",
        "Aplicar sensoriamento remoto na detecção de mudanças de cobertura vegetal.",
        "Utilizar aprendizado de máquina com validação espacialmente robusta e princípios FAIR.",
    ],
    "competencias_cols": [
        ("Competências Técnicas", [
            "Dominar geoprocessamento e análise espacial em plataformas livres (QGIS, GEE)",
            "Avaliar qualidade e incerteza de produtos cartográficos",
            "Integrar múltiplas fontes de dados espaciais (satelitais, censitários, hidrológicos)",
        ]),
        ("Competências Analíticas", [
            "Realizar análises multicriteriais e detecção de mudanças",
            "Aplicar métodos de ML com validação espacialmente robusta",
            "Interpretar indicadores ambientais e séries temporais",
        ]),
        ("Competências Ambientais", [
            "Monitorar recursos hídricos e processos de degradação",
            "Analisar impactos da mineração com geoprocessamento",
            "Avaliar mudanças de cobertura vegetal e métricas de paisagem",
        ]),
        ("Competências Profissionais", [
            "Elaborar produtos técnicos reprodutíveis (mapas, relatórios, scripts)",
            "Aplicar princípios FAIR e ciência aberta na pesquisa ambiental",
            "Subsidiar políticas públicas de gestão territorial",
        ]),
    ],
    "cronograma": [
        ("01", r"1\textsuperscript{a}", "Incerteza e Acurácia: matriz de confusão, Kappa, validação espacial.", False, False),
        ("02", r"2\textsuperscript{a}", "Fundamentos do Geoprocessamento: estruturas vetorial/matricial, operações espaciais.", False, False),
        ("03", r"3\textsuperscript{a}", "Geotecnologias e Recursos Hídricos: evapotranspiração, índices de seca, SR hidrológico.", False, False),
        ("04", r"4\textsuperscript{a}", "SIG na Exploração Mineral: análise multicriterial, AHP, tomada de decisão.", False, False),
        ("05", r"5\textsuperscript{a}", "Intemperismo, Erosão e Solos: processos pedogenéticos, RUSLE, SiBCS.", False, False),
        ("06", r"6\textsuperscript{a}", "Degradação, Desertificação e Clima: indicadores espaciais, monitoramento.", False, False),
        ("07", r"7\textsuperscript{a}", "Recursos Hídricos e Bacia Hidrográfica: delimitação, morfometria, Lei 9.433/97.", False, False),
        ("08", r"8\textsuperscript{a}", "Monitoramento Hidrológico: telemetria IoT, altimetria radar, modelos.", False, False),
        ("09", r"9\textsuperscript{a}", "Geoprocessamento na Mineração: DInSAR, NDVI, licenciamento, auditoria.", False, False),
        ("10", r"10\textsuperscript{a}", "SR e Cobertura Vegetal: NDVI/EVI, classificadores RF/SVM/U-Net, BFAST.", False, False),
        ("11", r"11\textsuperscript{a}", r"\textsf{IA e Qualidade}: ML, SHAP/LIME, princípios FAIR, Green AI, ética.", True, False),
    ],
    "cronograma_note": r"\textbf{Estrutura geral:}\enspace Enc.\,01--02 → Fundamentos\enspace|\enspace Enc.\,03--06 → Recursos Naturais e Solos\enspace|\enspace Enc.\,07--09 → Hidrologia e Mineração\enspace|\enspace Enc.\,10--11 → SR, IA e Ciência Aberta.",
    "metodologia": r"""A disciplina será desenvolvida ao longo de 11 encontros. As atividades combinarão exposição dialogada dos fundamentos teóricos com sessões práticas em ambiente computacional (QGIS, Google Earth Engine e R).

Cada encontro articulará uma dimensão conceitual (fundamentos, pressupostos e critérios) com uma dimensão aplicada (exercícios com dados reais, produção de mapas e relatórios). A disciplina enfatiza o rigor metodológico, a reprodutibilidade dos procedimentos e a interpretação crítica dos resultados.""",
    "avaliacao": [
        r"1\textsuperscript{a}\,Avaliação (Teórica\,I\,--\,individual): fundamentos, incerteza, recursos hídricos, solos\,\dotfill\,\textbf{25\,\%}",
        r"2\textsuperscript{a}\,Avaliação (Prática\,--\,individual/dupla): mapa temático + relatório técnico\,\dotfill\,\textbf{25\,\%}",
        r"3\textsuperscript{a}\,Avaliação (Teórica\,II\,--\,individual): bacias, SR, detecção de mudanças, IA\,\dotfill\,\textbf{25\,\%}",
        r"4\textsuperscript{a}\,Avaliação (Projeto Final\,--\,individual/grupo): análise integrada reprodutível\,\dotfill\,\textbf{25\,\%}",
    ],
    "significado": r"""O componente curricular \textit{Geotecnologias e SIG} é estruturante para a formação de profissionais de Geografia e áreas afins, por fornecer competências em análise espacial, sensoriamento remoto e modelagem ambiental indispensáveis ao diagnóstico, monitoramento e gestão do território. O domínio de geotecnologias é exigência crescente em licenciamentos, auditorias ambientais, planejamento urbano e regional, gestão de recursos hídricos e minerais.

A ênfase em plataformas livres (QGIS, Google Earth Engine), inteligência artificial aplicada e princípios de ciência aberta (FAIR, reprodutibilidade) prepara o(a) egresso(a) para atuar em órgãos públicos, empresas de consultoria, institutos de pesquisa e organizações ambientais.""",
    "ref_basica": [
        r"CÂMARA, G. \textit{et al.} \textbf{Anatomia de Sistemas de Informação Geográfica}. São José dos Campos: INPE, 2004.",
        r"NOVO, E.\,M.\,L.\,M. \textbf{Sensoriamento remoto}: princípios e aplicações. 4.\,ed. São Paulo: Blucher, 2008.",
        r"ROSA, R.; BRITO, J.\,L.\,S. \textbf{Introdução ao geoprocessamento}. Uberlândia: UFU, 1996.",
        r"TUCCI, C.\,E.\,M. \textbf{Hidrologia}: ciência e aplicação. 4.\,ed. Porto Alegre: ABRH/UFRGS, 2002.",
        r"ALLEN, R.\,G. \textit{et al.} \textbf{Crop evapotranspiration}. FAO Irrigation and Drainage Paper 56. Rome: FAO, 1998.",
    ],
    "ref_complementar": [
        r"EMBRAPA. \textbf{Sistema Brasileiro de Classificação de Solos}. 5.\,ed. Brasília: Embrapa, 2018.",
        r"BRASIL. \textbf{Lei nº 9.433, de 8 de janeiro de 1997}. Política Nacional de Recursos Hídricos. Brasília, 1997.",
        r"REICHSTEIN, M. \textit{et al.} Deep learning and process understanding for data-driven Earth system science. \textit{Nature}, v.\,566, p.\,195--204, 2019.",
        r"WILKINSON, M.\,D. \textit{et al.} The FAIR Guiding Principles. \textit{Scientific Data}, v.\,3, 160018, 2016.",
        r"SCHWARTZ, R. \textit{et al.} Green AI. \textit{Communications of the ACM}, v.\,63, n.\,12, p.\,54--63, 2020.",
    ],
}

# 6. GEOTÊXTEIS E NBS (POSDOC UEFS)
disciplines["geotexteis-nbs"] = {
    "header_left": r"UEFS\,--\,Geotêxteis e NbS",
    "department": "Pós-Doutorado em Geotecnia Ambiental",
    "course": "",
    "title": r"Geotêxteis e Soluções baseadas na Natureza",
    "subtitle": r"Tópicos Especiais\,--\,Seminários POSDOC",
    "has_logo": True,
    "info": [
        ("Carga Horária", "6 encontros intensivos"),
        ("Horário", "A definir"),
        ("Período", "2026"),
        ("Modalidade", "Presencial"),
        ("Docente", r"Prof.\,Dr.\,Luiz Diego Vidal Santos"),
        ("Contato", r"\href{mailto:ldvsantos@uefs.br}{ldvsantos@uefs.br}\enspace·\enspace\href{https://orcid.org/0000-0001-8659-8557}{ORCID: 0000-0001-8659-8557}"),
    ],
    "ementa": r"Fundamentos e aplicações estratégicas de geotêxteis; classificação e propriedades mecânicas; especificações de projeto; estudos de caso em seleção e dimensionamento; implementação, monitoramento e avaliação de desempenho; modelagem de vida útil de biotêxteis sob diferentes climas.",
    "objetivo_geral": r"Capacitar o(a) discente a compreender os fundamentos, propriedades e aplicações de geotêxteis convencionais e biodegradáveis, desenvolvendo competências para selecionar, dimensionar, implementar e monitorar soluções geotécnicas baseadas na natureza (NbS) para estabilização de taludes e controle de erosão.",
    "objetivos_especificos": [
        "Compreender os fundamentos teóricos e as aplicações estratégicas de geotêxteis.",
        "Classificar geotêxteis segundo suas propriedades mecânicas, hidráulicas e de durabilidade.",
        "Especificar geotêxteis para projetos de controle de erosão, drenagem, separação e reforço.",
        "Analisar estudos de caso em seleção e dimensionamento de geotêxteis para cenários reais.",
        "Planejar e avaliar a implementação em campo, incluindo monitoramento e avaliação de desempenho.",
        "Modelar a vida útil de biotêxteis sob diferentes regimes climáticos e condições ambientais.",
    ],
    "competencias_cols": [
        ("Competências Técnicas", [
            "Selecionar e especificar geotêxteis adequados a cada aplicação geotécnica",
            "Dimensionar soluções integradas de proteção e estabilização",
            "Interpretar normas técnicas (ABNT, ISO, ASTM) para geossintéticos",
        ]),
        ("Competências de Campo", [
            "Conduzir ensaios de caracterização e monitoramento de desempenho",
            "Avaliar vida útil e degradação de biotêxteis em diferentes contextos",
            "Planejar técnicas de instalação e controle de qualidade",
        ]),
        ("Competências Analíticas", [
            "Modelar degradação sob diferentes regimes climáticos",
            "Analisar fatores: UV, temperatura, umidade, microrganismos",
            "Avaliar custo-benefício de soluções convencionais vs.\\ naturais",
        ]),
        ("Competências de Projeto", [
            "Elaborar memoriais descritivos e relatórios técnicos",
            "Integrar geotêxteis em soluções baseadas na natureza (NbS)",
            "Propor soluções alinhadas aos ODS e engenharia ecológica",
        ]),
    ],
    "cronograma": [
        ("01", r"1\textsuperscript{o}", "Seminário POSDOC: visão geral, fundamentos e aplicações estratégicas de geotêxteis.", False, False),
        ("02", r"2\textsuperscript{o}", "Tipologia de Geotêxteis: classificação, propriedades mecânicas e hidráulicas.", False, False),
        ("03", r"3\textsuperscript{o}", "Geotêxteis: tipos, usos práticos, especificações de projeto e normas técnicas.", False, False),
        ("04", r"4\textsuperscript{o}", "Projeto Prático I: seleção e dimensionamento, memorial descritivo.", False, False),
        ("05", r"5\textsuperscript{o}", "Projeto Prático II: implementação, monitoramento e avaliação de desempenho.", False, False),
        ("06", r"6\textsuperscript{o}", r"\textsf{VIDA ÚTIL}: modelagem de degradação de biotêxteis sob diferentes climas.", True, False),
    ],
    "cronograma_note": r"\textbf{Estrutura:}\enspace Enc.\,01--03 → Fundamentos e Tipologia\enspace|\enspace Enc.\,04--05 → Projetos Práticos\enspace|\enspace Enc.\,06 → Modelagem de Vida Útil.",
    "metodologia": r"""A disciplina será desenvolvida ao longo de 6 encontros intensivos, com forte caráter prático e orientado a projetos. As atividades combinarão exposição teórica dos fundamentos com análise de estudos de caso, exercícios de dimensionamento e atividades aplicadas de campo.

Os encontros incluirão revisão bibliográfica, análise de normas técnicas, exercícios projetuais, discussão de resultados experimentais e modelagem computacional de degradação de biotêxteis.""",
    "avaliacao": [
        r"1\textsuperscript{a}\,Avaliação (Teórica/Seminário\,--\,individual): fundamentos, classificação, propriedades\,\dotfill\,\textbf{50\,\%}",
        r"2\textsuperscript{a}\,Avaliação (Projeto Prático\,--\,individual/dupla): seleção, dimensionamento, relatório\,\dotfill\,\textbf{50\,\%}",
    ],
    "significado": r"""O componente curricular \textit{Geotêxteis e Soluções baseadas na Natureza} é relevante para profissionais de engenharia geotécnica, ambiental e de conservação de solos. Os geotêxteis são elementos fundamentais em obras de contenção, drenagem, filtragem e proteção de superfícies, e o domínio de suas propriedades, critérios de seleção e procedimentos de implementação é competência cada vez mais exigida em projetos de infraestrutura sustentável.

A ênfase em biotêxteis e soluções baseadas na natureza (NbS) reflete a tendência global de integração de materiais naturais e engenharia ecológica, promovendo soluções de menor impacto ambiental e maior alinhamento com os Objetivos de Desenvolvimento Sustentável (ODS).""",
    "ref_basica": [
        r"KOERNER, R.\,M. \textbf{Designing with geosynthetics}. 6.\,ed. Upper Saddle River: Prentice Hall, 2012.",
        r"INGOLD, T.\,S. \textbf{Geotextiles and geomembranes handbook}. Oxford: Elsevier, 1994.",
        r"VERTEMATTI, J.\,C. (coord.). \textbf{Manual brasileiro de geossintéticos}. 2.\,ed. São Paulo: Blucher, 2015.",
        r"SCHIECHTL, H.\,M.; STERN, R. \textbf{Ground bioengineering techniques}. Oxford: Blackwell Science, 1996.",
        r"JOHN, N.\,W.\,M. \textbf{Geotextiles}. Glasgow: Blackie and Son, 1987.",
    ],
    "ref_complementar": [
        r"ABNT. \textbf{NBR ISO 10318}: Geossintéticos --- termos e definições. Rio de Janeiro: ABNT, 2013.",
        r"PALMEIRA, E.\,M. \textbf{Geossintéticos em geotecnia e meio ambiente}. São Paulo: Oficina de Textos, 2018.",
        r"MITCHELL, D.\,J.; BARR, C. The use of biotextiles for erosion control. In: \textbf{Eco- and Ground Bio-Engineering}. Dordrecht: Springer, 2007. p.\,243--256.",
        r"VISHNUDAS, S. \textit{et al.} Coir geotextile field studies. \textit{Geotextiles and Geomembranes}, v.\,24, n.\,5, p.\,316--325, 2006.",
        r"SMETS, T. \textit{et al.} Physical soil quality on biotextile efficiency. \textit{Geomorphology}, v.\,153--154, p.\,142--150, 2012.",
    ],
}

# 7. PROPRIEDADE INTELECTUAL
disciplines["propriedade-intelectual"] = {
    "header_left": r"UEFS\,--\,PI e Inovação",
    "department": "Departamento de Tecnologia\\,(DTEC)",
    "course": "Curso de Engenharia Agronômica",
    "title": "Propriedade Intelectual e Inovação",
    "subtitle": r"Plano de Ensino\,--\,2026.1",
    "has_logo": True,
    "info": [
        ("Carga Horária", "10 encontros"),
        ("Horário", "A definir"),
        ("Período", "2026.1"),
        ("Modalidade", "Presencial"),
        ("Docente", r"Prof.\,Dr.\,Luiz Diego Vidal Santos"),
        ("Contato", r"\href{mailto:ldvsantos@uefs.br}{ldvsantos@uefs.br}\enspace·\enspace\href{https://orcid.org/0000-0001-8659-8557}{ORCID: 0000-0001-8659-8557}"),
    ],
    "ementa": r"Gestão da inovação tecnológica na agropecuária; PI como ativo estratégico no agronegócio; empreendedorismo tecnológico agrícola; políticas de inovação; gestão de projetos de inovação; valoração de ativos de PI; transferência de tecnologia; gestão estratégica de PI em empresas rurais; \textit{spin-offs} acadêmicas; PI na agricultura digital.",
    "objetivo_geral": r"Capacitar o(a) discente a compreender os fundamentos da propriedade intelectual e da gestão da inovação no contexto agropecuário, desenvolvendo competências para proteger, valorar e transferir ativos intangíveis, promover o empreendedorismo tecnológico e gerir projetos de inovação no setor agrícola.",
    "objetivos_especificos": [
        "Compreender os fundamentos da gestão da inovação tecnológica aplicada ao setor agropecuário.",
        "Analisar a PI como ativo estratégico: patentes, marcas, cultivares, IGs e segredos industriais.",
        "Desenvolver competências em empreendedorismo tecnológico agrícola e criação de negócios de base tecnológica.",
        "Conhecer as políticas públicas de inovação e instrumentos de fomento para o setor agrícola.",
        "Aplicar técnicas de gestão de projetos de inovação com foco em PI.",
        "Utilizar métodos de valoração de ativos intangíveis no contexto agropecuário.",
        r"Compreender processos de transferência de tecnologia e modelos de \textit{spin-offs} acadêmicas.",
        "Analisar a proteção de PI na agricultura digital (Agricultura 4.0).",
    ],
    "competencias_cols": [
        ("Competências Conceituais", [
            "Identificar ativos de PI em empreendimentos agropecuários",
            "Definir estratégias de proteção adequadas a cada modalidade",
            "Compreender o ambiente regulatório (INPI, Lei de Cultivares, Lei de PI)",
        ]),
        ("Competências de Gestão", [
            "Elaborar projetos de inovação com componentes de PI",
            "Gerir portfólios de PI em empresas rurais",
            "Planejar processos de transferência de tecnologia",
        ]),
        ("Competências Analíticas", [
            "Avaliar economicamente ativos intangíveis",
            "Realizar buscas de anterioridade em bases de patentes",
            "Analisar cases de inovação no agronegócio",
        ]),
        ("Competências Empreendedoras", [
            r"Articular inovação, empreendedorismo e PI",
            r"Compreender ecossistemas de \textit{AgTechs} e incubadoras",
            "Propor modelos de negócio baseados em PI agrícola",
        ]),
    ],
    "cronograma": [
        ("01", r"1\textsuperscript{a}", "Gestão da Inovação Tecnológica na Agropecuária: fundamentos, tipos, sistemas.", False, False),
        ("02", r"2\textsuperscript{a}", "PI como Ativo Estratégico: patentes, marcas, cultivares, IGs, segredos industriais.", False, False),
        ("03", r"3\textsuperscript{a}", r"Empreendedorismo Tecnológico Agrícola: startups, \textit{AgTechs}, inovação.", False, False),
        ("04", r"4\textsuperscript{a}", r"Políticas de Inovação: SNPA, Marco Legal de CT\&I, FNDCT, incentivos.", False, False),
        ("05", r"5\textsuperscript{a}", "Gestão de Projetos de Inovação: escopo, riscos, canvas, roadmap.", False, False),
        ("06", r"6\textsuperscript{a}", "Valoração de Ativos de PI: métodos de custo, mercado, renda, opções reais.", False, False),
        ("07", r"7\textsuperscript{a}", "Transferência de Tecnologia: licenciamento, cessão, cooperação, NIT, ICT.", False, False),
        ("08", r"8\textsuperscript{a}", "Gestão Estratégica de PI em Empresas Rurais: portfólio, monitoramento, defesa.", False, False),
        ("09", r"9\textsuperscript{a}", r"\textit{Spin-offs} Acadêmicas: empreendedorismo universitário, incubadoras, aceleradoras.", False, False),
        ("10", r"10\textsuperscript{a}", r"\textsf{PI NA AGRICULTURA DIGITAL}: dados, IoT, algoritmos, regulação.", True, False),
    ],
    "cronograma_note": r"\textbf{Estrutura geral:}\enspace Enc.\,01--04 → Fundamentos, PI e Políticas\enspace|\enspace Enc.\,05--07 → Gestão, Valoração e Transferência\enspace|\enspace Enc.\,08--10 → Estratégia, Spin-offs e Agricultura Digital.",
    "metodologia": r"""A disciplina será desenvolvida ao longo de 10 encontros. As atividades combinarão exposição dialogada, estudos de caso do agronegócio, análise de documentos de patentes e cultivares, simulações de processos de registro e exercícios de valoração de ativos.

Os materiais incluirão legislação pertinente (Lei de PI, Lei de Cultivares, Marco Legal de CT\&I), bases de patentes (INPI, WIPO), cases de empresas do agro e materiais audiovisuais. A disciplina enfatiza a aplicação prática, com exercícios de busca de anterioridade, valoração de ativos e elaboração de planos de negócio com PI.""",
    "avaliacao": [
        r"1\textsuperscript{a}\,Avaliação (Teórica\,--\,individual): fundamentos de PI, inovação, empreendedorismo\,\dotfill\,\textbf{33\,\%}",
        r"2\textsuperscript{a}\,Avaliação (Prática\,--\,individual/grupo): busca de anterioridade, análise de patente\,\dotfill\,\textbf{33\,\%}",
        r"3\textsuperscript{a}\,Avaliação (Projeto Final\,--\,individual/grupo): plano de negócio com PI\,\dotfill\,\textbf{34\,\%}",
    ],
    "significado": r"""O componente curricular \textit{Propriedade Intelectual e Inovação} é relevante para a formação do(a) engenheiro(a) agrônomo(a), por abordar a dimensão estratégica da proteção do conhecimento e da inovação tecnológica. Em um cenário de crescente intensificação tecnológica (Agricultura 4.0, biotecnologia, sensoriamento remoto), a capacidade de identificar, proteger, valorar e transferir ativos intangíveis é competência diferenciadora para profissionais em pesquisa, desenvolvimento, consultoria e gestão de empreendimentos rurais.""",
    "ref_basica": [
        r"JUNGMANN, D.\,M.; BONETTI, E.\,A. \textbf{A caminho da inovação}: proteção e negócios com bens de PI --- guia para o empresário. Brasília: IEL, 2010.",
        r"BARBOSA, D.\,B. \textbf{Uma introdução à propriedade intelectual}. 2.\,ed. Rio de Janeiro: Lumen Juris, 2003.",
        r"BRASIL. \textbf{Lei nº 9.279, de 14 de maio de 1996} (Lei da Propriedade Industrial). Brasília, 1996.",
        r"BRASIL. \textbf{Lei nº 9.456, de 25 de abril de 1997} (Lei de Proteção de Cultivares). Brasília, 1997.",
        r"TIDD, J.; BESSANT, J. \textbf{Gestão da inovação}. 5.\,ed. Porto Alegre: Bookman, 2015.",
    ],
    "ref_complementar": [
        r"BRASIL. \textbf{Lei nº 13.243, de 11 de janeiro de 2016} (Marco Legal de CT\&I). Brasília, 2016.",
        r"INPI. \textbf{Manual de patentes}. Rio de Janeiro: INPI, 2023.",
        r"VIEIRA, A.\,C.\,P.; BUAINAIN, A.\,M. Aplicação da PI no agronegócio. In: \textbf{PI e Inovação no Agronegócio}. Brasília: MAPA, 2015.",
        r"EMBRAPA. \textbf{Política de inovação da Embrapa}. Brasília: Embrapa, 2018.",
        r"OECD/FAO. \textbf{OECD-FAO Agricultural Outlook}. Paris: OECD Publishing, 2024.",
    ],
}

# 8. SOCIOLOGIA RURAL
disciplines["sociologia-rural"] = {
    "header_left": r"UEFS\,--\,Sociologia Rural",
    "department": "Departamento de Tecnologia\\,(DTEC)",
    "course": "Curso de Engenharia Agronômica",
    "title": "Sociologia Rural",
    "subtitle": r"Plano de Ensino\,--\,2026.1",
    "has_logo": True,
    "info": [
        ("Carga Horária", "10 encontros"),
        ("Horário", "A definir"),
        ("Período", "2026.1"),
        ("Modalidade", "Presencial"),
        ("Docente", r"Prof.\,Dr.\,Luiz Diego Vidal Santos"),
        ("Contato", r"\href{mailto:ldvsantos@uefs.br}{ldvsantos@uefs.br}\enspace·\enspace\href{https://orcid.org/0000-0001-8659-8557}{ORCID: 0000-0001-8659-8557}"),
    ],
    "ementa": r"Sociologia rural no Brasil: atores, temas e objetos de estudo; organização social da agricultura familiar; políticas públicas para o meio rural; novas ruralidades e multifuncionalidade da agricultura; paradigmas do desenvolvimento rural; capitalismo no campo e modernização conservadora; movimentos sociais do campo e reforma agrária; comunicação de massa e publicidade rural; direitos humanos no campo; diversidade étnico-racial e povos tradicionais.",
    "objetivo_geral": r"Capacitar o(a) discente a compreender criticamente a estrutura social agrária brasileira, os processos de transformação do meio rural e as relações entre atores sociais, políticas públicas e dinâmicas produtivas, desenvolvendo visão humanística e comprometida com o desenvolvimento rural sustentável.",
    "objetivos_especificos": [
        "Compreender os fundamentos teóricos da sociologia rural e suas vertentes no contexto brasileiro.",
        "Analisar a organização social da agricultura familiar: lógicas, pluriatividade e reprodução social.",
        "Discutir as políticas públicas para o meio rural (PRONAF, PAA, PNAE) e seus impactos.",
        "Compreender as novas ruralidades, multifuncionalidade e processos de revalorização do campo.",
        "Analisar os paradigmas do desenvolvimento rural e suas implicações para a sustentabilidade.",
        "Discutir o capitalismo no campo, a modernização conservadora e os conflitos fundiários.",
        "Compreender os movimentos sociais do campo, a reforma agrária e os assentamentos rurais.",
        "Analisar a comunicação de massa, publicidade rural e questões de direitos humanos e diversidade.",
    ],
    "competencias_cols": [
        ("Competências Conceituais", [
            "Analisar criticamente a realidade social do meio rural brasileiro",
            "Reconhecer a diversidade de atores e lógicas produtivas no campo",
            "Compreender processos históricos de transformação do espaço rural",
        ]),
        ("Competências Analíticas", [
            "Avaliar políticas públicas e seus impactos sobre comunidades rurais",
            "Identificar conflitos fundiários e questões de justiça social",
            "Analisar representações do rural na mídia e comunicação de massa",
        ]),
        ("Competências Humanísticas", [
            "Debater direitos humanos no campo com embasamento teórico",
            "Reconhecer e valorizar a diversidade étnico-racial e povos tradicionais",
            "Desenvolver postura ética e inclusiva na atuação profissional",
        ]),
        ("Competências Profissionais", [
            "Articular saberes sociológicos na prática do(a) engenheiro(a) agrônomo(a)",
            "Dialogar com diferentes atores sociais do campo",
            "Contribuir para processos de desenvolvimento rural sustentável",
        ]),
    ],
    "cronograma": [
        ("01", r"1\textsuperscript{a}", "Sociologia Rural no Brasil: atores, temas, objetos e vertentes teóricas.", False, False),
        ("02", r"2\textsuperscript{a}", "Organização Social da Agricultura Familiar: lógicas, pluriatividade, estratégias.", False, False),
        ("03", r"3\textsuperscript{a}", "Políticas Públicas para o Meio Rural: PRONAF, PAA, PNAE, política fundiária.", False, False),
        ("04", r"4\textsuperscript{a}", "Novas Ruralidades: multifuncionalidade, turismo rural, agroecologia, patrimônio.", False, False),
        ("05", r"5\textsuperscript{a}", "Desenvolvimento Rural: paradigmas, desenvolvimento local, sustentabilidade.", False, False),
        ("06", r"6\textsuperscript{a}", "Capitalismo no Campo: modernização conservadora, agronegócio, conflitos.", False, False),
        ("07", r"7\textsuperscript{a}", "Movimentos Sociais do Campo: MST, Via Campesina, sindicalismo, lutas por terra.", False, False),
        ("08", r"8\textsuperscript{a}", "Comunicação de Massa e Publicidade Rural: rádio, TV, redes sociais, influência.", False, False),
        ("09", r"9\textsuperscript{a}", "Direitos Humanos no Campo: trabalho escravo, violência, acesso à terra.", False, False),
        ("10", r"10\textsuperscript{a}", r"\textsf{DIVERSIDADE}: povos indígenas, quilombolas, comunidades tradicionais.", True, False),
    ],
    "cronograma_note": r"\textbf{Estrutura geral:}\enspace Enc.\,01--05 → Fundamentos, Agricultura Familiar e Desenvolvimento\enspace|\enspace Enc.\,06--10 → Conflitos, Movimentos Sociais e Diversidade.",
    "metodologia": r"""A disciplina será desenvolvida ao longo de 10 encontros. As atividades combinarão exposição dialogada, leitura e discussão de textos clássicos e contemporâneos, análise de documentários, debates estruturados, estudos de caso e seminários temáticos.

A disciplina valoriza a participação ativa, o pensamento crítico e a construção coletiva do conhecimento. Os textos de referência serão disponibilizados em formato digital, e os debates serão orientados por roteiros de discussão e questões problematizadoras.""",
    "avaliacao": [
        r"1\textsuperscript{a}\,Avaliação (Teórica\,--\,individual): sociologia rural, agricultura familiar, políticas\,\dotfill\,\textbf{30\,\%}",
        r"2\textsuperscript{a}\,Avaliação (Seminário\,--\,em grupo): tema selecionado (capitalismo, movimentos, direitos)\,\dotfill\,\textbf{30\,\%}",
        r"3\textsuperscript{a}\,Avaliação (Ensaio Crítico\,--\,individual): reflexão articulando conteúdo e realidade local\,\dotfill\,\textbf{30\,\%}",
        r"Avaliação Contínua: participação em debates e fichamentos\,\dotfill\,\textbf{10\,\%}",
    ],
    "significado": r"""O componente curricular \textit{Sociologia Rural} é essencial para a formação humanística e crítica do(a) engenheiro(a) agrônomo(a), por oferecer instrumentos teóricos e analíticos para compreender a complexidade social do mundo rural brasileiro. A atuação profissional no campo exige mais do que competência técnica --- demanda sensibilidade para as relações sociais, respeito à diversidade cultural e compromisso com a justiça social.

A disciplina contribui para formar profissionais capazes de dialogar com diferentes atores sociais (agricultores familiares, povos tradicionais, movimentos sociais, agentes públicos), compreender os processos históricos de transformação do campo e avaliar criticamente as políticas e os modelos de desenvolvimento rural.""",
    "ref_basica": [
        r"WANDERLEY, M.\,N.\,B. \textbf{O mundo rural como espaço de vida}: reflexões sobre propriedade da terra, agricultura familiar e ruralidade. Porto Alegre: UFRGS, 2009.",
        r"SCHNEIDER, S. \textbf{A pluriatividade na agricultura familiar}. 2.\,ed. Porto Alegre: UFRGS, 2009.",
        r"ABRAMOVAY, R. \textbf{Paradigmas do capitalismo agrário em questão}. 3.\,ed. São Paulo: Edusp, 2007.",
        r"MARTINS, J.\,S. \textbf{Os camponeses e a política no Brasil}. 5.\,ed. Petrópolis: Vozes, 1995.",
        r"FERNANDES, B.\,M. \textbf{A formação do MST no Brasil}. Petrópolis: Vozes, 2000.",
    ],
    "ref_complementar": [
        r"VEIGA, J.\,E. \textbf{O desenvolvimento agrícola}: uma visão histórica. 2.\,ed. São Paulo: Edusp, 2007.",
        r"DELGADO, G.\,C. \textbf{Do capital financeiro na agricultura à economia do agronegócio}. Porto Alegre: UFRGS, 2012.",
        r"PLOEG, J.\,D. van der. \textbf{Camponeses e impérios alimentares}. Porto Alegre: UFRGS, 2008.",
        r"LITTLE, P.\,E. Territórios sociais e povos tradicionais no Brasil. \textit{Série Antropologia}, n.\,322. Brasília: UnB, 2002.",
        r"CARNEIRO, M.\,J. \textbf{Ruralidades contemporâneas}. Rio de Janeiro: Mauad X/FAPERJ, 2012.",
    ],
}


# ═══════════════════════════════════════════════════════════
# GENERATE ALL FILES
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    for slug, d in disciplines.items():
        outdir = os.path.join(WORKSPACE, "teaching", slug)
        outfile = os.path.join(outdir, "plano-pdf.tex")
        tex = generate_tex(d)
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(tex)
        print(f"✓ {slug}/plano-pdf.tex ({len(tex):,} chars)")
    
    print(f"\n{'='*50}")
    print(f"Generated {len(disciplines)} .tex files.")

import pdfplumber, glob, os, sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'aulas\analise_paisagem\extras\apresentacoes_alunos'
for f in sorted(glob.glob(os.path.join(d, '*.[pP][dD][fF]'))):
    print(f'\n========== {os.path.basename(f)} ==========')
    try:
        with pdfplumber.open(f) as pdf:
            for i, p in enumerate(pdf.pages):
                t = (p.extract_text() or '').strip()
                if t:
                    print(f'--- p{i+1} ---')
                    print(t)
    except Exception as e:
        print(f'ERR: {e}')

"""
Render specific slides from key PPTX presentations as PNG images
using PowerPoint COM automation.

Mapping:
  PPTX 1 "MUDANÇAS DE CENÁRIO"       → Ch01 transformações do mercado
  PPTX 2 "INTRODUÇÃO AO BRANDING"    → Ch02 o que é branding  +  Ch03 marca como ativo
  PPTX 3 "ESTRATÉGIA E DIFERENCIAÇÃO" → Ch05 estratégia diferenciação
  PPTX 4 "IDEIAS DIFERENCIADORAS"    → Ch06 ideias diferenciadoras
  PPTX 5 "ESTRATÉGIA DE PRODUTOS"    → Ch09 estratégia de produtos
  PPTX 6 "PÚBLICO IDEAL"             → Ch10 público ideal
  MOD2/4 "POSICIONAMENTO"            → Ch12 posicionamento
"""
import win32com.client
import os
import time

BASE_AULA = r"C:\Users\vidal\OneDrive\Documentos\1 - ACADEMICO\8 - MEUS CURSOS\1 - INTRODUÇÃO AO BRANDING\AULAS\PRIMEIRO MÓDULO\AULA"
BASE_MOD2 = r"C:\Users\vidal\OneDrive\Documentos\1 - ACADEMICO\8 - MEUS CURSOS\1 - INTRODUÇÃO AO BRANDING\AULAS\SEGUNDO MODULO\AULAS"
OUT_DIR = r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\meu_site\books\branding-agro\img\slides_render"

os.makedirs(OUT_DIR, exist_ok=True)

# Key slides to render: (file, slide_numbers, prefix)
targets = [
    # --- Ch01: Mudanças de cenário do mercado ---
    (os.path.join(BASE_AULA, "1. MUDANÇAS DE CENÁRIO DO MERCADO.pptx"),
     [
         4,   # Era uma vez um mercado - dificuldade antiga
         5,   # Demanda excedia oferta
         16,  # Pouca dificuldade = muitas empresas / mercado agressivo
         21,  # Qual nosso problema hoje? Todos iguais
         22,  # Você é só mais um
         23,  # Diferenciais tradicionais morreram
         26,  # Qualidade - todos tem acesso
         43,  # Preço não é diferencial
         54,  # O que é diferencial de verdade
         55,  # Seu diferencial não é mais o que você faz
         56,  # Granado - tradição
         57,  # Coca-cola - pioneirismo
         61,  # Apple/Starbucks - visão de mundo
         62,  # Body Shop/Natura - valores
         63,  # Chilli Beans/Havaianas - personalidade
     ], "ch01"),

    # --- Ch02-03: Introdução ao Branding ---
    (os.path.join(BASE_AULA, "2. INTRODUÇÃO AO BRANDING.pptx"),
     [
         9,   # Modelo: Materialização > Estratégia > Percepção > Gestão
         10,  # Estratégia > Identidade > Imagem
         27,  # Modelo completo de branding
         41,  # Cultura / Business / Diferenciais
         49,  # Sistema que funcione: diferenciais + cultura
         50,  # Definição de marca (Aaker)
         52,  # Marca ≠ Logo
         53,  # Marca = Reputação
         54,  # Reputação: Entrega vs Promessa
         56,  # Branding definição
         59,  # Identidade X Imagem
         62,  # Sua marca está na cabeça do outro
         66,  # Visível (pontos de contato) vs Invisível (estratégia)
         67,  # Gestão de marcas = esforço contínuo
         71,  # Branding vs Marketing
         81,  # O que é diferencial
         83,  # Tipos de diferenciais: estratégicos vs táticos
         103, # Pirâmide: Ideias > Benefícios > Suporte
     ], "ch02"),

    # --- Ch05: Estratégia e Diferenciação (já renderizado parcialmente) ---
    (os.path.join(BASE_AULA, "3. INTRODUÇÃO A ESTRATÉGIA E DIFERENCIAÇÃO.pptx"),
     [3, 10, 12, 33, 41, 42, 43, 44], "dif"),

    # --- Ch06: Ideias Diferenciadoras (já renderizado parcialmente) ---
    (os.path.join(BASE_AULA, "4. IDEIAS DIFERENCIADORAS.pptx"),
     [
         13,  # Uma ideia diferenciadora
         26, 27, 28, 29,  # Matriz: valor/imitabilidade
         30, 31,  # Diferencial / Fortaleza / Vulnerabilidades
         37,  # Pioneirismo título
         39,  # Uber - pioneirismo
         41,  # Coca vs Pepsi
         52,  # Tradição título
         53,  # Granado
         55,  # Phebo
         56,  # Gina
         60,  # História título
         61,  # Storytelling
         65,  # Storytelling ferramenta
         75,  # Experiência de mercado título
         85,  # Especialização título
         88,  # Especialização conceito
         97,  # Segmentação título
         110, # Forma de fabricação título
         112, # Fabricação exemplos
         125, # Autoria título
         126, # Brennand
         134, # Liderança título
         135, 136,  # Brahma / OMO
         145, # Preferência título
         146, # Lux
         155, # Performance título
         165, # Designer / Estilista título
         166, # Exemplo
         175, # Boutique título
         185, # Causa título
         186, # Exemplo causa
         199, # Premium título
         200, # Exemplo premium
         210, # Nicho título
         211, # Exemplo nicho
         220, # Escassez título
         221, # Exemplo escassez
     ], "ideias"),

    # --- Ch09: Estratégia de Produtos ---
    (os.path.join(BASE_AULA, "5. ESTRATÉGIA DE PRODUTOS.pptx"),
     [
         3,   # Dilema: excesso vs ampliação
         9,   # Produto x Público 
         10,  # Demanda: diferenciais + benefícios
         12,  # Produto > Público > Demanda > Credibilidade > Afinidade
         16,  # O que você vende? Ampliação de visão
         19,  # Oferta única
         21,  # Excesso de ofertas
         27,  # Paradoxo da escolha - insegurança
         28,  # Problemas: inseguros, adiam, menor satisfação
         29,  # Soluções: reduza opções (80/20)
         44,  # Precificação: custo vs valor
         62,  # Lei de Pareto 80/20
         64,  # Pareto: 20% árvores = 80% produção
         69,  # 20% clientes = 80% lucro
         71,  # Se não é lucrativo: substitua/repense/elimine
         86,  # Qual o papel de cada produto?
         93,  # Papéis: porta de entrada / visibilidade / posicionamento / recorrência
         100, # Reforçar posicionamento
         105, # Percepção de valor - exemplos preço
         109, # Geração de visibilidade
         112, # Porta de entrada
         115, # Complementar a oferta
         119, # Recorrência / novas vendas
     ], "ch09"),

    # --- Ch10: Público Ideal ---
    (os.path.join(BASE_AULA, "6. PÚBLICO IDEAL.pptx"),
     [
         5,   # Público Alvo vs Público Ideal
         10,  # User persona / Buyer persona / Brand persona
         18,  # Não seja genérico ou abrangente
         20,  # Público = quem mais provavelmente comprará
         21,  # Não pode atingir todo mundo - foco
         24,  # Focar não é limitar
         25,  # Entender conexões: visão de mundo, crenças, hábitos
         29,  # Relevante para poucos > irrelevante para muitos
         55,  # Até 3 públicos ideais
         77,  # Pareto em público: 20% = 80% lucro
         82,  # Fatores: financeiros + qualitativos
         84,  # Mais faturamento? Mais lucrativos? Conversão?
         88,  # Fatores subjetivos: engajamento, indicação
         107, # Canvas perfil público atual
         111, # Modelo B2B - perfil da empresa
         124, # Canvas proposta de valor - o que ele pensa e sente
         128, # Mapa de empatia
         143, # Processo contínuo: hipótese > dados > estratégia > validação
     ], "ch10"),

    # --- Ch12: Posicionamento ---
    (os.path.join(BASE_MOD2, "4. INTRODUÇÃO AO POSICIONAMENTO.pptx"),
     [
         3,   # É o seu posicionamento!
         6,   # Modelo: estratégia > identidade > posicionamento
         12,  # Posicionamento e plataforma da marca
         21,  # Produto > Público > Demanda > Credibilidade > Afinidade
         27,  # Quem quer ser tudo para todo mundo...
         28,  # Defina posicionamento: ideal vs real
         35,  # Você não é o produto que vende
         36,  # Cultura, valores, visão de mundo, propósito
         43,  # Enquadramento: designer gráfico ou...
         52,  # Enquadramento: quem é você
         57,  # Promessa de marca e alinhamento
         60,  # Promessa vs Entrega: decepção/satisfação/surpresa
         75,  # A marca como farol
         78,  # Do DNA à construção de valor
         83,  # Plataforma: cultura > estratégia > diferenciais > benefícios
         88,  # DNA > Valor > Reputação
         97,  # Quem NÃO somos?
         117, # Os 6 níveis de posicionamento: atributos
         122, # 6 níveis completo: atributos > discurso > personalidade > ideia > estratégico > propósito
         128, # Doenças de marca
         135, # Esquizofrenia de marca (principal problema)
         153, # Maria Ross: trying to be everything...
     ], "ch12"),
]

print("Starting PowerPoint...")
ppt = win32com.client.Dispatch("PowerPoint.Application")
ppt.Visible = True  # Need visible for Export to work

for filepath, slides, prefix in targets:
    if not os.path.exists(filepath):
        print(f"SKIP (not found): {filepath}")
        continue
    
    fname = os.path.basename(filepath)
    print(f"\nOpening: {fname}")
    pres = ppt.Presentations.Open(filepath, ReadOnly=True, WithWindow=False)
    total = pres.Slides.Count
    print(f"  Total slides: {total}")
    
    for snum in slides:
        if snum > total:
            print(f"  SKIP slide {snum} (max={total})")
            continue
        
        out_path = os.path.join(OUT_DIR, f"{prefix}_s{snum:03d}.png")
        try:
            slide = pres.Slides(snum)
            slide.Export(out_path, "PNG", 1920, 1080)
            sz = os.path.getsize(out_path) / 1024
            print(f"  s{snum:03d} -> {sz:.0f}KB")
        except Exception as e:
            print(f"  ERROR slide {snum}: {e}")
    
    pres.Close()
    print(f"  Closed: {fname}")

ppt.Quit()
print("\nDone! Rendered slides saved to:", OUT_DIR)

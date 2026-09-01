"""
Extract publications from Lattes XML and generate bibliography.bib + papers/index.qmd
"""
import re
import unicodedata
import sys

def slugify(text):
    """Create a simple slug from text for BibTeX keys."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '_', text).strip('_')[:40]

def extract_attr(block, attr):
    """Extract attribute value from XML-like block."""
    m = re.search(rf'{attr}="([^"]*)"', block)
    return m.group(1).strip() if m else ""

def clean_title(title):
    """Clean up title from OCR artifacts."""
    return title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').strip()

def main():
    xml_path = r"papers/7491112603328096.xml"
    
    with open(xml_path, 'r', encoding='iso-8859-1') as f:
        content = f.read()
    
    # Extract article blocks - each ARTIGO-PUBLICADO contains DADOS-BASICOS + DETALHAMENTO + AUTORES
    articles_raw = re.findall(r'<ARTIGO-PUBLICADO(.*?)</ARTIGO-PUBLICADO>', content, re.DOTALL)
    
    if not articles_raw:
        # Fallback: XML without proper tags, attributes concatenated
        # Split by ARTIGO-PUBLICADO
        articles_raw = re.split(r'ARTIGO-PUBLICADO(?:\s|>)', content)
    
    articles = []
    
    # Extract each ARTIGO-PUBLICADO block as a whole unit
    article_blocks = re.findall(r'<ARTIGO-PUBLICADO[^>]*>(.*?)</ARTIGO-PUBLICADO>', content, re.DOTALL)
    
    if not article_blocks:
        # Try alternative: split between tags
        article_blocks = re.findall(r'ARTIGO-PUBLICADO\b(.*?)(?=ARTIGO-PUBLICADO|ARTIGO-ACEITO-PARA-PUBLICACAO|</PRODUCAO-BIBLIOGRAFICA)', content, re.DOTALL)
    
    print(f"Found {len(article_blocks)} article blocks")
    
    for block in article_blocks:
        # Extract basic data
        dados_m = re.search(r'DADOS-BASICOS-DO-ARTIGO\s(.*?)/>', block, re.DOTALL)
        if not dados_m:
            continue
        
        title = extract_attr(dados_m.group(1), 'TITULO-DO-ARTIGO')
        year = extract_attr(dados_m.group(1), 'ANO-DO-ARTIGO')
        doi = extract_attr(dados_m.group(1), 'DOI')
        
        if not title or not year:
            continue
        
        # Extract details
        det_m = re.search(r'DETALHAMENTO-DO-ARTIGO\s(.*?)/>', block, re.DOTALL)
        journal = extract_attr(det_m.group(1), 'TITULO-DO-PERIODICO-OU-REVISTA') if det_m else ""
        volume = extract_attr(det_m.group(1), 'VOLUME') if det_m else ""
        pages_ini = extract_attr(det_m.group(1), 'PAGINA-INICIAL') if det_m else ""
        pages_fin = extract_attr(det_m.group(1), 'PAGINA-FINAL') if det_m else ""
        
        # Extract authors within THIS article block only
        author_matches = re.finditer(r'<AUTORES\s(.*?)/>', block, re.DOTALL)
        author_list = []
        for am in author_matches:
            nome = extract_attr(am.group(1), 'NOME-COMPLETO-DO-AUTOR')
            ordem = extract_attr(am.group(1), 'ORDEM-DE-AUTORIA')
            if nome:
                author_list.append((int(ordem) if ordem else 99, nome))
        
        # Sort by order of authorship
        author_list.sort(key=lambda x: x[0])
        # Deduplicate authors (preserve order)
        seen_authors = set()
        author_names = []
        for _, nome in author_list:
            nome_lower = nome.lower().strip()
            if nome_lower not in seen_authors:
                seen_authors.add(nome_lower)
                author_names.append(nome)
        
        # If no authors found, use default
        if not author_names:
            author_names = ["Santos, Luiz Diego Vidal"]
        
        pages = ""
        if pages_ini and pages_fin:
            pages = f"{pages_ini}--{pages_fin}"
        elif pages_ini:
            pages = pages_ini
        
        articles.append({
            'title': clean_title(title),
            'year': year,
            'doi': doi,
            'journal': journal,
            'volume': volume,
            'pages': pages,
            'authors': author_names,
        })
    
    # Sort by year descending, then title
    articles.sort(key=lambda a: (-int(a['year']), a['title']))
    
    # Remove exact duplicates (same title+year)
    seen = set()
    unique_articles = []
    for a in articles:
        key = (a['title'].lower()[:80], a['year'])
        if key not in seen:
            seen.add(key)
            unique_articles.append(a)
    articles = unique_articles
    
    print(f"Found {len(articles)} unique articles")
    
    # ==========================================
    # Also extract book chapters (CAPITULO-DE-LIVRO-PUBLICADO)
    # ==========================================
    chapters = []
    chapter_blocks = re.findall(r'<CAPITULO-DE-LIVRO-PUBLICADO[^>]*>(.*?)</CAPITULO-DE-LIVRO-PUBLICADO>', content, re.DOTALL)
    print(f"Found {len(chapter_blocks)} book chapter blocks")
    
    for block in chapter_blocks:
        dados_m = re.search(r'DADOS-BASICOS-DO-CAPITULO\s(.*?)/>', block, re.DOTALL)
        if not dados_m:
            continue
        title = extract_attr(dados_m.group(1), 'TITULO-DO-CAPITULO-DO-LIVRO')
        year = extract_attr(dados_m.group(1), 'ANO')
        doi = extract_attr(dados_m.group(1), 'DOI')
        if not title or not year:
            continue
        
        det_m = re.search(r'DETALHAMENTO-DO-CAPITULO\s(.*?)/>', block, re.DOTALL)
        book_title = extract_attr(det_m.group(1), 'TITULO-DO-LIVRO') if det_m else ""
        org = extract_attr(det_m.group(1), 'ORGANIZADORES') if det_m else ""
        publisher = extract_attr(det_m.group(1), 'NOME-DA-EDITORA') if det_m else ""
        pages_ini = extract_attr(det_m.group(1), 'PAGINA-INICIAL') if det_m else ""
        pages_fin = extract_attr(det_m.group(1), 'PAGINA-FINAL') if det_m else ""
        
        author_matches = re.finditer(r'<AUTORES\s(.*?)/>', block, re.DOTALL)
        author_list = []
        for am in author_matches:
            nome = extract_attr(am.group(1), 'NOME-COMPLETO-DO-AUTOR')
            ordem = extract_attr(am.group(1), 'ORDEM-DE-AUTORIA')
            if nome:
                author_list.append((int(ordem) if ordem else 99, nome))
        author_list.sort(key=lambda x: x[0])
        seen_a = set()
        author_names = []
        for _, nome in author_list:
            if nome.lower().strip() not in seen_a:
                seen_a.add(nome.lower().strip())
                author_names.append(nome)
        if not author_names:
            author_names = ["Santos, Luiz Diego Vidal"]
        
        pages = f"{pages_ini}--{pages_fin}" if pages_ini and pages_fin else pages_ini
        
        chapters.append({
            'title': clean_title(title),
            'year': year,
            'doi': doi,
            'booktitle': book_title,
            'publisher': publisher,
            'pages': pages,
            'authors': author_names,
            'type': 'incollection',
        })
    
    # Remove duplicate chapters
    seen = set()
    unique_chapters = []
    for c in chapters:
        key = (c['title'].lower()[:80], c['year'])
        if key not in seen:
            seen.add(key)
            unique_chapters.append(c)
    chapters = unique_chapters
    chapters.sort(key=lambda a: (-int(a['year']), a['title']))
    print(f"Found {len(chapters)} unique book chapters")
    
    # ==========================================
    # Also extract conference papers (TRABALHO-EM-EVENTOS)
    # ==========================================
    conf_papers = []
    conf_blocks = re.findall(r'<TRABALHO-EM-EVENTOS[^>]*>(.*?)</TRABALHO-EM-EVENTOS>', content, re.DOTALL)
    print(f"Found {len(conf_blocks)} conference paper blocks")
    
    for block in conf_blocks:
        dados_m = re.search(r'DADOS-BASICOS-DO-TRABALHO\s(.*?)/>', block, re.DOTALL)
        if not dados_m:
            continue
        title = extract_attr(dados_m.group(1), 'TITULO-DO-TRABALHO')
        year = extract_attr(dados_m.group(1), 'ANO-DO-TRABALHO')
        doi = extract_attr(dados_m.group(1), 'DOI')
        if not title or not year:
            continue
        
        det_m = re.search(r'DETALHAMENTO-DO-TRABALHO\s(.*?)/>', block, re.DOTALL)
        event_name = extract_attr(det_m.group(1), 'NOME-DO-EVENTO') if det_m else ""
        city = extract_attr(det_m.group(1), 'CIDADE-DO-EVENTO') if det_m else ""
        pages_ini = extract_attr(det_m.group(1), 'PAGINA-INICIAL') if det_m else ""
        pages_fin = extract_attr(det_m.group(1), 'PAGINA-FINAL') if det_m else ""
        
        author_matches = re.finditer(r'<AUTORES\s(.*?)/>', block, re.DOTALL)
        author_list = []
        for am in author_matches:
            nome = extract_attr(am.group(1), 'NOME-COMPLETO-DO-AUTOR')
            ordem = extract_attr(am.group(1), 'ORDEM-DE-AUTORIA')
            if nome:
                author_list.append((int(ordem) if ordem else 99, nome))
        author_list.sort(key=lambda x: x[0])
        seen_a = set()
        author_names = []
        for _, nome in author_list:
            if nome.lower().strip() not in seen_a:
                seen_a.add(nome.lower().strip())
                author_names.append(nome)
        if not author_names:
            author_names = ["Santos, Luiz Diego Vidal"]
        
        pages = f"{pages_ini}--{pages_fin}" if pages_ini and pages_fin else pages_ini
        
        conf_papers.append({
            'title': clean_title(title),
            'year': year,
            'doi': doi,
            'booktitle': event_name,
            'address': city,
            'pages': pages,
            'authors': author_names,
            'type': 'inproceedings',
        })
    
    # Remove duplicate conf papers
    seen = set()
    unique_conf = []
    for c in conf_papers:
        key = (c['title'].lower()[:80], c['year'])
        if key not in seen:
            seen.add(key)
            unique_conf.append(c)
    conf_papers = unique_conf
    conf_papers.sort(key=lambda a: (-int(a['year']), a['title']))
    print(f"Found {len(conf_papers)} unique conference papers")
    
    total = len(articles) + len(chapters) + len(conf_papers)
    print(f"TOTAL publications: {total}")
    
    # Generate BibTeX
    bib_entries = []
    used_keys = set()
    
    def make_unique_key(base_key):
        k = base_key
        suffix = 1
        while k in used_keys:
            k = f"{base_key}_{suffix}"
            suffix += 1
        used_keys.add(k)
        return k
    
    # Articles
    for a in articles:
        first_author_last = a['authors'][0].split(',')[0].split()[-1] if a['authors'] else 'santos'
        key = make_unique_key(slugify(f"{first_author_last}_{a['year']}_{a['title'][:30]}"))
        
        bib_authors = " and ".join(a['authors'])
        
        entry = f"@article{{{key},\n"
        entry += f"  title = {{{a['title']}}},\n"
        entry += f"  author = {{{bib_authors}}},\n"
        entry += f"  journal = {{{a['journal']}}},\n"
        entry += f"  year = {{{a['year']}}},\n"
        if a['volume']:
            entry += f"  volume = {{{a['volume']}}},\n"
        if a['pages']:
            entry += f"  pages = {{{a['pages']}}},\n"
        if a['doi']:
            entry += f"  doi = {{{a['doi']}}},\n"
        entry += "}\n"
        bib_entries.append(entry)
    
    # Book chapters
    for c in chapters:
        first_author_last = c['authors'][0].split(',')[0].split()[-1] if c['authors'] else 'santos'
        key = make_unique_key(slugify(f"{first_author_last}_{c['year']}_{c['title'][:30]}"))
        
        bib_authors = " and ".join(c['authors'])
        
        entry = f"@incollection{{{key},\n"
        entry += f"  title = {{{c['title']}}},\n"
        entry += f"  author = {{{bib_authors}}},\n"
        entry += f"  booktitle = {{{c['booktitle']}}},\n"
        entry += f"  year = {{{c['year']}}},\n"
        if c['publisher']:
            entry += f"  publisher = {{{c['publisher']}}},\n"
        if c['pages']:
            entry += f"  pages = {{{c['pages']}}},\n"
        if c['doi']:
            entry += f"  doi = {{{c['doi']}}},\n"
        entry += "}\n"
        bib_entries.append(entry)
    
    # Conference papers
    for c in conf_papers:
        first_author_last = c['authors'][0].split(',')[0].split()[-1] if c['authors'] else 'santos'
        key = make_unique_key(slugify(f"{first_author_last}_{c['year']}_{c['title'][:30]}"))
        
        bib_authors = " and ".join(c['authors'])
        
        entry = f"@inproceedings{{{key},\n"
        entry += f"  title = {{{c['title']}}},\n"
        entry += f"  author = {{{bib_authors}}},\n"
        entry += f"  booktitle = {{{c['booktitle']}}},\n"
        entry += f"  year = {{{c['year']}}},\n"
        if c.get('address'):
            entry += f"  address = {{{c['address']}}},\n"
        if c['pages']:
            entry += f"  pages = {{{c['pages']}}},\n"
        if c['doi']:
            entry += f"  doi = {{{c['doi']}}},\n"
        entry += "}\n"
        bib_entries.append(entry)
    
    # Write .bib file
    with open('papers/bibliography.bib', 'w', encoding='utf-8') as f:
        for entry in bib_entries:
            f.write(entry + "\n")
    
    print(f"Written {len(bib_entries)} entries to papers/bibliography.bib")
    
    # Generate papers/index.qmd
    qmd = f"""---
title: "Publicações Acadêmicas"
bibliography: bibliography.bib
csl: https://raw.githubusercontent.com/citation-style-language/styles/master/apa.csl
nocite: |
  @*
---

Publicações acadêmicas de **Luiz Diego Vidal Santos**. Para informações completas e atualizadas, consulte:

- {{{{< ai orcid >}}}} [ORCID — 0000-0001-8659-8557](https://orcid.org/0000-0001-8659-8557)
- {{{{< fa graduation-cap >}}}} [Plataforma Lattes](http://lattes.cnpq.br/7491112603328096)

::: {{.callout-tip}}
## Resumo
- **{len(articles)}** artigos em periódicos
- **{len(chapters)}** capítulos de livros
- **{len(conf_papers)}** trabalhos em eventos
- **{total}** publicações no total

Dados extraídos automaticamente do Currículo Lattes (XML).
:::

::: {{#refs}}
:::
"""
    
    with open('papers/index.qmd', 'w', encoding='utf-8') as f:
        f.write(qmd)
    
    print("Written papers/index.qmd")

if __name__ == '__main__':
    main()

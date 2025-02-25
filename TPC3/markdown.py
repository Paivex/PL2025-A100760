import re

def markdown_to_html(markdown: str) -> str:
    # Cabeçalhos
    markdown = re.sub(r'^# (.+)$', r'<h1>\1</h1>', markdown, flags=re.MULTILINE)
    markdown = re.sub(r'^## (.+)$', r'<h2>\1</h2>', markdown, flags=re.MULTILINE)
    markdown = re.sub(r'^### (.+)$', r'<h3>\1</h3>', markdown, flags=re.MULTILINE)
    
    # Negrito
    markdown = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', markdown)
    
    # Itálico
    markdown = re.sub(r'(?<!\!)\*(.*?)\*', r'<i>\1</i>', markdown)
    
    # Imagens
    markdown = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1"/>', markdown)
    
    # Listas numeradas
    markdown = re.sub(r'(?:^|\n)(\d+\. .+)', r'<li>\1</li>', markdown)
    markdown = re.sub(r'(<li>\d+\. .+</li>\n?)+', lambda m: f"<ol>\n{m.group(0)}\n</ol>", markdown)
    markdown = re.sub(r'<li>(\d+\. )', r'    <li>', markdown)
    markdown = re.sub(r'</li>', r'</li>\n', markdown)
    
    # Links
    markdown = re.sub(r'(?<!!)\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', markdown)
    
    return markdown.strip()

if __name__ == "__main__":
    print("Insira o texto em Markdown (digite 'x' para terminar):")
    lines = []
    while True:
        try:
            line = input()
            if line.strip().lower() == 'x':
                break
            lines.append(line)
        except EOFError:
            break
    
    md_text = "\n".join(lines)
    html_output = markdown_to_html(md_text)
    
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(html_output)
    
    print("\nHTML gerado e guardado em 'output.txt'.")

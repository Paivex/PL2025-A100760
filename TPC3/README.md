**Conversor de Markdown para HTML**

**Requisitos**

Neste TPC, o objetivo foi criar um script Python que converte um texto em formato Markdown para HTML, seguindo os requisitos:

Cabeçalhos: # Exemplo, ## Exemplo, ### Exemplo

Negrito: **exemplo**

Itálico: *exemplo*

Listas numeradas:

Item 1

Item 2

Item 3

Links: [texto](endereço)

Imagens: ![texto alternativo](caminho para a imagem)

**Solução**

Para a implementação, foi utilizada a biblioteca re (expressões regulares) para realizar a conversão de Markdown para HTML.

Para negrito, itálico, imagens e links, foram usadas expressões regulares com re.sub:

Negrito: \*\*(.*?)\*\* → <b>texto</b>

Itálico: \*(.*?)\* → <i>texto</i>

Imagens: !\[(.*?)\]\((.*?)\) → <img src="URL" alt="texto"/>

Links: \[(.*?)\]\((.*?)\) → <a href="URL">texto</a>

Para cabeçalhos e listas numeradas, foi adotada uma lógica diferente:

Utiliza-se re.sub para identificar #, ##, ### no início das linhas e substituí-los pelos elementos HTML <h1>, <h2>, <h3>.

Listas numeradas:

Utiliza-se re.sub para identificar itens numerados (1. item) e envolvê-los dentro de <ol> e <li>.

Para garantir a correta estruturação das listas, o código verifica se a lista foi iniciada e fecha corretamente a tag <ol> quando necessário.

**Output**

O script lê o texto inserido pelo utilizador, processa-o e guarda o resultado num ficheiro output.txt.
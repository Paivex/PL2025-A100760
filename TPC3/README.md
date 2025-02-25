# Conversor de Markdown para HTML

## Requisitos

Este projeto consiste num script Python que converte texto em formato Markdown para HTML. O código suporta a seguinte sintaxe básica:

```markdown
# Cabeçalhos
## Subcabeçalhos
### Subsubcabeçalhos

**Negrito**
*Itálico*

1. Item de lista 1
2. Item de lista 2
3. Item de lista 3

[Texto do link](https://exemplo.com)

![Texto alternativo](caminho/para/imagem.jpg)
```

## Solução

O código utiliza a biblioteca `re` para processar as marcações Markdown e convertê-las para HTML.

### Estratégia Utilizada

Para **negrito, itálico, imagens e links**, foram utilizadas expressões regulares com `re.sub`:

```python
# Negrito: **texto** → <b>texto</b>
re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', markdown)

# Itálico: *texto* → <i>texto</i>
re.sub(r'(?<!\!)\*(.*?)\*', r'<i>\1</i>', markdown)

# Imagens: ![alt](url) → <img src="url" alt="alt"/>
re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1"/>', markdown)

# Links: [texto](url) → <a href="url">texto</a>
re.sub(r'(?<!!)\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', markdown)
```

Para **cabeçalhos e listas numeradas**, foi usada uma abordagem específica:

- **Cabeçalhos**:
  - Identificam-se `#`, `##` e `###` no início das linhas e substituem-se pelas tags HTML `<h1>`, `<h2>`, `<h3>`.

- **Listas numeradas**:
  - Identifica-se se uma linha começa com um número seguido de um ponto (`1. `) para determinar se é um item de lista.
  - Envolve-se a lista entre `<ol>` e `<li>`.
  - Garante-se que a lista é fechada corretamente quando necessário.

### Detalhes Adicionais

O script recolhe a entrada do utilizador através do terminal e gera um ficheiro `output.txt` contendo a versão HTML correspondente ao Markdown inserido.




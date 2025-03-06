# Analisador Léxico para Consultas SPARQL Simplificadas

Este trabalho implementa um analisador léxico em Python utilizando a biblioteca `ply.lex`. O lexer processa consultas de uma linguagem.

## Estrutura da Solução

O código define um conjunto de tokens que representam os principais elementos de uma consulta, incluindo:
- **Palavras-chave**: `SELECT`, `WHERE`, `LIMIT`
- **Identificadores**: Prefixos (`dbo:`, `foaf:`) e variáveis (`?variavel`)
- **Símbolos especiais**: `{ } .`
- **Strings**: Expressões entre aspas com etiquetas de idioma (`"texto"@lang`)
- **Números**: Constantes numéricas
- **Comentários**: Linhas iniciadas com `#`

O lexer percorre a entrada e extrai tokens de forma sequencial, ignorando espaços e quebras de linha desnecessárias.

## Execução e Resultados

Ao executar o código, o lexer processa a seguinte consulta de exemplo:

```
# DBPedia: obras de Chuck Berry
select ?nome ?desc where {
?s a dbo:MusicalArtist.
?s foaf:name "Chuck Berry"@en .
?w dbo:artist ?s.
?w foaf:name ?nome.
?w dbo:abstract ?desc
} LIMIT 1000
```

O resultado esperado é uma lista de tokens identificados corretamente, como:
```
LexToken(COMMENT, '# DBPedia: obras de Chuck Berry', 1, 0)
LexToken(SELECT, 'select', 2, 35)
LexToken(VARIABLE, '?nome', 2, 42)
LexToken(VARIABLE, '?desc', 2, 48)
LexToken(WHERE, 'where', 2, 54)
LexToken(LBRACE, '{', 2, 60)
LexToken(VARIABLE, '?s', 3, 62)
LexToken(PREFIX, 'dbo:MusicalArtist', 3, 65)
...
```


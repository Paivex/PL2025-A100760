# Análise de Obras Musicais

Este programa lê um ficheiro CSV (`obras.csv`) contendo informações sobre obras musicais e apresenta estatísticas organizadas por período musical.

**Funcionalidades**
- Extrai dados do CSV utilizando **expressões regulares**.
- Gera uma **lista ordenada de compositores**.
- Conta e apresenta o **número de obras por período**.
- Agrupa e ordena os **títulos das obras por período**.

**Estrutura do Código**
1. **Leitura do ficheiro CSV**  
   - O cabeçalho é ignorado.  
   - Cada linha é processada com **regex** para extrair os campos corretamente.  

2. **Armazenamento dos dados**  
   - Os compositores são guardados num **conjunto (set)** para evitar repetições.  
   - As obras são organizadas num **dicionário por período**, tanto para contagem como para listagem dos títulos.  

3. **Ordenação e Apresentação dos Resultados**  
   - Os compositores são ordenados alfabeticamente e impressos um por linha.  
   - As obras são agrupadas por período, apresentando a contagem e os títulos de forma organizada.  

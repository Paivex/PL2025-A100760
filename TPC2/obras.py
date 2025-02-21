import re

# Expressão regular para extrair os campos do CSV
padrao_regex = re.compile(
    r'([^;]+);("(?:[^"]*(?:"[^"]*)*)"|[^;]+);([^;]+);([^;]+);([^;]+);([^;]*)\n?'
)

# Conjunto para armazenar os compositores únicos
compositores = set()

obras_por_periodo = {}
titulos_por_periodo = {}

with open("obras.csv", "r", encoding="utf-8") as ficheiro:
    ficheiro.readline()  # Ignorar cabeçalho
    buffer_linha = ""
    
    for linha in ficheiro:
        buffer_linha += linha
        correspondencia = re.match(padrao_regex, buffer_linha)
        
        if correspondencia:
            titulo = correspondencia.group(1).strip()
            periodo = correspondencia.group(4).strip()
            compositor = correspondencia.group(5).strip()
            
            compositores.add(compositor)
            
            obras_por_periodo[periodo] = obras_por_periodo.get(periodo, 0) + 1
            
            if periodo not in titulos_por_periodo:
                titulos_por_periodo[periodo] = []
            titulos_por_periodo[periodo].append(titulo)
            
            buffer_linha = ""

# Ordenar os compositores e os títulos
compositores_ordenados = sorted(compositores)
for periodo in titulos_por_periodo:
    titulos_por_periodo[periodo].sort()

# Apresentar os resultados
print("1. Lista de compositores (ordenada alfabeticamente):")
for compositor in compositores_ordenados:
    print(compositor)

print("\n2. Número de obras por período:")
for periodo in sorted(obras_por_periodo.keys()):
    print(f"{periodo}: {obras_por_periodo[periodo]} obras")

print("\n3. Títulos organizados por período:")
for periodo in sorted(titulos_por_periodo.keys()):
    print(f"\n{periodo}:")
    for titulo in titulos_por_periodo[periodo]:
        print(f"\t- {titulo}")

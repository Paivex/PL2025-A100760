import sys

def process_text(text):
    sum_active = True  # Inicialmente, a soma está ativa
    total_sum = 0
    output_lines = []
    
    lines = text.split("\n") 
    
    for line in lines:
        words = line.split()
        new_line = []
        
        for word in words:
            cleaned_word = "".join(filter(str.isalnum, word))  # Remover pontuação para análise
            
            if cleaned_word.lower() == "off":
                sum_active = False
                new_line.append(word)  
            elif cleaned_word.lower() == "on":
                sum_active = True
                new_line.append(word)  
            
            new_line.append(word) 
            
            if "=" in word:
                output_lines.append(" ".join(new_line))  
                output_lines.append(f">> {total_sum}")  # Exibir a soma atual
                new_line = [] 
            elif sum_active and cleaned_word.isdigit():
                total_sum += int(cleaned_word)
        
        if new_line:
            output_lines.append(" ".join(new_line))  
    
    output_lines.append(f">> {total_sum}")  # Imprimir soma final
    return "\n".join(output_lines)

if __name__ == "__main__":
    input_text = sys.stdin.read() 
    output_text = process_text(input_text)
    print(output_text)

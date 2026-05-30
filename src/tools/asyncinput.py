import sys
import uselect
import asyncio

async def async_input(prompt):
    print(prompt, end="")
    
    # Configura o monitoramento do terminal (stdin) no MicroPython
    poller = uselect.poll()
    poller.register(sys.stdin, uselect.POLLIN)
    
    buffer = ""
    
    while True:
        # Verifica se há alguma tecla pressionada (timeout = 0 para não travar)
        if poller.poll(0):
            char = sys.stdin.read(1)
            
            # Se for Enter (fim da linha)
            if char == '\n' or char == '\r':
                print()  # Salta a linha no terminal
                poller.unregister(sys.stdin)
                return buffer
            
            # Se for Backspace (apagar caractere)
            elif char == '\x08' or char == '\x7f':
                if len(buffer) > 0:
                    buffer = buffer[:-1]
                    sys.stdout.write('\b \b')  # Apaga o caractere visualmente no terminal
            
            # Qualquer outro caractere comum
            else:
                buffer += char
                sys.stdout.write(char)  # Faz o "echo" do caractere na tela
        
        # ESSENCIAL: Passa o controle para o asyncio atualizar a animação do display
        await asyncio.sleep(0.02)
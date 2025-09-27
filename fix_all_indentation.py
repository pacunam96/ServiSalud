#!/usr/bin/env python3

# Script para corregir todas las indentaciones problemáticas en app.py
with open('app.py', 'r') as f:
    content = f.read()

# Dividir en líneas
lines = content.split('\n')

# Corregir líneas específicas
for i, line in enumerate(lines):
    line_num = i + 1
    
    # Corregir línea 460
    if line_num == 460:
        lines[i] = "                            client = Socrata(\"www.datos.gov.co\", None)"
    
    # Corregir línea 488
    elif line_num == 488:
        lines[i] = "                    except Exception as e:"

# Escribir el archivo corregido
with open('app.py', 'w') as f:
    f.write('\n'.join(lines))

print("Todas las indentaciones corregidas")

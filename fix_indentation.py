#!/usr/bin/env python3

# Script para corregir la indentación en app.py
with open('app.py', 'r') as f:
    lines = f.readlines()

# Corregir la línea 460 (índice 459)
if len(lines) > 459:
    lines[459] = "                            client = Socrata(\"www.datos.gov.co\", None)\n"

# Escribir el archivo corregido
with open('app.py', 'w') as f:
    f.writelines(lines)

print("Indentación corregida")

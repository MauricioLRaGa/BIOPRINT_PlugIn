#!/bin/bash
# ============================================================
# validar_y_copiar.sh
# Valida el QML del plugin y lo copia a Cura si es correcto
# Tesis PUCP - Mauricio Ramos Gallegos
# Uso: bash ~/Desktop/BIOSLICER/validar_y_copiar.sh
# ============================================================

# Rutas relativas — funciona en cualquier máquina
BIOSLICER="$(cd "$(dirname "$0")" && pwd)"
CURA_QML="$APPDATA/cura/5.7/plugins/BioprintingPlugin/resources/qml"
CURA_PLUGIN="$APPDATA/cura/5.7/plugins/BioprintingPlugin"

echo "============================================"
echo " Bioprinting Plugin — Validador QML"
echo "============================================"
echo "BIOSLICER: $BIOSLICER"
echo ""

# Verificar que los archivos existen
if [ ! -f "$BIOSLICER/resources/qml/BioprintingDialog.qml" ]; then
    echo "ERROR: No se encontro BioprintingDialog.qml"
    echo "Ruta buscada: $BIOSLICER/resources/qml/"
    exit 1
fi

# Validar QML con Python
python3 - "$BIOSLICER" << 'PYEOF'
import sys
import os

bioslicer = sys.argv[1]

files = [
    os.path.join(bioslicer, "resources", "qml", "BioprintingDialog.qml"),
    os.path.join(bioslicer, "resources", "qml", "AboutDialog.qml"),
]

all_ok = True

for filepath in files:
    filename = os.path.basename(filepath)

    if not os.path.exists(filepath):
        print(f"SKIP: {filename} no encontrado en {filepath}")
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []

    # Verificar llaves balanceadas
    opens  = content.count('{')
    closes = content.count('}')
    if opens != closes:
        errors.append(f"  Llaves: {opens} abiertas vs {closes} cerradas")

    # Verificar punto y coma fuera de strings
    for i, line in enumerate(content.split('\n'), 1):
        s = line.strip()
        if s.startswith('//'):
            continue
        in_str = False
        for c in s:
            if c == '"':
                in_str = not in_str
            if c == ';' and not in_str and 'for (' not in s and 'while (' not in s:
                errors.append(f"  Semicolon L{i}: {s[:55]}")
                break

    if errors:
        print(f"[ERROR] {filename}:")
        for e in errors:
            print(e)
        all_ok = False
    else:
        lines = len(content.split('\n'))
        print(f"[OK]    {filename} — {lines} lineas, llaves balanceadas")

sys.exit(0 if all_ok else 1)
PYEOF

# Si la validacion fallo, salir
if [ $? -ne 0 ]; then
    echo ""
    echo "Corrige los errores antes de copiar a Cura."
    exit 1
fi

echo ""
echo "Copiando archivos a Cura..."

# Crear carpeta qml si no existe
mkdir -p "$CURA_QML"

# Copiar QML
cp "$BIOSLICER/resources/qml/BioprintingDialog.qml" "$CURA_QML/" && echo "  BioprintingDialog.qml copiado"
cp "$BIOSLICER/resources/qml/AboutDialog.qml"       "$CURA_QML/" && echo "  AboutDialog.qml copiado"

# Copiar Python
cp "$BIOSLICER/BioprintingPlugin.py" "$CURA_PLUGIN/" && echo "  BioprintingPlugin.py copiado"
cp "$BIOSLICER/__init__.py"          "$CURA_PLUGIN/" && echo "  __init__.py copiado"
cp "$BIOSLICER/plugin.json"          "$CURA_PLUGIN/" && echo "  plugin.json copiado"

# Copiar ScaffoldGenerator si existe
if [ -f "$BIOSLICER/ScaffoldGenerator.py" ]; then
    cp "$BIOSLICER/ScaffoldGenerator.py" "$CURA_PLUGIN/" && echo "  ScaffoldGenerator.py copiado"
fi

echo ""
echo "============================================"
echo " Listo. Reinicia Cura para ver los cambios."
echo "============================================"

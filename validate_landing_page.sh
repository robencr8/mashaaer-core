#!/bin/bash

# Validar que cosmic_onboarding.html es la página de inicio predeterminada
echo "Verificando que cosmic_onboarding.html es la página de inicio..."

# Verificar que el archivo cosmic_onboarding.html existe tanto en la raíz como en templates
if [ -f "cosmic_onboarding.html" ] && [ -f "templates/cosmic_onboarding.html" ]; then
    echo "✅ Archivos cosmic_onboarding.html encontrados en ambas ubicaciones"
else
    echo "❌ No se encontraron los archivos cosmic_onboarding.html en una o ambas ubicaciones"
    echo "Reparando la situación..."
    # Si existe en la raíz pero no en templates, copiar a templates
    if [ -f "cosmic_onboarding.html" ] && [ ! -f "templates/cosmic_onboarding.html" ]; then
        cp cosmic_onboarding.html templates/cosmic_onboarding.html
        echo "✅ Archivo copiado de la raíz a templates/"
    # Si existe en templates pero no en la raíz, copiar a la raíz
    elif [ ! -f "cosmic_onboarding.html" ] && [ -f "templates/cosmic_onboarding.html" ]; then
        cp templates/cosmic_onboarding.html cosmic_onboarding.html
        echo "✅ Archivo copiado de templates/ a la raíz"
    else
        echo "❌ No se encontró cosmic_onboarding.html en ninguna ubicación"
        exit 1
    fi
fi

# Verificar que main.py tiene configurada la ruta de inicio para servir cosmic_onboarding.html
if grep -q "def index():" main.py && grep -q "cosmic_onboarding.html" main.py; then
    echo "✅ La ruta de inicio en main.py está configurada correctamente"
else
    echo "❌ La ruta de inicio en main.py no está configurada para cosmic_onboarding.html"
    exit 1
fi

echo "✅ Validación completa: cosmic_onboarding.html es la página de inicio predeterminada"
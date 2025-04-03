#!/bin/bash

# Copiar el archivo cosmic_onboarding.html de la raíz a la carpeta templates
echo "Copiando cosmic_onboarding.html a templates..."
cp cosmic_onboarding.html templates/cosmic_onboarding.html

# Verificar si la copia fue exitosa
if [ $? -eq 0 ]; then
    echo "✅ Archivo copiado exitosamente"
else
    echo "❌ Error al copiar el archivo"
    exit 1
fi

# Verificar que el archivo en templates tenga el formato HTML correcto
if grep -q "<!DOCTYPE html>" templates/cosmic_onboarding.html; then
    echo "✅ Archivo HTML tiene la estructura correcta"
else
    echo "❌ El archivo HTML no tiene la estructura correcta"
    exit 1
fi

echo "Proceso completado exitosamente."
#!/bin/bash

# Create a backup of the original file
cp cosmic_onboarding.html cosmic_onboarding.html.manual_backup

# Use sed to replace the GET fetch with a POST fetch
sed -i 's|fetch(.\\/api\\/listen-for-voice?language=. + userLanguage)|fetch('\''\/api\/listen-for-voice'\'', {\n        method: '\''POST'\'',\n        headers: {\n          '\''Content-Type'\'': '\''application\/json'\''\n        },\n        body: JSON.stringify({\n          language: userLanguage\n        })\n      })|g' cosmic_onboarding.html

echo "Update completed."

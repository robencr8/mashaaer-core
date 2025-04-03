#!/bin/bash

# Update first listen-for-voice call
sed -i '1005,1007s|fetch(.*/api/listen-for-voice?language=.*userLanguage).*|fetch("/api/listen-for-voice", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          language: userLanguage
        })
      })|' templates/cosmic_onboarding.html

# Update second listen-for-voice call
sed -i '1093,1095s|fetch(.*/api/listen-for-voice?language=.*userLanguage).*|fetch("/api/listen-for-voice", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          language: userLanguage
        })
      })|' templates/cosmic_onboarding.html

echo "API calls updated in cosmic_onboarding.html"

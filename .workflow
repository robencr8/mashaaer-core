<name>
Start Mashaaer App
</name>
<command>
cd "$(dirname "$0")" && gunicorn --bind 0.0.0.0:8080 --reuse-port --timeout 120 --reload main:app
</command>

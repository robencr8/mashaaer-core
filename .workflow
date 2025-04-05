name = "Start application"
command = "gunicorn --bind 0.0.0.0:5000 --reuse-port --reload --timeout 120 --workers 3 --access-logfile - main:app"

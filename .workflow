name = "Start application"
command = "gunicorn --bind 0.0.0.0:5000 --reuse-port --reload --access-logfile - --error-logfile - main:app"

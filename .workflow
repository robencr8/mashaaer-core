<workflow>
<name>
Start application
</name>
<command>
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
</command>
</workflow>

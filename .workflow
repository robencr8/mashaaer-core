<workflow>
<name>
Start application
</name>
<command>
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload standalone_pwa:app
</command>
</workflow>

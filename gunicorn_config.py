"""
Gunicorn configuration file for Mashaaer Feelings application.

This configuration is specifically designed for Replit deployment.
"""
import os
import logging
import logging.handlers
import multiprocessing

# Basic server settings
bind = "0.0.0.0:5000"
backlog = 2048
worker_class = "sync"  # Standard synchronous workers
workers = 1  # For Replit, we use a single worker
timeout = 30
keepalive = 2

# Logging
loglevel = "info"
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "mashaaer_app"
default_proc_name = "mashaaer_app"

# Server mechanics
daemon = False  # Don't daemonize on Replit
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Server hooks
def on_starting(server):
    print("Starting Mashaaer Feelings application with Gunicorn...")

def on_reload(server):
    print("Reloading Mashaaer Feelings application...")

def when_ready(server):
    print(f"Gunicorn server is ready. Listening at: {bind}")
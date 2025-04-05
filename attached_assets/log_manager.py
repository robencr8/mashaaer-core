import csv
from datetime import datetime

def log_interaction(user_input, emotion, action, params):
    with open('logs/interaction_log.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.utcnow(), user_input, emotion, action, str(params)])
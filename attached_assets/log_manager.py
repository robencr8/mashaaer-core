import csv
from datetime import datetime

def log_interaction(user_input, emotion, action, params, file='logs/interaction_log.csv'):
    with open(file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.utcnow(), user_input, emotion, action, params])

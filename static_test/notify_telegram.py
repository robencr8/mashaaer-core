import os
import sys
import requests

# متغيرات البيئة أو مباشر
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN",
                      "7664942391:AAGobNjnvGrMOZTtL_b6g0T80DvAzrOu_LI")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7769852671")


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("✅ Message sent to Telegram")
    except requests.exceptions.RequestException as e:
        print("❌ Failed to send message:", e)


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) if len(
        sys.argv) > 1 else "Hello from Mashaaer 🪐"
    send_telegram_message(msg)

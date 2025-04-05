import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def update_audio_handling(filepath: str) -> bool:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return False

    soup = BeautifulSoup(content, 'html.parser')

    if not soup.find(id="audio-notification"):
        notification_div = soup.new_tag("div", id="audio-notification")
        notification_div['style'] = (
            "position: fixed; bottom: 20px; left: 0; right: 0; text-align: center; padding: 10px; "
            "background-color: rgba(0, 0, 0, 0.7); color: white; z-index: 1000; border-radius: 5px; "
            "margin: 0 auto; width: fit-content; max-width: 80%; font-size: 14px; display: none;"
        )
        notification_div.append(soup.new_tag("span", **{"class": "ar"})).string = "انقر لتفعيل الصوت"
        notification_div.append(soup.new_tag("span", **{"class": "en"})).string = "Click anywhere to enable audio"

        body = soup.body
        if body:
            body.insert(0, notification_div)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        logger.info(f"Audio interaction features added to: {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to write changes to {filepath}: {str(e)}")
        return False

import os
import time
import re
import winsound
import requests
from dotenv import load_dotenv
from PIL import ImageGrab
import pytesseract

load_dotenv()

tesseract_path = os.environ.get("TESSERACT_PATH")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    print(f"✅ ใช้ Tesseract จาก: {tesseract_path}")
else:
    print("⚠️ ไม่พบ TESSERACT_PATH")

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
if DISCORD_WEBHOOK_URL:
    print("✅ พบ Discord Webhook URL แล้ว")
else:
    print("⚠️ ไม่พบ DISCORD_WEBHOOK_URL ใน .env — จะไม่ส่งแจ้งเตือนไป Discord")

# ==========================================
# ตั้งค่า
# ==========================================
# จัดจอ 1920x1080 เป็น 4 ส่วน:
# ซ้ายบน = (0, 0, 960, 540)
# ขวาบน = (960, 0, 960, 540)
# ซ้ายล่าง = (0, 540, 960, 540)
# ขวาล่าง = (960, 540, 960, 540)
REGION = (0, 0, 960, 540)
KEYWORDS = ["spawned in"]
CHECK_INTERVAL = 2
THRESHOLD = 150
DEBUG = False
COOLDOWN_SECONDS = 230


def preprocess_image(img):
    gray = img.convert("L")
    bw = gray.point(lambda x: 255 if x > THRESHOLD else 0, mode="1")
    bw = bw.resize((bw.width * 2, bw.height * 2))
    return bw


def clean_text(text):
    lines = text.split("\n")
    seen = set()
    unique_lines = []
    for line in lines:
        clean = line.strip()
        if clean and clean not in seen:
            seen.add(clean)
            unique_lines.append(clean)
    return unique_lines


def check_keywords(lines, keywords):
    found = []
    for line in lines:
        line_lower = line.lower()
        for kw in keywords:
            if kw.lower() in line_lower:
                found.append(kw)
    return found


def send_discord_alert(keyword):
    """ส่งข้อความแจ้งเตือนไปยัง Discord ผ่าน Webhook"""
    if not DISCORD_WEBHOOK_URL:
        return

    payload = {
        "content": "🔔 **พบไข่หายาก!**"
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code in (200, 204):
            print(f"✅ ส่งแจ้งเตือนไป Discord สำเร็จ: {keyword}")
        else:
            print(f"⚠️ ส่งไป Discord ไม่สำเร็จ (status {response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ ส่งไป Discord ล้มเหลว: {e}")


def alert(keyword):
    print(f"🔔 พบไข่หายาก! -> {keyword}")
    try:
        winsound.Beep(1000, 500)
    except RuntimeError:
        pass
    send_discord_alert(keyword)


def main():
    print("เริ่มตรวจจับ... กด Ctrl+C เพื่อหยุด")
    last_alert_time = {}

    while True:
        try:
            screenshot = ImageGrab.grab(bbox=REGION)
            processed = preprocess_image(screenshot)
            text = pytesseract.image_to_string(processed)

            unique_lines = clean_text(text)

            if DEBUG:
                print("─" * 40)
                print("📷 OCR อ่านได้ (ตัดซ้ำแล้ว):")
                for line in unique_lines:
                    print(f"  • {line}")
                if not unique_lines:
                    print("  (ว่างเปล่า)")
                print("─" * 40)

            found_keywords = check_keywords(unique_lines, KEYWORDS)
            now = time.time()

            for kw in set(found_keywords):
                last_time = last_alert_time.get(kw, 0)
                if now - last_time >= COOLDOWN_SECONDS:
                    alert(kw)
                    last_alert_time[kw] = now

        except Exception as e:
            print(f"เกิดข้อผิดพลาด: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
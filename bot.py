import time
import mss
import pytesseract
from PIL import Image
import requests
from collections import deque

# =========================
# ⚙️ ตั้งค่าหลัก (แก้ตรงนี้)
# =========================

# ถ้าใช้ Windows และยังไม่ได้ตั้ง PATH ให้ tesseract ให้เปิดบรรทัดล่างแล้วใส่ path จริง
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# พื้นที่จอที่แชท Roblox แสดงผล (ต้องวัดพิกัดจริงจากจอคุณ)
REGION = {"top": 500, "left": 20, "width": 500, "height": 200}

# คำ/วลีที่ต้องการให้จับ (พิมพ์เล็กใหญ่ไม่สำคัญ)
TARGET_TEXTS = [
    "Secret",
    "Eternal",
    "Divine",
]

# Discord Webhook URL ของคุณ
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1543910120054984754/RL8sNW9h431pxEpHRJdGL62cpdAmN23nfZ6cDczTAHYTnFyz3uEBpQWi01Fh_khx72K2"

# ความถี่ในการสแกนจอ (วินาที)
CHECK_INTERVAL = 90

# จำนวนบรรทัดล่าสุดที่จะจำไว้ (กันไม่ให้แจ้งซ้ำ)
MAX_SEEN_LINES = 300

# =========================
# 🧠 ตัวแปรสถานะ (ไม่ต้องแก้)
# =========================

seen_lines_queue = deque(maxlen=MAX_SEEN_LINES)
seen_lines_set = set()


# =========================
# 📸 จับภาพหน้าจอ + OCR
# =========================

def capture_and_read(region):
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        text = pytesseract.image_to_string(img, lang="eng")
        return text


# =========================
# 🔍 เช็คบรรทัดใหม่ที่ยังไม่เคยเห็น
# =========================

def get_new_lines(current_text):
    lines = [line.strip() for line in current_text.split("\n") if line.strip()]
    new_lines = [line for line in lines if line not in seen_lines_set]
    return lines, new_lines


def update_seen(lines):
    for line in lines:
        if line not in seen_lines_set:
            if len(seen_lines_queue) == seen_lines_queue.maxlen:
                old = seen_lines_queue.popleft()
                seen_lines_set.discard(old)
            seen_lines_queue.append(line)
            seen_lines_set.add(line)


# =========================
# 🎯 เช็คว่าบรรทัดไหนตรงกับ keyword
# =========================

def check_matches_in_lines(lines, target_list):
    matches = []
    for line in lines:
        line_lower = line.lower()
        for target in target_list:
            if target.lower().strip() in line_lower:
                matches.append((target, line))
    return matches


# =========================
# 📩 ส่งข้อความไป Discord
# =========================

def send_discord_message(message):
    try:
        payload = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code not in (200, 204):
            print(f"⚠️ ส่งแจ้งเตือนล้มเหลว: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ เกิดข้อผิดพลาดตอนส่ง Discord: {e}")


# =========================
# 🔁 ลูปหลัก
# =========================

def main():
    print("🚀 เริ่มตรวจจับแชท Roblox... กด Ctrl+C เพื่อหยุด")
    while True:
        try:
            text = capture_and_read(REGION)
            all_lines, new_lines = get_new_lines(text)

            if new_lines:
                print(f"📥 บรรทัดใหม่: {new_lines}")
                matches = check_matches_in_lines(new_lines, TARGET_TEXTS)
                for target, line in matches:
                    print(f"✅ พบคำว่า '{target}' ในข้อความ: {line}")
                    send_discord_message(f"**พบคำว่า:** `{target}`\n**ข้อความ:** {line}")

            update_seen(all_lines)

        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
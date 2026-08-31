import mss
import mss.tools
import pytesseract
from PIL import Image
import time
import requests
import os
from dotenv import load_dotenv

# ============================================
# ⚙️ โหลดค่าจากไฟล์ .env
# ============================================

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TESSERACT_PATH = os.getenv("TESSERACT_PATH")

# ตรวจสอบว่าตั้งค่าครบไหม ก่อนรันจริง
if not DISCORD_WEBHOOK_URL or not TESSERACT_PATH:
    raise ValueError("❌ ไม่พบค่าตั้งค่าใน .env กรุณาสร้างไฟล์ .env และใส่ DISCORD_WEBHOOK_URL กับ TESSERACT_PATH ให้ครบ")

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# ============================================
# ⚙️ ตั้งค่าอื่นๆ (ไม่ใช่ความลับ ตั้งในโค้ดได้ปกติ)
# ============================================

# พื้นที่จับภาพ (REGION) — เลือกอันที่ตรงกับจอที่ Roblox เปิดอยู่
REGION = {"top": 0, "left": 0, "width": 960, "height": 250}
# ถ้า Roblox อยู่จอซ้าย (left เริ่มที่ -1920) ให้ comment บรรทัดบน แล้วเปิดบรรทัดนี้แทน
# REGION = {"top": 0, "left": -1920, "width": 960, "height": 250}

KEYWORDS = ["Secret", "Eternal", "Divine"]

DEBUG_MODE = True
CHECK_INTERVAL = 3
DEBUG_FOLDER = "debug_captures"

# ============================================
# 🔧 ฟังก์ชันหลัก
# ============================================

def send_discord_alert(message, image_path=None):
    """ส่งข้อความแจ้งเตือนไปที่ Discord webhook"""
    try:
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                files = {"file": f}
                data = {"content": message}
                requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)
        else:
            requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
        print(f"[DISCORD] ส่งแจ้งเตือนแล้ว: {message}")
    except Exception as e:
        print(f"[ERROR] ส่ง Discord ไม่สำเร็จ: {e}")


def capture_screen(region):
    """จับภาพหน้าจอตาม region ที่กำหนด คืนค่าเป็น PIL Image"""
    with mss.mss() as sct:
        sct_img = sct.grab(region)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img


def save_debug_image(img, index):
    """เซฟรูปที่จับได้ลงโฟลเดอร์ debug พร้อม timestamp"""
    if not os.path.exists(DEBUG_FOLDER):
        os.makedirs(DEBUG_FOLDER)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(DEBUG_FOLDER, f"capture_{timestamp}_{index}.png")
    img.save(filepath)
    return filepath


def check_keywords(text, keywords):
    """เช็คว่ามีคำในลิสต์ keyword อยู่ในข้อความที่ OCR อ่านได้ไหม"""
    text_lower = text.lower()
    found = [kw for kw in keywords if kw.lower() in text_lower]
    return found


# ============================================
# 🔁 ลูปหลักของบอท
# ============================================

def main():
    print("=" * 50)
    print("🤖 บอทเริ่มทำงานแล้ว")
    print(f"📍 REGION ที่ใช้: {REGION}")
    print(f"🔍 คำที่กำลังตามหา: {KEYWORDS}")
    print(f"🐞 Debug Mode: {'เปิด' if DEBUG_MODE else 'ปิด'}")
    print("=" * 50)

    round_count = 0

    while True:
        round_count += 1
        try:
            img = capture_screen(REGION)

            saved_path = None
            if DEBUG_MODE:
                saved_path = save_debug_image(img, round_count)
                print(f"\n[รอบที่ {round_count}] 📸 เซฟภาพไว้ที่: {saved_path}")

            text = pytesseract.image_to_string(img, lang="eng")

            if DEBUG_MODE:
                print("[OCR อ่านได้] " + "-" * 30)
                print(text if text.strip() else "(ไม่พบตัวอักษรใดๆ ในภาพ)")
                print("-" * 45)

            found_keywords = check_keywords(text, KEYWORDS)

            if found_keywords:
                alert_msg = f"🚨 พบคำที่ตามหา: {', '.join(found_keywords)}\nข้อความเต็ม: {text.strip()[:200]}"
                print(f"[แจ้งเตือน] {alert_msg}")
                send_discord_alert(alert_msg, saved_path)
            else:
                if DEBUG_MODE:
                    print("[สถานะ] ยังไม่พบคำที่ตามหาในรอบนี้")

        except Exception as e:
            print(f"[ERROR] เกิดข้อผิดพลาด: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
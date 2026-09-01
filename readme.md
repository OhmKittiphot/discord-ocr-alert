# Discord OCR Alert

โปรเจกต์นี้เป็น Python bot ที่จับภาพจากหน้าจอ แล้วอ่านข้อความด้วย OCR เพื่อค้นหา keyword ที่กำหนดไว้ เมื่อเจอข้อความที่ตรงกัน จะส่งข้อความแจ้งเตือนไปยัง Discord ผ่าน Webhook

> โค้ดนี้ถูกออกแบบให้ทำงานแบบวนลูปต่อเนื่อง เพื่อคอยตรวจจับข้อความบนหน้าจอแบบ real-time โดยมีการกรองข้อความซ้ำและตั้งเวลา cooldown เพื่อป้องกันการแจ้งเตือนซ้ำซ้อนมากเกินไป

## ภาพรวม

บอทนี้เหมาะสำหรับกรณีที่ต้องการตรวจจับข้อความที่ปรากฏบนหน้าจอ เช่น:

- แชทเกม
- หน้าต่างหรือข้อความที่แสดงอยู่บนจอ
- เมนูหรือข้อความแจ้งเหตุการณ์ที่ต้องการเฝ้าดู

กระบวนการทำงานมีดังนี้:

1. จับภาพจากพื้นที่หน้าจอที่กำหนด
2. แปลงภาพให้อยู่ในรูปแบบที่ OCR อ่านง่าย
3. ใช้ Tesseract OCR เพื่ออ่านข้อความ
4. ล้างข้อความที่ซ้ำกันและจัดรูปแบบ
5. ตรวจสอบว่าเจอ keyword ที่กำหนดหรือไม่
6. ถ้าพบ ให้ส่งข้อความไปยัง Discord Webhook

## คุณสมบัติ

- ตรวจจับบนหน้าจอแบบกำหนดพื้นที่ (screen region)
- ใช้ Tesseract OCR อ่านข้อความจากภาพ
- กรองข้อความที่ซ้ำเพื่อหลีกเลี่ยงการแจ้งเตือนซ้ำ
- ตรวจจับ keyword แบบ case-insensitive
- มี cooldown ระหว่างการแจ้งเตือนแต่ละ keyword
- ส่งข้อความแจ้งเตือนไปยัง Discord ผ่าน Webhook
- ไม่มีการส่งเสียง beep ในเวอร์ชันปัจจุบัน

## โครงสร้างไฟล์

- `bot.py` - ไฟล์หลักที่มี logic ทั้งหมด
- `requirements.txt` - รายการ dependency ที่ต้องติดตั้ง
- `.env` - ไฟล์เก็บค่า Tesseract path และ Discord Webhook URL
- `readme.md` - คู่มือการใช้งาน

## ข้อกำหนดเบื้องต้น

ก่อนใช้งาน ต้องมีดังนี้:

- Python 3.9 ขึ้นไป
- Tesseract OCR ติดตั้งบนเครื่องแล้ว
- Windows (เพราะโค้ดใช้ `ImageGrab` และกำหนด path สำหรับ Tesseract แบบ Windows)
- Discord Webhook URL สำหรับช่องที่ต้องการรับแจ้งเตือน

## การติดตั้ง

1. เปิด Terminal หรือ PowerShell ที่โฟลเดอร์โปรเจกต์
2. ติดตั้ง dependency

```bash
pip install -r requirements.txt
```

## การติดตั้ง Tesseract OCR

หากยังไม่มี Tesseract ให้ติดตั้งจากลิงก์นี้:

- https://github.com/UB-Mannheim/tesseract/wiki

ตรวจสอบว่าติดตั้งเรียบร้อยแล้วด้วยคำสั่ง:

```bash
tesseract --version
```

ถ้า Tesseract ไม่อยู่ใน PATH หรือคุณใช้เวอร์ชันที่ไม่ใช่ค่า default ให้ตั้งค่าใน `.env` เช่น:

```env
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url
```

> ถ้าไม่มี `TESSERACT_PATH` โปรแกรมจะพิมพ์ warning แต่ยังคงรันต่อได้ หาก OCR ไม่ทำงาน ให้ตั้งค่า path ให้ถูกต้อง

## การตั้งค่าเริ่มต้น

เปิดไฟล์ `bot.py` และปรับค่าด้านบนของไฟล์ให้ตรงกับสภาพแวดล้อมของคุณ:

```python
REGION = (0, 0, 1920, 540)
KEYWORDS = ["spawned in"]
CHECK_INTERVAL = 1
THRESHOLD = 150
DEBUG = False
COOLDOWN_SECONDS = 230
```

### 1) REGION

`REGION` คือพื้นที่บนหน้าจอที่ bot จะจับภาพและ OCR

รูปแบบ:

```python
REGION = (left, top, width, height)
```

ตัวอย่าง:

```python
REGION = (0, 0, 1920, 540)
```

> ควรตั้งค่าให้ครอบคลุมเฉพาะบริเวณที่ต้องการตรวจจับเท่านั้น เพื่อให้ OCR แม่นยำและลดการแจ้งเตือนผิดพลาด

### 2) KEYWORDS

```python
KEYWORDS = ["spawned in"]
```

สามารถเพิ่มคำหรือวลีที่ต้องการตรวจจับได้ เช่น:

```python
KEYWORDS = ["spawned in", "rare", "legendary", "egg"]
```

คำทั้งหมดจะถูกเปรียบเทียบแบบไม่สนใจตัวพิมพ์เล็ก/ใหญ่

### 3) CHECK_INTERVAL

```python
CHECK_INTERVAL = 1
```

หมายถึงช่วงเวลาที่ bot สแกนหน้าจอในแต่ละรอบ หน่วยเป็นวินาที

### 4) THRESHOLD

```python
THRESHOLD = 150
```

ใช้ในการแปลงภาพเป็นภาพขาว-ดำก่อน OCR หากค่าเกินไปหรือต่ำเกินไป อาจทำให้ OCR อ่านข้อความผิดได้

### 5) COOLDOWN_SECONDS

```python
COOLDOWN_SECONDS = 230
```

เวลา cooldown ในหน่วยวินาที เพื่อป้องกันการแจ้งเตือนซ้ำจาก keyword เดียวกันในช่วงเวลาสั้น ๆ

## การตั้งค่า Environment Variables

สร้างไฟล์ `.env` ในโฟลเดอร์โปรเจกต์แล้วใส่ค่าเช่นนี้:

```env
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url_here
```

> ควรเก็บ Webhook URL เป็นความลับ อย่าเผยแพร่ต่อสาธารณะ เพราะคนอื่นสามารถส่งข้อความเข้าช่องของคุณได้

## การใช้งาน

รันโปรเจกต์ด้วยคำสั่ง:

```bash
python bot.py
```

จากนั้นบอทจะเริ่มทำงานและตรวจจับข้อความไปเรื่อย ๆ หากต้องการหยุด ให้กด:

```bash
Ctrl + C
```

## การตรวจสอบ debug

ถ้าต้องการดูข้อความ OCR ที่อ่านได้แบบละเอียด ให้ตั้งค่า:

```python
DEBUG = True
```

เมื่อเปิด debug แล้ว โปรแกรมจะแสดงข้อความที่ OCR อ่านได้ในแต่ละรอบ เช่น บรรทัดที่พบหรือข้อความที่ถูกกรองแล้ว

## วงจรการทำงาน

1. Grab ภาพจากพื้นที่หน้าจอที่กำหนด
2. ประมวลผลภาพให้เหมาะกับ OCR
3. อ่านข้อความด้วย Tesseract
4. ล้างข้อความซ้ำและทำความสะอาด
5. ตรวจหา keyword ที่ตรงตามกฎ
6. ถ้าพบและยังไม่เกิน cooldown ให้ส่งแจ้งเตือนไป Discord

## ปัญหาที่พบบ่อย

### OCR อ่านผิด หรืออ่านไม่ออก

- ปรับค่า `REGION` ให้สั้นลงและตรงจุดที่ต้องการมากขึ้น
- ปรับค่า `THRESHOLD` ให้เหมาะสม
- ตรวจสอบว่าหน้าจอมีความคมชัดและสว่างเพียงพอ
- ใช้ฟอนต์หรือธีมที่อ่านง่าย

### ไม่ส่งข้อความไป Discord

- ตรวจสอบว่า `.env` มี `DISCORD_WEBHOOK_URL` ถูกต้อง
- ตรวจสอบว่า webhook ยังใช้งานได้
- ดู error message ที่ terminal หรือ command prompt

### แจ้งเตือนซ้ำมากเกินไป

- ปรับค่า `COOLDOWN_SECONDS` ให้สูงขึ้น
- ปรับ `KEYWORDS` ให้เฉพาะเจาะจงขึ้น
- ตรวจสอบว่าข้อความ OCR อาจอ่านซ้ำหรืออ่านผิดบ่อย

### ไม่พบ Tesseract

- ตรวจสอบว่า Tesseract ติดตั้งจริง
- ตรวจสอบว่า path ใน `.env` ถูกต้อง
- รันคำสั่ง `tesseract --version` เพื่อยืนยัน

## ข้อควรระวัง

- โค้ดนี้ใช้ OCR กับภาพหน้าจอแบบ real-time จึงอาจมีความผิดพลาดได้จากแสง สี ตัวอักษร หรือความละเอียดบนหน้าจอ
- ควรใช้เฉพาะในระบบหรือแอปพลิเคชันที่คุณมีสิทธิ์ใช้งานเท่านั้น
- Webhook URL เป็นข้อมูลที่ละเอียดอ่อน ควรเก็บเป็นความลับ
- หากต้องการลดเสียงรบกวนให้ชัดเจน ให้ปรับ `KEYWORDS` และ `COOLDOWN_SECONDS` ให้เหมาะสมกับกรณีใช้งาน

## ตัวอย่างการตั้งค่าแบบใช้งานจริง

```python
REGION = (0, 0, 1920, 540)
KEYWORDS = ["spawned in", "rare", "epic"]
CHECK_INTERVAL = 1
THRESHOLD = 150
DEBUG = False
COOLDOWN_SECONDS = 230
```

```env
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxxxxxxx
```




from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests

# ==========================================
# تنظیمات تلگرام
TELEGRAM_TOKEN = "توکن_ربات_خود_را_اینجا_بگذارید"
CHAT_ID = "آیدی_عددی_خود_را_اینجا_بگذارید"
# ==========================================

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Error sending msg: {e}")

# تنظیمات مرورگر
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

print(">>> شروع ربات برای کدهای ۰ تا ۹ ...")

# لیست کدهایی که باید چک شوند (از ۰ تا ۹)
target_codes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

for code in target_codes:
    print(f"\n🔵 در حال پردازش کد {code} ...")
    
    found_count = 0
    # تیتر گزارش برای هر کد
    message_buffer = f"💎 **گزارش ۱۰ سیم‌کارت ارزان کد {code}**\n➖➖➖➖➖➖➖➖\n"
    
    try:
        # ساخت لینک اختصاصی برای هر کد
        url = f"https://rond.ir/s?numberArrayParam=%5B%22{code}%22,null,null,null,null,null,null%5D&simCardNumberPreCodes=%5B%220912%22%5D&activeTab=ALL"
        
        driver.get(url)
        time.sleep(10) # صبر برای لود کامل

        # کلیک روی ارزان‌ترین
        try:
            sort_button = driver.find_element(By.XPATH, "//*[contains(text(), 'ارزان‌ترین')]")
            driver.execute_script("arguments[0].click();", sort_button)
            print(f"   > فیلتر ارزان‌ترین کد {code} زده شد.")
            time.sleep(10) # صبر برای لود لیست جدید
        except:
            print(f"   ! دکمه پیدا نشد (ادامه با پیش‌فرض)")

        rows = driver.find_elements(By.TAG_NAME, "tr")
        
        for row in rows:
            try:
                # استخراج شماره
                number_el = row.find_elements(By.CSS_SELECTOR, ".mw-220px")
                if not number_el: continue
                number = number_el[0].text.strip()
                
                # استخراج متن کل ردیف برای تحلیل
                row_text = row.text
                
                # 1. پیدا کردن وضعیت (صفر / کارکرده)
                status = "نامشخص"
                if "کارکرده" in row_text: status = "کارکرده"
                elif "صفر" in row_text: status = "صفر"
                elif "در حد صفر" in row_text: status = "در حد صفر"
                
                # 2. پیدا کردن شرایط (نقد / اقساط)
                try:
                    raw_condition = row.find_element(By.CSS_SELECTOR, ".d-xl-table-cell").text.strip()
                    # حذف تکرار (مثلا: نقد نقد -> نقد)
                    parts = raw_condition.split()
                    condition = parts[0] if len(parts) > 0 else "---"
                except:
                    condition = "---"
                
                # 3. پیدا کردن قیمت
                price = "توافقی"
                lines = row_text.split('\n')
                for line in lines:
                    # قیمت معمولا عددی است که ویرگول دارد و طولانی است
                    if "," in line and len(line) > 3 and any(char.isdigit() for char in line):
                        price = line + " تومان"
                        break
                
                # --- ساخت خروجی ۴ خطی ---
                item_text = (
                    f"📱 {number}\n"
                    f"💰 {price}\n"
                    f"📦 {status}\n"
                    f"🛒 {condition}\n"
                    f"➖➖➖➖➖\n"
                )
                
                message_buffer += item_text
                found_count += 1
                print(f"   + {number} استخراج شد.")
                
                # محدودیت دقیق ۱۰ عدد
                if found_count >= 10:
                    break

            except Exception as inner:
                continue
        
        # ارسال پیام به تلگرام (اگر موردی پیدا شد)
        if found_count > 0:
            send_telegram_message(message_buffer)
        else:
            print(f"   - هیچ موردی برای کد {code} یافت نشد.")

    except Exception as e:
        print(f"❌ خطا در کد {code}: {e}")

    # --- استراحت بین کدها (جلوگیری از بلاک) ---
    if code != target_codes[-1]: # اگر کد آخر نیست
        print(">>> ⏳ ۴۵ ثانیه استراحت ...")
        driver.delete_all_cookies() # پاک کردن ردپا
        time.sleep(45)

print("✅ پایان کار ربات.")
driver.quit()

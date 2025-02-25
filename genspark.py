import re
import time
import random
import requests
import phonenumbers
from faker import Faker
from phonenumbers import PhoneNumberFormat
from playwright.sync_api import sync_playwright

INVITE_URL = "https://www.genspark.ai/invite?invite_code=OWViODRiNDhMYTRhZkw4YTc0TDlkYWFMNDgwNDI5NjA4ZDM3"
DOMAIN = "https://api.mail.cx/api/v1"
DEFAULT_PASSWORD = "ZXCvbnm0987###"
COUNTRY_CODES = ["1", "86", "81", "82", "44", "33", "49", "39", "7", "61"]

def generate_valid_phone_number(country_code):
    try:
        region_code = phonenumbers.region_code_for_country_code(int(country_code.replace('+', '')))
        example_number = phonenumbers.example_number_for_type(region_code, phonenumbers.PhoneNumberType.MOBILE)
        if not example_number:
            raise ValueError(f"No example mobile number found for country code {country_code}")
        formatted_number = phonenumbers.format_number(example_number, PhoneNumberFormat.NATIONAL)
        digits_only = ''.join(filter(str.isdigit, formatted_number))
        prefix = digits_only[:-4]
        remaining_digits = ''.join(str(random.randint(0, 9)) for _ in range(4))
        return prefix + remaining_digits
    except Exception as e:
        raise ValueError(f'Error generating valid phone number for country code {country_code}: {str(e)}')

def generate_name():
    fake = Faker('en_US')
    while True:
        name = fake.name().replace(' ', '_')
        if len(name) <= 10:
            return name

def get_auth():
    url = f"{DOMAIN}/auth/authorize_token"
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer undefined',
    }
    response = requests.post(url, headers=headers)
    return str(response.json())

def get_mail_address():
    return f"{generate_name()}@nqmo.com"

def get_mail_id(address, auth):
    url = f"{DOMAIN}/mailbox/{address}"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {auth}',
    }
    response = requests.get(url, headers=headers)
    body = response.json()
    return body[0]['id'] if body and body[0]['id'] else None

def setup_browser_context(playwright):
    browser = playwright.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security", 
            "--disable-features=IsolateOrigins,site-per-process"
        ]
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        java_script_enabled=True
    )
    return browser, context

def register(invite_url):
    with sync_playwright() as p:
        browser, context = setup_browser_context(p)
        page = context.new_page()
        
        # 反检测
        page.add_init_script("""
            Object.defineProperties(navigator, {
                'webdriver': { get: () => undefined },
                'language': { get: () => 'zh-CN' },
                'platform': { get: () => 'Win32' },
                'userAgent': { get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36' }
            });
        """)

        # 打开邀请链接
        page.goto(invite_url, wait_until="networkidle", timeout=100000000)
        print("[+]打开邀请链接")
        
        # 点击按钮
        page.get_by_text("领取会员权益").click()
        page.get_by_text("Login with email").click()
        page.get_by_text("Sign up now").click()
        print("[+]开始注册")

        # 邮箱验证
        auth = get_auth()
        email = get_mail_address()
        page.fill('xpath=//*[@id="email"]', email)
        print(f"[+]邮箱地址: {email}")
        page.get_by_text("Send verification code").click()
        page.wait_for_selector('xpath=//*[@id="emailVerificationCode"]')

        # 获取邮箱验证码
        id_ = None
        while id_ is None:
            id_ = get_mail_id(email, auth)
            
        url = f"{DOMAIN}/mailbox/{email}/{id_}"
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {auth}',
        }
        body = requests.get(url, headers=headers).json()["body"]["text"]
        if match := re.search(r"Your code is: \s*(\d+)\s*", body):
            verification_code = match.group(1)
            print(f"[+]验证码: {verification_code}")

        # 完成注册
        page.fill('xpath=//*[@id="emailVerificationCode"]', verification_code)
        page.get_by_text("Verify code").click()
        page.fill('xpath=//*[@id="newPassword"]', DEFAULT_PASSWORD)
        page.fill('xpath=//*[@id="reenterPassword"]', DEFAULT_PASSWORD)
        page.get_by_text("Create").click()
        print("[+]注册成功，开始填写手机号")
        time.sleep(10)

        # 电话验证
        country_code = random.choice(COUNTRY_CODES)
        phone_number = generate_valid_phone_number(country_code)
        print(f"[+]电话号码: +{country_code} {phone_number}")
        
        phone_input = page.locator('input.vti__input')
        phone_input.fill(f"+{country_code} {phone_number}")

        # 获取短信验证码
        with page.expect_response(lambda r: "api/phone/sms_send_verification" in r.url) as response_info:
            page.click('button.row4_button:has-text("获取验证码")')
            
        response = response_info.value
        if response.ok:
            data = response.json()
            print('data', data)
            print(f"手机验证码：{data['code']}")
            
        time.sleep(2)
        
        # 完成电话验证
        verification_code = page.locator('#verification_code')
        verification_code.fill(data['code'])
        
        # 领取会员权益
        page.wait_for_selector("button.row4_button", state="visible", timeout=5000)
        time.sleep(2)
        page.click("button.row4_button:has-text('领取会员权益')")
        print("领取成功")
        page.wait_for_timeout(1000)

        browser.close()

if __name__ == "__main__":
    for _ in range(20):
        register(INVITE_URL)
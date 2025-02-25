import cloudscraper

def get_random_mail():
    url = "https://22.do/action/mailbox/random"
    payload = {"type": "random"}
    headers = {
        "Content-Type": "application/json"
    }
    
    scraper = cloudscraper.create_scraper()
    response = scraper.post(url, json=payload, headers=headers)
    response.encoding = "utf-8"
    
    try:
        response.raise_for_status()
        data = response.json()
        return data['data']['email']
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        print(f"Response content: {response.text}")
        raise

def get_message(mail, lasttime=0):
    url = "https://22.do/action/mailbox/message"
    payload = {"email": mail, "lastime": lasttime}
    headers = {
        "Content-Type": "application/json"
    }
    
    scraper = cloudscraper.create_scraper()
    response = scraper.post(url, json=payload, headers=headers)
    response.encoding = "utf-8"
    
    try:
        response.raise_for_status()
        return response.json()
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        print(f"Response content: {response.text}")
        raise

# 调用方法
result = get_random_mail()
print(result)

# r = get_message("im9slfv@usdtbeta.com")
# print(r)
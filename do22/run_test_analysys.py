import cloudscraper

# 创建 cloudscraper 对象
scraper = cloudscraper.create_scraper()

# 请求的 URL
url = "https://analysys.simitalk.com/api/v1/data"

# 请求的 Headers
headers = {
    "dateTime": "1736848484269",
    "sendType": "9",
    "zoneCode": "Asia/Shanghai",
    "zoneTime": "utc+8",  # 注意这里不用 URL 编码
    "hashKey": "4749a77a7dfa3fcc91a818a539d9eba4bab990b0e584646825b9a44ec5b0fb86",
    "sign": "a2242889ea54f587aacf45c23805d244"
    ,
    "Content-Type": "application/json"
    ,
    "User-Agent": "xxx.....Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}

# 请求的 Body 数据（JSON 格式）
data = {
    "dataEncrypt": "/pdUy2WKzWVW6Cvygbh62rPMwq38aM6Lf7vFVqEjrIw="
}

# 发送 POST 请求
response = scraper.post(url, headers=headers, json=data)

# 输出返回结果
print(response.status_code)
print(response.text)
import cloudscraper
scraper = cloudscraper.create_scraper()

url='https://22.do/inbox'
response = scraper.get(url)
response.encoding = "utf-8"

print(response.text)
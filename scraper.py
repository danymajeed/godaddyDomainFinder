import json
import math
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

driver.get("https://www.godaddy.com//domainsearch/find")
domain_text_box = driver.find_element_by_id('domain-search-box')
domains = {}
namesList = []
progress = 0
file = open("names.txt", "r")
for x in file:
    name = re.sub(r'[^A-Za-z0-9]', '', x)
    namesList.append(name.lower())

with open('exports/domains.json') as json_file:
    file = json_file.read()
    if file:
        domains = json.loads(file)

for index, name in enumerate(namesList):
    if name + '.com' not in domains:
        price = None
        status = "Available"
        domain_text_box.send_keys(Keys.CONTROL + "a")
        domain_text_box.send_keys(Keys.DELETE)
        domain_text_box.send_keys(name)
        domain_text_box.send_keys(Keys.ENTER)
        time.sleep(5)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')

        site_avilability = soup.find('span', class_='domain-name-text')
        site_avilability1 = soup.find('div', {'data-cy': 'celebrate-exact-match-title'})
        domain_type = soup.find('span', class_='exact-header-tag')

        if domain_type is not None:
            status = domain_type.text

        if site_avilability1 is not None and site_avilability1.text == 'Your domain is available!':
            price = soup.select('div[data-cy=celebrate-exact-match-pricing] > span')[1].getText()
            price = int(price.replace('₨', '').replace(',', ''))

        elif (site_avilability is not None and site_avilability.text == name + '.com is available'):
            price = soup.find('span', {'data-cy': 'exact-match-price-main'}).text
            price = int(price.replace('₨', '').replace(',', ''))

        if price is None:
            status = 'Not Available'

        name = name + '.com'
        domains[name] = {
                'status': status,
                'price': price,
            }

        with open('exports/domains.json', 'w') as outfile:
            json.dump(domains, outfile)
    
    progress = math.floor(((index + 1) * 100) / len(namesList))
    print(str(progress) + "%")
    
driver.close()

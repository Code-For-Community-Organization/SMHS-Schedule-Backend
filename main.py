from bs4 import BeautifulSoup
from selenium import webdriver
import time
import json
import re
import requests



driver = webdriver.Chrome("/Users/jevonmao/Git_directory/Aeries-scraping/chromedriver")
url = "https://my.iusd.org/"
driver.get(url)

username = driver.find_element_by_id("portalAccountUsername")
password = driver.find_element_by_id("portalAccountPassword")

username.send_keys("jevkevceo@gmail.com")
nextItem = driver.find_element_by_id("next")
nextItem.click()
password.send_keys("511969")

driver.find_element_by_id("LoginButton").click()
time.sleep(5)
cookies = driver.get_cookies()

indexa = cookies.index('_pk_id')
print(indexa)
sessionid=cookies[3]['value']
aereisnet=cookies[1]['value']
pk_id=cookies[indexa]['value']
print(pk_id)
PARAMS ={
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'en-US,en;',
'Connection': 'keep-alive',
'Cookie': 'AeriesNet='+aereisnet+';'+'ASP.NET_SessionId='+sessionid+';'+'_pk_id.1.95d3='+pk_id,
'Host': 'my.iusd.org',
'Sec-Fetch-Dest': 'document',
'Sec-Fetch-Mode': 'navigate',
'Sec-Fetch-Site': 'none',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
'X-Requested-With': 'XMLHttpRequest'
}


URL = " https://my.iusd.org/Widgets/ClassSummary/GetClassSummary?IsProfile=True"
r = requests.get(url = URL, params = PARAMS) 

print(r.text)

'ASP.NET_SessionId=wcyarn3lbyyngbcmtbldbyr3; AeriesNet=LastSC_0=501&LastSN_0=5125&LastID_0=169160019; _pk_id.1.95d3=8e2458f3afe66422.1588987408.1.1588987408.1588987408.; _pk_ses.1.95d3=1'

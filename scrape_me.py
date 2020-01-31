from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import sys
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time

ua = UserAgent() # From here we generate a random user agent
proxies = [] # Will contain proxies [ip, port]


def init_chrome_driver(proxy):
    selenium_grid_url = "0.0.0.0:4444/wd/hub"
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("window-size=1920x1080")
    options.add_argument("disable-gpu")
    options.add_argument(f"--user-agent={ua.random}")
    options.add_experimental_option("prefs", {"intl.accept_languages": "ko_KR"})
    options.add_argument("lang=ko_KR")
    options.add_argument(f'--proxy-server={proxy}')
    chromeDriver = webdriver.Remote(command_executor=selenium_grid_url, options=options)
    return chromeDriver
    
def main(mode):
  proxies_req = Request('https://www.sslproxies.org/')
  proxies_req.add_header('User-Agent', ua.random)
  proxies_doc = urlopen(proxies_req).read().decode('utf8')

  soup = BeautifulSoup(proxies_doc, 'html.parser')
  proxies_table = soup.find(id='proxylisttable')

  # Save proxies in the array
  for row in proxies_table.tbody.find_all('tr'):
    proxies.append({
      'ip':   row.find_all('td')[0].string,
      'port': row.find_all('td')[1].string
    })

  # Choose a random proxy

  if mode == 'selenium':
    selenium_ip_check(proxies)
  elif mode == 'urllib':
    urllib_ip_check(proxies)
  else:
    print('no option')

def selenium_ip_check(proxies):
  for n in range(1, 15):
    proxy_index = random_proxy()
    proxy = proxies[proxy_index]
    proxy_target = proxy['ip'] + ':' + proxy['port']
    driver = init_chrome_driver(proxy_target)
    # Every 10 requests, generate a new proxy
    if n % 5 == 0:
      proxy_index = random_proxy()
      proxy = proxies[proxy_index]

    # Make the call
    try:
      driver.get('http://www.naver.com')
      print(f'proxy ip : { proxy_target} real ip : {driver.page_source}')
    except Exception as e: # If error, delete this proxy and find another one
      print(e)
      del proxies[proxy_index]
      print('Proxy ' + proxy['ip'] + ':' + proxy['port'] + ' deleted.')
      proxy_index = random_proxy()
      proxy = proxies[proxy_index]

    driver.close()

def urllib_ip_check(proxies):
  proxy_index = random_proxy()
  proxy = proxies[proxy_index]
  for n in range(1, 5):
    req = Request('https://www.naver.com')
    req.set_proxy(proxy['ip'] + ':' + proxy['port'], 'https')

    # Every 10 requests, generate a new proxy
    if n % 5 == 0:
      proxy_index = random_proxy()
      proxy = proxies[proxy_index]

    # Make the call
    try:
      my_ip = urlopen(req).read().decode('utf8')
      print('#' + str(n) + ': ' + my_ip)
    except Exception as e: # If error, delete this proxy and find another one
      print(e)
      del proxies[proxy_index]
      print('Proxy ' + proxy['ip'] + ':' + proxy['port'] + ' deleted.')
      proxy_index = random_proxy()
      proxy = proxies[proxy_index]

# Retrieve a random index proxy (we need the index to delete it if not working)
def random_proxy():
  return random.randint(0, len(proxies) - 1)

if __name__ == '__main__':
  main(mode=sys.argv[1])

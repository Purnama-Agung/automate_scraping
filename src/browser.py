import undetected_chromedriver as uc
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from src.proxies import get_proxy
from lib.logger import Logger

logger = Logger('Browser')

def get_browser_chrome(proxy=False, files=None):
    address = port = None
    if proxy:
        item = get_proxy(files=files)
        address = item['address']
        port = int(item['port'])
        logger.log(f'Trying with proxy {address}:{port}')

    logger.log('Start chrome browser')
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--dns-prefetch-disable')

    # For ChromeDriver version 79.0.3945.16 or over
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    capabilities = dict(DesiredCapabilities.CHROME)
    if not "chromeOptions" in capabilities:
        capabilities['chromeOptions'] = {
            'args': [],
            'binary': "",
            'extensions': [],
            'prefs': {}
        }
    capabilities['proxy'] = {
        'httpProxy': '{}:{}'.format(address, port),
        "ftpProxy": '{}:{}'.format(address, port),
        "sslProxy": '{}:{}'.format(address, port),
        'noProxy': None,
        'proxyType': "MANUAL",
        'class': "org.openqa.selenium.Proxy",
        'autodetect': False
    }

    browser = uc.Chrome(options=chrome_options, desired_capabilities=capabilities)
    browser.execute_script('return navigator.webdriver')
    browser.maximize_window()
    return browser

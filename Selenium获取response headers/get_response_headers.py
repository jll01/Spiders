import json
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def get_log_response_headers(url):
    caps = DesiredCapabilities.CHROME
    caps['loggingPrefs'] = {
        'browser': 'ALL',
        'performance': 'ALL',
    }
    caps['perfLoggingPrefs'] = {
        'enableNetwork': True,
        'enablePage': False,
        'enableTimeline': False
    }

    option = webdriver.ChromeOptions()
    option.add_argument('--no-sandbox')
    # option.add_argument('--headless')
    option.add_argument("--disable-extensions")
    option.add_argument("--allow-running-insecure-content")
    option.add_argument("--ignore-certificate-errors")
    option.add_argument("--disable-single-click-autofill")
    option.add_argument("--disable-autofill-keyboard-accessory-view[8]")
    option.add_argument("--disable-full-form-autofill-ios")
    option.add_experimental_option('w3c', False)
    option.add_experimental_option('perfLoggingPrefs', {
        'enableNetwork': True,
        'enablePage': False,
    })

    driver = webdriver.Chrome(options=option, desired_capabilities=caps)
    driver.get(url)
    time.sleep(20)
    for typelog in driver.log_types:
        perfs = driver.get_log(typelog)
        for row in perfs:
            try:
                log_data = row
                log_json = json.loads(log_data['message'])
                log = log_json['message']
            except:
                pass
            else:
                if log['method'] == 'Network.responseReceivedExtraInfo':
                    # print(log)
                    try:
                        accessToken = log['params']['headers']['accessToken']
                    except:
                        pass
                    else:
                        if accessToken:
                            print(f'accessToken is {accessToken}')
                            driver.quit()
                            return accessToken


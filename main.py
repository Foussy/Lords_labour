from selenium import webdriver
from python_anticaptcha import AnticaptchaClient, ImageToTextTask
import requests
import xml.etree.ElementTree as ET
import app

def open_chromepage(chromdriver_path):
    """ ouverture de Chromium sur LordsWM.com """
    try:
        url = "https://www.lordswm.com/"
        browser = webdriver.Chrome(chromdriver_path)
        browser.get(url)
        return browser
    except Exception as error:
        print(error)


def login_homepage(browser, login, password):
    """ connexion à la home page """
    try:
        login_textbox = browser.find_element_by_name('login')
        login_textbox.send_keys(login)

        password_textbox = browser.find_element_by_name('pass')
        password_textbox.send_keys(password)

        login_but_url = '/html/body/form/table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[1]/table[2]/tbody/tr/td/div/input'
        login_button = browser.find_element_by_xpath(login_but_url)
        login_button.click()
    except Exception as error:
        print(error)


def player_region(browser, character_page_url):
    browser.get(character_page_url)
    location_xpath = '/html/body/center/table/tbody/tr/td/table[1]/tbody/tr[2]/td[3]/table/tbody/tr[3]/td/a'
    location = browser.find_element_by_xpath(location_xpath)
    return location.text


def load_locations(location):
    tree = ET.parse('map.xml')
    prod_sites, machin_sites, mines_sites = [], [], []

    for url in tree.findall('region[@name="' + location + '"]/production/site/url'):
        prod_sites.append(str(url.text))

    for url in tree.findall('region[@name="' + location + '"]/machining/site/url'):
        machin_sites.append(str(url.text))

    for url in tree.findall('region[@name="' + location + '"]/mining/site/url'):
        mines_sites.append(str(url.text))

    return prod_sites, machin_sites, mines_sites


def find_location_to_work(browser, list_url):
    for url in list_url:
        try:
            browser.get(url)
            time.sleep(0.5)
            img_url = '/html/body/center/table/tbody/tr/td/table/tbody/tr/td/form[2]/table/tbody/tr[2]/td[1]/img'
            captcha_img = browser.find_element_by_xpath(img_url)
            return url
        except:
            continue
    return False


def download_captcha(browser, url, captcha_filepath):
    """ téléchargement du captcha """
    try:
        browser.get(url)
        img_url = '/html/body/center/table/tbody/tr/td/table/tbody/tr/td/form[2]/table/tbody/tr[2]/td[1]/img'
        captcha_img = browser.find_element_by_xpath(img_url)
        src = captcha_img.get_attribute('src')
        img = requests.get(src)
        with open(captcha_filepath, 'wb') as f:
            f.write(img.content)
        return captcha_filepath
    except Exception as error:
        print(error)


def solve_captcha(filepath):
    """ résolution du captcha """
    try:
        api_key = '7efb4f91db0301564967acb3ebde07f9'
        captcha_fp = open(filepath, 'rb')
        client = AnticaptchaClient(api_key)
        task = ImageToTextTask(captcha_fp)
        job = client.createTask(task)
        job.join()
        return job.get_captcha_text()
    except Exception as error:
        print(error)


def send_captcha(browser, code):
    """ envoi de la solution dans la page Chrome """
    try:
        txt_box_url = '/html/body/center/table/tbody/tr/td/table/tbody/tr/td/form[2]/table/tbody/tr[2]/td[2]/input[1]'
        captcha_textbox = browser.find_element_by_xpath(txt_box_url)
        captcha_textbox.send_keys(code)

        valid_but_url = '/html/body/center/table/tbody/tr/td/table/tbody/tr/td/form[2]/table/tbody/tr[2]/td[2]/input[7]'
        validate_button = browser.find_element_by_xpath(valid_but_url)
        validate_button.click()
    except Exception as error:
        print(error)


def check_enrollment(browser):
    condition_url = '/html/body/center/table/tbody/tr/td/center[1]'
    condition = browser.find_element_by_xpath(condition_url)
    if condition.text == 'You have successfully enrolled.':
        print("Enrolled Successfully : ", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return True
    else:
        print("Enrollment failed - wrong code : ", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return False


if __name__ == '__main__':
    App = app.Application()

from selenium import webdriver
from python_anticaptcha import AnticaptchaClient, ImageToTextTask

from datetime import datetime
import requests
import tkinter
import xml.etree.ElementTree as ET


class Application(object):
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('LordsWM Enroller')
        self.root.geometry("300x80")

        tkinter.Label(self.root, text="Login :").grid(row=0, column=0)
        self.login_entree = tkinter.Entry(self.root, width=20)
        self.login_entree.grid(row=0, column=1, columnspan=2)

        tkinter.Label(self.root, text="Password :").grid(row=1, column=0)
        self.passw_entree = tkinter.Entry(self.root, width=20)
        self.passw_entree.grid(row=1, column=1, columnspan=2)

        tkinter.Button(self.root, text='Launch', command=combine_funcs(self.start_enroll, self.enroll)) \
            .grid(row=2, column=1)
        tkinter.Button(self.root, text='Stop', command=self.stop_enroll) \
            .grid(row=2, column=2)

        self.menuBar = tkinter.Menu(self.root)

        self.menuOptions = tkinter.Menu(self.menuBar, tearoff=0)
        self.menuOptions.add_command(label="Parameters", command=self.parameters_window)
        self.menuBar.add_cascade(label="options", menu=self.menuOptions)

        self.menuHelp = tkinter.Menu(self.menuBar, tearoff=0)
        self.menuHelp.add_command(label="About", command=self.parameters_window)
        self.menuBar.add_cascade(label="Help", menu=self.menuHelp)
        self.root.config(menu=self.menuBar)

        self.chromedriver_path = '/usr/lib/chromium-browser/libs/chromedriver'
        self.captcha_filepath = '/home/pi/Pictures/captcha.jpeg'
        self.character_page_url = 'https://www.lordswm.com/pl_info.php?id=4552704'

        self.enroll_state = False
        self.timer = 1000
        self.root.mainloop()

    def stop_enroll(self):
        self.enroll_state = False
        print('programm pause : {0}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    def start_enroll(self):
        self.enroll_state = True
        print('programm resume : {0}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    def enroll(self):
        if self.enroll_state:

            chromepage = open_chromepage(self.chromedriver_path)
            try:
                login_homepage(chromepage, self.login_entree.get(), self.passw_entree.get())
                region = player_region(chromepage, self.character_page_url)
                prod_sites, machin_sites, mines_sites = load_locations(region)
                url = find_location_to_work(chromepage, prod_sites)
                if not url:
                    url = find_location_to_work(chromepage, machin_sites)
                    if not url:
                        url = find_location_to_work(chromepage, mines_sites)
                captcha_filepath = download_captcha(chromepage, url, self.captcha_filepath)
                code = solve_captcha(captcha_filepath)
                send_captcha(chromepage, code)
                if check_enrollment(chromepage):
                    self.timer = 3600 * 1000
                else:
                    self.timer = 1200 * 1000
            except Exception as Error:
                print(Error)
                self.timer = 1200 * 1000
            finally:
                chromepage.quit()
                self.root.after(self.timer, self.enroll)

    def parameters_window(self):
        print(self.chromedriver_path)
        print(self.captcha_filepath)
        print(self.character_page_url)


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


def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combined_func


if __name__ == '__main__':
    App = Application()

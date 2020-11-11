import tkinter
import time

def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)

    return combined_func

class Application(object):
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('LordsWM Enroller')

        ########## logins frame ##########
        self.frame_logins = tkinter.Frame(self.root, highlightbackground="black", highlightthickness=0, bd=10)
        self.frame_logins.grid(row=0, column=0)

        tkinter.Label(self.frame_logins, text="Login :").grid(row=0, column=0)
        self.login_entree = tkinter.Entry(self.frame_logins, width=20)
        self.login_entree.grid(row=0, column=1)

        tkinter.Label(self.frame_logins, text="Password :").grid(row=1, column=0)
        self.passw_entree = tkinter.Entry(self.frame_logins, width=20)
        self.passw_entree.grid(row=1, column=1)
        ##############################

        ########## enroll frame ##########
        self.frame_enroll = tkinter.Frame(self.root, highlightbackground="black", highlightthickness=0, bd=10)
        self.frame_enroll.grid(row=0, column=1)

        tkinter.Button(self.frame_enroll, text="Launch", command=combine_funcs(self.start_enroll, self.enroll)) \
            .grid(row=0, column=0)
        tkinter.Button(self.frame_enroll, text="Stop", command=self.stop_enroll) \
            .grid(row=0, column=1)

        tkinter.Label(self.frame_enroll, text="Next enroll in :").grid(row=1, column=0)
        self.timer_label = tkinter.Label(self.frame_enroll, text="--:--:--", font=('Helvetica', 10), fg='red')
        self.timer_label.grid(row=1, column=1)
        ##############################

        ########## filepaths ##########
        self.frame_filepath = tkinter.Frame(self.root, highlightbackground="black", highlightthickness=1, bd=10)
        self.frame_filepath.grid(row=1, column=0, columnspan=2)

        self.chromedriver_path = '/usr/lib/chromium-browser/libs/chromedriver'
        # self.chromedriver_path = 'C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe'
        self.chromedriver_path_var = tkinter.StringVar(self.root, value=self.chromedriver_path)

        self.captcha_filepath = '/home/pi/Pictures/captcha.jpeg'
        # self.captcha_filepath = 'C:/Users/Foussy/Pictures/LordsWM_captchas/captcha.jpeg'
        self.captcha_filepath_var = tkinter.StringVar(self.root, value=self.captcha_filepath)

        # self.character_page_url = 'https://www.lordswm.com/pl_info.php?id=5526781'
        self.character_page_url = 'https://www.lordswm.com/pl_info.php?id=5526781'
        self.character_page_url_var = tkinter.StringVar(self.root, value=self.character_page_url)
        ##############################

        self.enroll_state = False
        self.static_timer = 0
        self.countdown = 0
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
                url_list = prod_sites + machin_sites + mines_sites
                url = find_location_to_work(chromepage, url_list)
                captcha_filepath = download_captcha(chromepage, url, self.captcha_filepath)
                code = solve_captcha(captcha_filepath)
                send_captcha(chromepage, code)
                check_enrollment(chromepage)

            except Exception as Error:
                print(Error)

            finally:
                self.static_timer = 3600
                chromepage.quit()
                self.update_timer(self.static_timer)
                self.root.after(self.static_timer * 1000, self.enroll)

    def update_timer(self, countdown=None):
        if countdown is not None:
            self.countdown = countdown

        if self.countdown <= 0:
            self.timer_label.configure(text="--:--:--")
        else:
            self.timer_label.configure(text=str(timedelta(seconds=self.countdown)))
            self.countdown = self.countdown - 1
            self.root.after(1000, self.update_timer)
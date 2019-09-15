import time
import os
import sys
import pickle

import telegram
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import dotenv


# Load settings from environment
dotenv.load_dotenv()


class Robot:
    """
    Robot.

    Selenium robot class
    """
    def __init__(self):

        # Settings
        self.selenium_url = os.environ.get('SELENIUM_URL', 'http://localhost:4444/wd/hub')
        self.headless = os.environ.get('HEADLESS', None) is not None
        self.user_agent = os.environ.get('USER_AGENT', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36')
        self.locale = os.environ.get('LOCALE', 'ru,ru_RU')
        self.chromedriver_path = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
        self.cookie_path = os.environ.get('COOKIE_PATH', '/tmp/cookie.pkl')
        self.acc_user = os.environ.get('ACC_USER')
        self.acc_pass = os.environ.get('ACC_PASS')
        self.bot_token = os.environ.get('BOT_TOKEN')
        self.chat_id = os.environ.get('CHAT_ID')
        self.bot = self.get_bot()

        # Get driver
        self.driver = self.get_driver()

    def start(self):
        """
        Start

        Exec job
        :return:
        """
        try:
            self.inner_start()
        except BaseException as e:
            sys.exit('%s' % e)
        finally:
            self.driver.close()

    def inner_start(self):

        # Check user credentials
        if len(self.acc_user) == 0 or len(self.acc_pass) == 0:
            raise Exception('Missing account creds')

        self.check_login()
        time.sleep(2)

        # Scroll bottom
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

        # Scroll top
        self.driver.execute_script('window.scrollTo(0, -document.body.scrollHeight);')

        # Check new notifications
        try:
            self.driver.find_element_by_css_selector('.b-user-menu-clause-quantity')

            # Send notify to telegram
            self.bot.send_message(chat_id=self.chat_id, text='You have new notifications')

        except NoSuchElementException:
            print('No new messages')

    def check_login(self):
        self.driver.get('https://www.fl.ru/login/')
        self.load_cookies()
        self.driver.get('https://www.fl.ru/login/')

        try:
            self.driver.find_element_by_css_selector('.b-dropdown-opener-picture')
            self.driver.get('https://www.fl.ru/projects/')
        except NoSuchElementException:
            time.sleep(3)
            login_input = self.driver.find_element_by_css_selector('input[name=login]')
            login_input.send_keys(self.acc_user)

            password_input = self.driver.find_element_by_css_selector('input[name=passwd]')
            password_input.send_keys(self.acc_pass)

            login_button = self.driver.find_element_by_css_selector('button[name=singin]')
            login_button.click()

            time.sleep(3)
            self.store_cookies()

    def get_bot(self):
        return telegram.Bot(token=self.bot_token)

    def get_driver(self):
        """
        Get Driver

        Initialize webdriver.
        :return:
        """
        opts = self.build_options()

        if self.in_docker():
            return webdriver.Remote(command_executor=self.selenium_url, desired_capabilities=opts.to_capabilities())
        else:
            return webdriver.Chrome(self.chromedriver_path, chrome_options=opts)

    def build_options(self):
        """
        Build Options

        Build chrome driver options
        :return:
        """
        opts = Options()
        opts.headless = self.headless
        opts.add_argument('user-agent=%s' % self.user_agent)
        opts.add_argument('start-maximized')
        opts.add_argument('disable-infobars')
        opts.add_experimental_option('useAutomationExtension', False)
        opts.add_experimental_option('forceDevToolsScreenshot', True)
        opts.add_experimental_option('excludeSwitches', ['enable-automation'])
        opts.add_experimental_option('prefs', {
            'intl.accept_languages': self.locale,
            'profile.default_content_settings.popups': 0,
        })
        opts.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        return opts

    def store_cookies(self):
        pickle.dump(self.driver.get_cookies(), open(self.cookie_path, 'wb'))

    def load_cookies(self):
        """
        load cookeis.

        Look up and load cookies
        """
        if os.path.exists(self.cookie_path):
            print('load cookies from %s' % self.cookie_path)
            cookies = pickle.load(open(self.cookie_path, 'rb'))
            for cookie in cookies:
                # FIXME set correct expiry?
                if 'expiry' in cookie:
                    del cookie['expiry']
                self.driver.add_cookie(cookie)

    @staticmethod
    def in_docker():
        """
        In Docker

        Check robot ran in docker
        :return:
        """
        return os.path.exists('/.dockerenv')


if __name__ == '__main__':
    robot = Robot()
    robot.start()

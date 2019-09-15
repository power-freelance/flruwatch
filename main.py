import time
import os
import pickle

from selenium.common.exceptions import WebDriverException
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
        # TODO: other robot settings
        # self.param = os.environ.get('PARAM', 'default_value')

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
            os.exit('%s' % e)
        finally:
            self.driver.close()

    def inner_start(self):
        # TODO write code here :)
        pass
    
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
        opts.add_experimental_option("useAutomationExtension", False)
        opts.add_experimental_option("forceDevToolsScreenshot", True)
        opts.add_experimental_option("excludeSwitches", ['enable-automation'])
        opts.add_experimental_option("prefs", {
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

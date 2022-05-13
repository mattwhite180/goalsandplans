from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time
import logging
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager


class SeleniumGP:
    def __init__(self, base_url=None):
        if not base_url:
            base_url = "http://server:8000"
        self.base_url = base_url
        self.gp_ids = {
            "login_btn": "topbar-login",
            "logout_btn": "topbar-logout",
            "create_account_btn": "topbar-create",
            "about_btn": "topbar-about",
            "home_btn": "topbar-home",
            "submit": "submit"
        }
        logging.debug("setting driver")
        self.driver = webdriver.Remote(
            command_executor="http://chrome:4444/wd/hub",
        )
        logging.debug("logging out of gp")
        self.goto(self.base_url)
        if self.click("logout_btn"):
            logging.debug("successfully logged out of gp")
        else:
            logging.debug("already logged out")

    def __del__(self):
        logging.debug("quitting driver")
        self.driver.close()

    def goto(self, url="", no_base=False):
        if no_base:
            self.driver.get(url)
        else:
            self.driver.get(f"{self.base_url}/{url}")
        while self.get_url() != url:
            time.sleep(0.1)

    def get_driver(self):
        return self.driver

    def get_title(self):
        return self.driver.title

    def get_url(self):
        return self.driver.current_url

    def get_element(self, element_name: str, is_custom=True):
        if is_custom:
            return self.driver.find_element(By.ID, self.gp_ids[element_name])
        else:
            return self.driver.find_element(By.ID, element_name)

    def find_element(self, element_name: str, is_custom=True) -> bool:
        try:
            if is_custom:
                self.driver.find_element(By.ID, self.gp_ids[element_name])
            else:
                self.driver.find_element(By.ID, element_name)
            return True
        except NoSuchElementException:
            return False
        return True

    def login(self, username=None, password=None):
        self.get_element(element_name="login_btn").click()
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.get_element("submit").click()

    def click(self, element_name: str, is_custom=True):
        if self.find_element(element_name, is_custom):
            self.get_element(element_name, is_custom).click()
            return True
        else:
            return False


def main():
    logging.debug("hello world!")
    sgp = SeleniumGP()
    logging.debug(sgp.get_url())
    if sgp.click("home_btn"):
        logging.debug("clicked home button")
    else:
        logging.debug("cannot click home button")
    logging.debug("logging in...")
    sgp.login(username="root", password="asdf")
    logging.debug("logged in!")
    if sgp.click("home_btn"):
        logging.debug("clicked home button")
    else:
        logging.debug("cannot click home button")


if __name__ == "__main__":
    main()

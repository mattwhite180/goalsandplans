from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager


class SeleniumGP:
    def __init__(self, base_url=None):
        if not base_url:
            base_url = "http://server:8000"
        self.gp_ids = {
            "login_btn": "topbar-login",
            "logout_btn": "topbar-logout",
            "create_account_btn": "topbar-create",
            "about_btn": "topbar-about",
            "home_btn": "topbar-home",
            "submit": "submit"
        }
        print("setting driver")
        self.driver = webdriver.Remote(
            command_executor="http://chrome:4444/wd/hub",
        )
        print("logging out of gp")
        self.base_url = base_url
        self.goto(self.base_url)
        if self.click("logout_btn"):
            print("successfully logged out of gp")
        else:
            print("already logged out")

    def __del__(self):
        print("quitting driver")
        self.driver.quit()

    def goto(self, url=None):
        if url:
            self.driver.get(self.base_url)
        else:
            self.driver.get(url)

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
    print("hello world!")
    sgp = SeleniumGP()
    print(sgp.get_url())
    sgp.login(username="root", password="asdf")
    if sgp.click("home_btn"):
        print("clicked home button")
    else:
        print("cannot click home button")


if __name__ == "__main__":
    main()

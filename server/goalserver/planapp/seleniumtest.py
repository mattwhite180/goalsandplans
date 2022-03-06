from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

DRIVERS = {
    "docker": "/usr/bin/app/chromedriver",
    "local": "/home/mattw/Downloads/chromedriver",
}


s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)
driver.minimize_window()
driver.get("http://localhost")
driver.refresh()
print(driver.title)
print(driver.current_url)
driver.close()

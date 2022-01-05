from selenium import webdriver

DRIVERS = {
    'docker': '/usr/bin/app/chromedriver',
    'local': '/home/mattw/Downloads/chromedriver'
}

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

s=Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)
driver.minimize_window()
driver.get('http://localhost')
driver.refresh()
print(driver.title)
print(driver.current_url)
driver.close()

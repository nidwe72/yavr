from builtins import bytearray

import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains

from getpass import getpass

#username = input("Enter in your username: ")
username = 'edwin.roth@gmx.at'

#password = getpass("Enter in your password: ")
password = 'Rustam6971'

driver = webdriver.Chrome()

driver.get("https://www.amazon.de/")



#cookiesButton = driver.find_element('xpath','//*[@id="sp-cc-accept"]/span')
# cookiesButton = driver.find_element(by=By.XPATH,value='//*[@id="sp-cc-accept"]/span')
# cookiesButton.click()


cookiesButton = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="sp-cc-accept"]'))
    )

print(cookiesButton)
cookiesButton.click()


signinButton = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="nav-link-accountList"]'))
    )
print(signinButton)
signinButton.click()


# SignIn_button = driver.find_element('xpath','//*[@id="nav-link-accountList"]/span')
# SignIn_button.click()

# username_textbox = driver.find_element_by_id("ap_email")

username_textbox=WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, 'ap_email'))
    )
username_textbox.send_keys(username)

# Continue_button = driver.find_element_by_id("continue")
Continue_button=WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, 'continue'))
    )
Continue_button.submit()

#password_textbox = driver.find_element_by_id("ap_password")
password_textbox=WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, 'ap_password'))
    )
password_textbox.send_keys(password)

#SignIn_button = driver.find_element_by_id("auth-signin-button-announce")
SignIn_button=WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, 'auth-signin-button-announce'))
    )
SignIn_button.submit()

 time.sleep(60)

driver.get("https://www.amazon.de/gp/video/detail/B0B6STPSVJ/?autoplay=1&t=0")



time.sleep(400)




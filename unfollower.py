import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = '/PATH/TO/Google Chrome'
chrome_webdriver_path = '/PATH/TO/chromedriver'

driver = webdriver.Chrome(chrome_webdriver_path, options=chrome_options)

# constants
auth = {
  'username': '',
  'password': ''
}
unfollow_count = 150

# init
driver.get('https://www.instagram.com')
try:
  myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.NAME, 'password')))
except TimeoutException:
  driver.quit()

# login
username_input = driver.find_element_by_name('username')
password_input = driver.find_element_by_name('password')

username_input.send_keys(auth['username'])
password_input.send_keys(auth['password'])
password_input.send_keys(Keys.RETURN)

try:
  myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Not Now')]")))
  notnow_button = driver.find_element_by_xpath("//*[contains(text(), 'Not Now')]")
  notnow_button.click()
except TimeoutException:
  print('Loading took too much time, skipping!')

try:
  myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Not Now')]")))
  notnow_button = driver.find_element_by_xpath("//*[contains(text(), 'Not Now')]")
  notnow_button.click()
except TimeoutException:
  print('Loading took too much time, skipping!')

# set up following screen
driver.get('https://www.instagram.com/' + auth['username'] + '/')

try:
  myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//a[@href="/' + auth['username'] + '/following/"]')))
except TimeoutException:
  driver.quit()

following_modal_toggle = driver.find_element_by_xpath('//a[@href="/' + auth['username'] + '/following/"]')
following_modal_toggle.click()

try:
  myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"]//ul')))
except TimeoutException:
  driver.quit()

following_modal = driver.find_element_by_xpath('//div[@role="dialog"]')
following_modal_content = driver.find_element_by_xpath('//div[@role="dialog"]/div/div[last()]')
for i in range(20):
  driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', following_modal_content)
  time.sleep(1)

# unfollow
cursor = 0
unfollow_buttons = driver.find_elements_by_xpath("//button[contains(., 'Following')]")
while(cursor < unfollow_count):
  unfollow_buttons[cursor].click()
  time.sleep(0.5)
  try:
    myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//button[contains(., "Unfollow")][1]')))
    confirm_button = driver.find_element_by_xpath("//button[contains(., 'Unfollow')][1]")
    confirm_button.click()
  except TimeoutException:
    print('Oops, taking a long time')
  cursor += 1
  time.sleep(1)
driver.quit()

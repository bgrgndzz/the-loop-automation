import time
from datetime import datetime
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

load_dotenv()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.binary_location = os.getenv('BINARY_LOCATION')
chrome_webdriver_path = os.getenv('WEBDRIVER_PATH')

driver = webdriver.Chrome(chrome_webdriver_path, options=chrome_options)

# constants
auth = {
  'username': os.getenv('USERNAME'),
  'password': os.getenv('PASSWORD')
}
unfollow_count = int(os.getenv('UNFOLLOW_COUNT'))
unfollow_timeout = int(os.getenv('UNFOLLOW_TIMEOUT'))

# load activity-log
with open('activity-log.txt', 'r') as activity_log_file:
  activity_log = activity_log_file.read().splitlines()

unfollow_blacklist = [log.split()[1] for log in activity_log if log.split()[0] == 'follow' and (datetime.utcnow() - datetime.strptime(log.split()[2], '%Y-%m-%dT%H:%M:%SZ')).days < unfollow_timeout + 1]

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
  print('Loading took too much time, quitting!')
  driver.quit()

following_modal_toggle = driver.find_element_by_xpath('//a[@href="/' + auth['username'] + '/following/"]')
following_modal_toggle.click()

try:
  myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"]//ul')))
except TimeoutException:
  print('Loading took too much time, quitting!')
  driver.quit()

following_modal_content = driver.find_element_by_xpath('//div[@role="dialog"]/div/div[last()]')
for i in range(10):
  driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', following_modal_content)
  time.sleep(1)

# unfollow
unfollowed_users = []
cursor = 0
unfollow_buttons = driver.find_elements_by_xpath("//button[contains(., 'Following')]")
while(cursor < unfollow_count):
  unfollowed_user = unfollow_buttons[cursor].find_element_by_xpath(".//../../div/div[2]/div/span/a").text
  cursor += 1
  if unfollowed_user in unfollow_blacklist:
    continue

  unfollow_buttons[cursor].click()
  time.sleep(0.5)
  unfollowed_users.append(unfollowed_user)

  try:
    myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//button[contains(., "Unfollow")][1]')))
    confirm_button = driver.find_element_by_xpath("//button[contains(., 'Unfollow')][1]")
    confirm_button.click()
  except TimeoutException:
    print('Oops, taking a long time')

  time.sleep(1)

# log new activity
current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
with open('activity-log.txt', 'a') as activity_log_file:
  for unfollowed_user in unfollowed_users:
    activity_log_file.write(f'unfollow {unfollowed_user} {current_date}\n')

driver.quit()

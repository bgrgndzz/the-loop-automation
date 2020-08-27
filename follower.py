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
follow_count = int(os.getenv('FOLLOW_COUNT'))

# load follow-list
with open('./follow-list.txt', 'r') as follow_list_file:
  follow_list = follow_list_file.read().splitlines()
  if len(follow_list) == 0:
    print('Empty follow list, quitting...')
    driver.quit()

# load activity-log
with open('./activity-log.txt', 'r') as activity_log_file:
  activity_log = activity_log_file.read().splitlines()

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

# follow
followed_users = []
skipped = 0

for i in range(len(follow_list)):
  followed_user = follow_list[i]

  if any(followed_user in log for log in activity_log):
    skipped += 1
    continue

  driver.get(f'https://www.instagram.com/{followed_user}')

  try:
    myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//button[text()='Follow']")))
  except TimeoutException:
    skipped += 1
    continue

  follow_button = driver.find_element_by_xpath('//button[text()="Follow"]')
  follow_button.click()

  followed_users.append(followed_user)

  if len(followed_users) == follow_count:
    break

  time.sleep(1.5)

# log new activity
current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
with open('./activity-log.txt', 'a') as activity_log_file:
  for followed_user in followed_users:
    activity_log_file.write(f'follow {followed_user} {current_date}\n')

with open('./follow-list.txt', 'w') as follow_list_file:
  iterations = len(followed_users) + skipped
  if len(follow_list) > iterations:
    for follow_user in follow_list[iterations:]:
      follow_list_file.write(f'{follow_user}\n')

driver.quit()

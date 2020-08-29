import time
from datetime import datetime
from dotenv import load_dotenv
import os
import sys
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

# load arguments
if len(sys.argv) == 1:
  print('Empty argument list, quitting!')
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

# load likers
likers = []
for post in sys.argv[1:]:
  driver.get(post)
  time.sleep(5)

  try:
    myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Liked by')]/button")))
    likers_toggle = driver.find_element_by_xpath("//*[contains(text(), 'Liked by')]/button")
    likers_toggle.click()
  except TimeoutException:
    print('Loading took too much time, quitting!')
    driver.quit()

  try:
    myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"]/div/div[last()]/div')))
  except TimeoutException:
    print('Loading took too much time, quitting!')
    driver.quit()

  likedby_modal_content = driver.find_element_by_xpath('//div[@role="dialog"]/div/div[last()]/div')

  try:
    myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//button[text()='Follow']")))
  except TimeoutException:
    print('Loading took too much time, quitting!')
    driver.quit()

  follow_buttons = []

  retry = 5

  while True:
    new_follow_buttons = driver.find_elements_by_xpath(f"//div[@role='dialog']//button[text()='Follow']")
    if len(follow_buttons) != 0 and new_follow_buttons[-1] == follow_buttons[-1]:
      if retry > 0:
        retry -= 1
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + 500', likedby_modal_content)
        time.sleep(1)
        continue
      break
    follow_buttons = new_follow_buttons

    for follow_button in follow_buttons:
      liker = follow_button.find_element_by_xpath(".//../../div[2]//span/a").text

      if any(liker in log for log in activity_log) or liker in likers:
        continue

      likers.append(liker)

    driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + 500', likedby_modal_content)
    time.sleep(1)

# save likers
with open('./follow-list.txt', 'a') as follow_list_file:
  for liker in likers:
    follow_list_file.write(f'{liker}\n')

driver.quit()

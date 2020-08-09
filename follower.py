import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import os

load_dotenv()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.binary_location = os.getenv('BINARY_LOCATION')
chrome_webdriver_path = os.getenv('WEBDRIVER_PATH')

driver = webdriver.Chrome(chrome_webdriver_path, options=chrome_options)

# constants
auth = {
  'username': os.getenv('USERNAME'),
  'password': os.getenv('PASSWORD')
}
follow_count = os.getenv('FOLLOW_COUNT')

# load follow-list
with open('follow-list.txt', 'r') as follow_list_file:
  follow_list = follow_list_file.read().splitlines()
  if len(follow_list) == 0:
    print('Empty follow list, quitting...')
    driver.quit()

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
followed_count = 0
follow_list_cursor = 0
while followed_count != follow_count and follow_list_cursor != len(follow_list):
  driver.get(follow_list[follow_list_cursor])

  try:
    myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Liked by')]/button")))
    likers_toggle = driver.find_element_by_xpath("//*[contains(text(), 'Liked by')]/button")
    likers_toggle.click()
  except TimeoutException:
    print('Loading took too much time, quitting!')
    driver.quit()

  try:
    myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"]/div/div[last()]')))
  except TimeoutException:
    print('Loading took too much time, quitting!')
    driver.quit()

  likedby_modal_content = driver.find_element_by_xpath('//div[@role="dialog"]/div/div[last()]/div')
  unfollow_buttons = driver.find_elements_by_xpath("//div[@role='dialog']//button[text()='Following' or text()='Requested']")
  for i in range((len(unfollow_buttons) // 10) + 3):
    driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', likedby_modal_content)
    time.sleep(1)

  try:
    myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//button[text()='Follow']")))
  except TimeoutException:
    print('Loading took too much time, quitting!')
    driver.quit()

  while(followed_count < follow_count):
    follow_button = driver.find_element_by_xpath("//div[@role='dialog']//button[text()='Follow']")
    follow_button.click()
    time.sleep(1.5)
    followed_count += 1

  follow_list_cursor += 1

driver.quit()

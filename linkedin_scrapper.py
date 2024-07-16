from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from openpyxl import Workbook
import time
import requests
import os
from dotenv import load_dotenv
import pytest
import json

load_dotenv()

email = os.getenv('LINKEDIN_EMAIL')
password = os.getenv('LINKEDIN_PASSWORD')

def has_modal_class(element, target_class):
  current_element = element
  while current_element:
    if target_class in current_element.get_attribute('class'):
      return True
    try:
      current_element = current_element.find_element(By.XPATH, '..')
    except:
      break
  return False

def is_connected():
  try:
    requests.get('https://www.google.com', timeout=5)
    return True
  except requests.ConnectionError:
    return False

def wait_for_internet_connection():
  while not is_connected():
    print("Internet connection lost. Waiting to reconnect...")
    time.sleep(5)
  print("Internet connection restored. Resuming...")

def save_cookies(sb):
  cookies = sb.driver.get_cookies()
  for cookie in cookies:
    if "httpOnly" in cookie:
      cookie["httpOnly"] = bool(cookie["httpOnly"])
    if "secure" in cookie:
      cookie["secure"] = bool(cookie["secure"])

  with open("cookies.json", "w") as file:
    json.dump(cookies, file, indent=2)

def load_cookies(sb):
  with open("cookies.json", "r") as file:
    cookies = json.load(file)
    for cookie in cookies:
      sb.driver.add_cookie(cookie)


def scrape_linkedin_data(url):  
  with SB(uc=True, demo=True) as sb:
    try:
      if os.path.exists("cookies.json"):
        sb.driver.get('https://www.linkedin.com')
        load_cookies(sb)
        sb.sleep(1)
      else:
        raise FileNotFoundError
    except FileNotFoundError:
      print("No cookie found yet")


    sb.driver.get(url)
    

    emailField = "input[aria-label^='Email or Phone']"
    passwordField = "input[aria-label^='Password']"
    signInBtn = "button[aria-label='Sign in']"

    if sb.is_element_visible(emailField):
      sb.click(emailField)
      sb.type(emailField, email)

      sb.wait_for_element_visible(passwordField)
      sb.click(passwordField)
      sb.type(passwordField, password)

      sb.wait_for_element_clickable(signInBtn)
      sb.click(signInBtn)
      sb.sleep(5)  # Wait for login to complete

      save_cookies(sb)
    elif sb.is_element_visible(passwordField):
      sb.wait_for_element_visible(passwordField)
      sb.click(passwordField)
      sb.type(passwordField, password)

      sb.wait_for_element_clickable(signInBtn)
      sb.click(signInBtn)
      sb.sleep(5)  # Wait for login to complete

      save_cookies(sb)
    else: 
      sb.sleep(5)

    showAllFollowersButton = "//button[contains(., 'Show all followers')]"
    sb.wait_for_element_visible(showAllFollowersButton, timeout=200)
    sb.scroll_to(showAllFollowersButton)
    sb.click(showAllFollowersButton)
    
    scrollable_element = ".scaffold-finite-scroll__content"
    sb.wait_for_element_visible(scrollable_element)

    try:
      invalid_elements_count = 0
      max_invalid_elements = 5
      while True:
        if not is_connected():
          wait_for_internet_connection()

        actions = ActionChains(sb.driver)
        actions.send_keys('\ue004').perform()

        highlighted_element = sb.driver.switch_to.active_element

        if has_modal_class(highlighted_element, 'org-view-page-followers-modal__follower-list-item'):
          invalid_elements_count = 0 
          # if highlighted_element.tag_name == 'a':
          #     href = highlighted_element.get_attribute('href')
          #     name_element = highlighted_element.find_element(By.CLASS_NAME, 'artdeco-entity-lockup__title')
          #     name = name_element.text.strip()
          #     print(f"{href}, {name}")
        else:
          invalid_elements_count += 1
          if invalid_elements_count >= max_invalid_elements:
            print("Too many consecutive invalid elements, breaking the loop.")
            break
        
        sb.sleep(1)
      
      sb.sleep(5)
      child_elements = sb.find_elements(f"{scrollable_element} > *")
      
      links = []
      for el in child_elements:
        try:
          a_tag = el.find_element(By.TAG_NAME, 'a')
          href = a_tag.get_attribute('href')
          links.append(href)
          print(href)
        except Exception as e:
          print('Could not find link in elements')
          
      print(len(child_elements))

      wb = Workbook()
      ws = wb.active
      ws.title = "Links"

      for idx, link in enumerate(links, start=1):
        ws.cell(row=idx, column=1, value=link)

      wb.save("links.xlsx")
      print('End of list')

    except Exception as e:
      sb.sleep(10)
      print(e)




url = "https://www.linkedin.com/company/89752477/admin/analytics/followers/"

scrape_linkedin_data(url)
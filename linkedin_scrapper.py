from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from openpyxl import Workbook
import time
import requests
import os
from dotenv import load_dotenv
import pytest

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

    
def scrape_linkedin_data(url):  
  with SB(uc=True, demo=True) as sb:
    sb.driver.get(url)

    try:
      sb.load_cookies(name="cookies.txt")
      sb.driver.refresh()
    except:
      print("no cookie found yet")

    emailField = "input[aria-label^='Email or Phone']"
    if sb.is_element_visible(emailField):
      sb.click(emailField)
      sb.type(emailField, email)

      passwordField = "input[aria-label^='Password']"
      sb.wait_for_element_visible(passwordField)
      sb.click(passwordField)
      sb.type(passwordField, password)

      signInBtn = "button[aria-label='Sign in']"
      sb.wait_for_element_clickable(signInBtn)
      sb.click(signInBtn)
      sb.sleep(5)  # Wait for login to complete
      sb.save_cookies(name="cookies.txt")
    else:
      passwordField = "input[aria-label^='Password']"
      sb.wait_for_element_visible(passwordField)
      sb.click(passwordField)
      sb.type(passwordField, password)

      signInBtn = "button[aria-label='Sign in']"
      sb.wait_for_element_clickable(signInBtn)
      sb.click(signInBtn)
      sb.sleep(5)  # Wait for login to complete
      sb.save_cookies(name="cookies.txt")
      
    
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



urls = ["https://www.linkedin.com/company/89752477/admin/analytics/followers/"]
@pytest.mark.parametrize("url", urls)
def test_multi_threaded(url):
  scrape_linkedin_data(url)
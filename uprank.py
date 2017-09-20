from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common import action_chains, keys
from pyvirtualdisplay import Display
import sys
import time
import yaml
import os


dir = os.path.dirname(__file__)
config_file_path = os.path.join(dir,"config.yml")
config = yaml.safe_load(open(config_file_path))
url = 'https://www.wg-gesucht.de/'
edit_url = 'https://www.wg-gesucht.de/gesuch-bearbeiten.html?edit={}'.format(config['application_id'])

# allows running it on remote server
display = Display(visible=0, size=(800, 600))
display.start()

browser = webdriver.Chrome(config['path_to_driver'])
delay = 30

def load_web_page():
    browser.get(url)
    try:
        WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, "//div[@id='service-navigation']/div/a[2]")))
        print "Page has loaded!"
    except TimeoutException:
        print "Loading took more than {} seconds!".format(delay)
        sys.exit(1)

def login():
    # Click on Login Link
    browser.find_element(By.XPATH, "//div[@id='service-navigation']/div/a[2]").click()

    try:
        WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, "login_email_username")))
        print "Login modal has loaded!"
    except TimeoutException:
        print "Loading the modal took more than {} seconds!".format(delay)
        sys.exit(1)

    # Make sure the login input fields are loaded and visible by simulating a click
    assert 'login_email_username' in browser.page_source
    action = action_chains.ActionChains(browser)
    action.send_keys(keys.Keys.COMMAND+keys.Keys.ALT+'i')
    action.perform()
    time.sleep(3)
    action.send_keys(keys.Keys.ENTER)
    action.send_keys("document.querySelector('#login_email_username').click()"+keys.Keys.ENTER)
    action.perform()

    # Login
    browser.find_element_by_id('login_email_username').send_keys(config['username'])
    browser.find_element_by_id('login_password').send_keys(config['password'])
    browser.find_element_by_id('login_basic').submit()

    time.sleep(3)

def update_title():
    title1 = u'Studium vorbei - suche WG in der Heimat !'
    title2 = u'Studium vorbei - suche WG in der Heimat!'
    try:
        title_element = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, "title")))
        print "Title input is ready!"
        current_title = title_element.get_attribute('value')
        title_element.clear()
        new_title = title1
        if current_title == title1:
            new_title = title2

        title_element.send_keys(new_title)
        print("Set title to {}".format(new_title))
        
    except TimeoutException:
        print "Loading title input took more than {} seconds!".format(delay)
        sys.exit(1)
    


def update_application():
    # Go to edit page of application
    browser.get(edit_url)

    # Leave and submit first page of application as is
    try:
        first_page = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, "create_ad")))
        print "Ad submit button is ready!"
        first_page.submit()

    except TimeoutException:
        print "Loading ad submit button took more than {} seconds!".format(delay)
        sys.exit(1)

    # Update title on second page of application
    update_title()

    # Submit change
    browser.find_element_by_id('thisForm').submit()

def shut_down():
    browser.close()
    display.stop()
    print("Finished update!")


if __name__ == '__main__':
    load_web_page()
    login()
    update_application()
    shut_down()

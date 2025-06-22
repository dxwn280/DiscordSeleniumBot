from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

def sendCommand(username: str, driver):
    '''Used to send commands to the textbox'''
    path = '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div[2]/div/div/div[3]/main/form/div/div[1]/div/div/div[3]/div/div[2]' # textbox for input

    WebDriverWait(driver, 10).until( # wait until the text box appears
        ec.presence_of_element_located((By.XPATH, path))
    )

    input_element = driver.find_element(By.XPATH, path)
    input_element.send_keys("/c" + Keys.ENTER + username + Keys.ENTER) # send command

def ContainerExist(container_xpath: str, time:int, driver): 
    '''A check to see if the container exists'''
    try:
        WebDriverWait(driver, time).until(
            ec.presence_of_element_located((By.XPATH, container_xpath)) # wait until container exists
        )
        return True
    except StaleElementReferenceException:
        return 404
    except TimeoutException: # if timeout due to no container then username is invalid
        return False

def usernameFind(username_xpath: str, driver):
    '''Find and retrieve username'''
    try:
        return driver.find_element(By.XPATH, username_xpath).text
    except StaleElementReferenceException:
        return False

def retrieveMessage(messageContainer:str, time:int, driver):
    '''Find, check and retrieve any message contents'''
    try:
        WebDriverWait(driver, time).until(
            ec.presence_of_all_elements_located((By.XPATH, messageContainer))
        )

        message = driver.find_element(By.XPATH, messageContainer).text.split('\n')
        message2 = driver.find_elements(By.XPATH, messageContainer+'[2]') # sometimes the message contents is split into 2, check if there's a second message
        if message2:
            message2 = driver.find_element(By.XPATH, messageContainer+'[2]').text.split('\n')
            message = message + message2

        return message
    except StaleElementReferenceException:
        return 404
    except NoSuchElementException: # if no message container then no message to retrieve
        return False

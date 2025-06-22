from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from concurrent.futures import ThreadPoolExecutor
import time

from commands.login import login
from commands.find import sendCommand, ContainerExist, retrieveMessage, usernameFind

print("Starting")

profile = "profiles\\profileName"
options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={profile}")
service = Service(executable_path="files\\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)


numCommands = 4 # number of commands per betch

time.sleep(4)
user_input = input(f"Please enter an integer (or press Enter for default {numCommands}): ")
    
if user_input.strip() == "":
    numCommands = numCommands
else:
    try:
        numCommands = int(user_input)
    except ValueError:
        print("Invalid input")
        numCommands = 4

# xpath's to find elements
container_xpaths = [f"/html/body/div[1]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div[2]/div/div/div[3]/main/div[1]/div/div/ol/li[last()-{numCommands-1-i}]/div/div[3]/article/div/div" for i in range(numCommands)]
mesasge_xpaths = [f"/html/body/div[1]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div[2]/div/div/div[3]/main/div[1]/div/div/ol/li[last()-{numCommands-1-i}]/div/div[3]/article/div/div/div[2]/span" for i in range(numCommands)]
username_xpaths = [f"/html/body/div[1]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div[2]/div[2]/div/div/div[3]/main/div[1]/div/div/ol/li[last()-{numCommands-1-i}]/div/div[3]/article/div/div/div[1]/span"for i in range(numCommands)]

requeue = [] # list of usernames that need requing


def writeToFile(username: str, limiteds: list): # for saving results if any
    '''Save any results'''
    with open('files\\output.txt', 'a') as file:
        writelimiteds = ', '.join(limiteds)
        file.write(f'{username}, {writelimiteds}\n')

def StaleElementFound(username: str):
    '''Requeue any usernames which have become stale due to the node being rebuilt'''
    global requeue

    logging(f'Requing user: {username}')
    requeue.append(username)

def logging(string: str):
    print(string)
    with open('files\\log.txt', 'a') as file:
        file.write(f'{string}\n')



def findMessage(username: str, i: int):
    '''Check and retrieve message & username content from response'''
    global temp_usernames
    container_exist = ContainerExist(container_xpaths[i], 5, driver)
    if container_exist:
        message = retrieveMessage(mesasge_xpaths[i], 1, driver)
        if isinstance(message, list):
            if message[0].startswith("https://"): # sometimes the message container text would have a https link
                pass
            else:
                user = usernameFind(username_xpaths[i], driver) # username might change, use the most updated one
                if user:
                    writeToFile(user, message)
                    logging(f'{user} = {message}')
                else:
                    StaleElementFound(username)
        elif message == 404: 
            StaleElementFound(username)
        else:
            pass
    elif container_exist == 404:
        StaleElementFound(username)
    else:
        logging(f'TimeOutException for {username}')

    

def runBatch(usernames: list):
    '''Send two seperate batches of commands, one to send the commands, another to retrieve output'''
    logging(f"\n--- Starting Batch ---")
    i = 0
    with ThreadPoolExecutor(max_workers=numCommands) as executor:
        for username in usernames:
            logging(f'Checking username: {username}')
            executor.submit(sendCommand, username, driver) # send the 5 commands

        executor.shutdown(wait=True)

    logging('')
    ContainerExist(container_xpaths[numCommands-1], 15, driver) # wait until last container exists

    with ThreadPoolExecutor(max_workers=numCommands) as executor:
        for username in usernames:
            executor.submit(findMessage, username, i) # find message contents
            i+= 1

        executor.shutdown(wait=True)
        i = 0
    


def main_loop():
    '''Main loop used to get usernames to use for each batch'''
    global requeue
    temp_usernames = []

    with open('files\\usernames.txt', 'r') as file:
        for line in file:

            for username in requeue: # requeue any elements that were stale from the previous batch
                temp_usernames.append(username)

            counter = len(temp_usernames)
            requeue.clear()

            line = line.strip()
            temp_usernames.append(line) # append the usernames being used for the batch
            counter += 1
            
            if counter == numCommands: # to ensure we have the right amount of usernames for desired amount per batch
                start = time.time()

                runBatch(temp_usernames)

                end = time.time()
                duration = end - start
                logging(f"\nCompleted in {duration:.2f}")

                temp_usernames.clear()
                
                counter = 0 

 
if __name__ == "__main__":
    login(driver)
    main_loop()
    
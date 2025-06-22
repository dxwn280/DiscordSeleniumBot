import time
import json

with open('commands\\config.json') as config:
    config_data = json.load(config)

token = config_data['token']
url = config_data['url']

def login(driver):
    print("Logging in!")
    driver.get(url)

    script = f'''
    function login(token) {{
        setInterval(() => {{
            document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${{token}}"`;
        }}, 50);
        setTimeout(() => {{
            location.reload();
        }}, 2500);
    }}
    login("{token}");  // Call the login function with the token
    '''


    driver.execute_script(script)
    time.sleep(10) # give it time to load everything afterwards
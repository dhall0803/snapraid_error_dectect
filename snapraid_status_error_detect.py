#!/usr/bin/python3
import os
import logging
import subprocess
import json
import requests

#You need to create a config.json file with the following keys:
#"toEmail" with the email you want to send the error notification to
#"fromEmail" with the email address that is sending the notification

#load configuration
with open("config.json", "r") as config_file:
    config = json.loads(config_file.read())

email_enabled = config["email"]["enabled"]
telegram_enabled = config["telegram"]["enabled"]

#configure logging:
logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s',level=logging.INFO, filename="log.txt")

try:
    #Start script
    logging.info("Script starting")

    #Run snapraid status and save output to status.txt
    logging.info("Running snapraid status")
    subprocess.run("sudo snapraid status > status.txt", check=True, shell=True)

    #Open status.txt and look for the string "No error detected": if it is found, do nothing, else send a notification saying an error
    #has been detected
    logging.info("Checking result for errors...")
    with open("status.txt", "r") as f:
        if not "No error detected.\n" in f.readlines():
            logging.warning("Error detected in status.txt")
            if email_enabled:
                logging.info("Sending email notification")
                to_email = config["toEmail"]
                from_email = config["fromEmail"]
                subprocess.run(f"cat status.txt | mail -r {from_email} -s \"Snapraid error detected!\" {to_email}", shell=True, check=True)
                logging.info("Email sent")
            if telegram_enabled:
                logging.info("Sending telegram notification")
                telegram_bot_token = os.environ[config["telegram"]["environmentVariables"]["bot_token_var"]]
                telegram_chat_id = os.environ[config["telegram"]["environmentVariables"]["chat_id_var"]]
                queryParams = {
                    "chatId": telegram_chat_id,
                    "text": f"WARNING! Snapraid errors detected!\n\n{f.read()}" 
                }
                url = f"https://api.telegram.org/bot{telegram_bot_token}"
                response = requests.get(url, queryParams)
                if response.status_code is not 200:
                    logging.error(f"{response.status_code} received sending telegram notifcation")
                    logging.error(f"{str.encode(response.content)})")

        else:
            logging.info("No errors detected")
except Exception as e:
    logging.error(e)

#!/usr/bin/python3
import logging
import subprocess
import json

#You need to create a config.json file with the following keys:
#"toEmail" with the email you want to send the error notification to
#"fromEmail" with the email address that is sending the notification

#load configuration
with open("config.json", "r") as config_file:
    config = json.loads(config_file.read())

to_email = config["toEmail"]
from_email = config["fromEmail"]

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
            subprocess.run(f"cat status.txt | mail -r {from_email} -s \"Snapraid error detected!\" {to_email}", shell=True, check=True)

        else:
            logging.info("No errors detected")
except Exception as e:
    logging.error(e)

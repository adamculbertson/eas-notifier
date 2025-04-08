import sys
import subprocess
import os
import json
import threading
import logging

import requests

# Define the logger and set up the logging level
logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s")

# The level can be  whatever names setLevel() supports
if "LOG_LEVEL" in os.environ:
    level = os.environ['LOG_LEVEL']
else:
    # Default to INFO if not specified
    level = logging.INFO

logging.getLogger().setLevel(level)

if "WEBHOOK_URL" not in os.environ:
    logging.critical("No WEBHOOK_URL provided in the environment!")
    sys.exit(1)

webhook_url = os.environ['WEBHOOK_URL']

# SAME codes are optional, so check if they were provided
try:
    same = os.environ['SAME']
    # Remove the quotes from the SAME codes
    # Convert the SAME codes into an array
    # This will be passed to dsame3
    same = same.replace("\"", "")
    same = same.split(" ")

    if not same:
        same = None
except KeyError:
    same = None

if same is not None:
    logging.debug(f"Number of SAME codes specified: {len(same)}")
else:
    logging.debug("No SAME codes specified")

# Check if the authorization token exists in the environment and contains a valid "truthful" value (not empty quotes)
try:
    webhook_authorization = os.environ['WEBHOOK_AUTHORIZATION']
    if not webhook_authorization:
        webhook_authorization = None
except KeyError:
    webhook_authorization = None

if webhook_authorization is not None:
    logging.debug("Using provided webhook authorization token")


def parse_event(event: dict):
    # See Event Codes from here: https://github.com/jamieden/dsame3
    # Send the data obtained to the provided webhook
    headers = {}
    if webhook_authorization is not None:
        headers['Authorization'] = webhook_authorization

    try:
        r = requests.post(webhook_url, json=event, headers=headers)
    except Exception as e:
        logging.error(f"Caught exception posting to webhook. {e}")
        return

    if not r.ok:
        logging.error(f"Error posting to webhook. Received status code {r.status_code}\nHeaders: {json.dumps(headers)}")
        return

    logging.info("Successfully posted to webhook!")


if __name__ == "__main__":
    logging.info("Ready to parse incoming alerts!\n")
    for line in sys.stdin:
        # Skip the end message of an alert
        if "NNNN" in line:
            logging.debug("Skipping NNNN line")
            continue

        if line.startswith("EAS:"):
            # Strip out the EAS: line from the output so that we can directly send it to dsame.py
            line = line.replace("EAS: ", "").strip()
            # same_decode(line, "EN", same_watch=same, event_watch=None,

            logging.debug(f"Alert received: {line}")

            # I would rather just call the function instead of using subprocess for this
            # However, given how much trouble it's been just getting some output and dealing with buffering
            # I am going to use subprocess.run for a while, but may end up in the future trying the function

            params = ["python", "-u", "/eas-notifier/dsame3/dsame.py", "--msg", line ]

            # The SAME codes are passed using a single --same flag, but as multiple parameters
            # We append the list containing the SAME codes to the parameter list
            # Determine if any SAME codes were provided
            if same is not None:
                params += ["--same"] + same

            params += ["--json", "-"]  # Have dsame output the JSON to stdout instead

            logging.debug(f"dsame parameters: {params}")

            p = subprocess.run(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.returncode == 0 and p.stdout:
                try:
                    js = json.loads(p.stdout)
                except json.JSONDecodeError:
                    # dsame sometimes outputs an empty string
                    # Output the line that causes the empty string for debugging
                    logging.error(f"Error decoding JSON from dsame\nOutput: {p.stdout}\nLine: {line}")
                    continue

                # Print out the fully parsed message
                print(js['MESSAGE'])

                js['line'] = line  # Add the raw data for the line to the payload
                # Send the stdout of the process to the parse_event function in a new thread
                threading.Thread(target=parse_event, args=(js,)).start()

            elif p.returncode == 0 and not p.stdout:
                # Blank output can be caused by the use of the --same parameter
                # When the alert does not match anything in the list of codes, then nothing is output
                logging.debug(f"dsame blank output: {line}")

            else:
                logging.error(f"Unexpected return value from dsame: {p.returncode}\nLine: {line}")

import sys
import subprocess
import os
import json
import threading

import requests

same = os.environ['SAME']
webhook_url = os.environ['WEBHOOK_URL']

# Remove the quotes from the SAME codes
# Convert the SAME codes into an array
# This will be passed to dsame3
same = same.replace("\"", "")
same = same.split(" ")

# Check if the authorization token exists in the environment and contains a valid "truthful" value (not empty quotes)
try:
    webhook_authorization = os.environ['WEBHOOK_AUTHORIZATION']
    if not webhook_authorization:
        webhook_authorization = None
except KeyError:
    webhook_authorization = None


def parse_event(event: dict):
    # See Event Codes from here: https://github.com/jamieden/dsame3
    # Send the data obtained to the provided webhook
    headers = {}
    if webhook_authorization is not None:
        headers['Authorization'] = webhook_authorization

    try:
        r = requests.post(webhook_url, json=event, headers=headers)
    except Exception as e:
        sys.stderr.write(f"Caught exception posting to webhook. {e}\n")
        sys.stderr.flush()
        return

    if r.status_code != r.ok:
        sys.stderr.write(f"Error posting to webhook. Received status code {r.status_code}\n")
        sys.stderr.flush()


if __name__ == "__main__":
    sys.stdout.write("Ready to parse incoming alerts!\n")
    sys.stdout.flush()
    for line in sys.stdin:
        if "NNNN" in line:
            continue

        if line.startswith("EAS:"):
            # Strip out the EAS: line from the output so that we can directly send it to dsame.py
            line = line.replace("EAS: ", "")
            # same_decode(line, "EN", same_watch=same, event_watch=None,

            # I would rather just call the function instead of using subprocess for this
            # However, given how much trouble it's been just getting some output and dealing with buffering
            # I am going to use subprocess.run for a while, but may end up in the future trying the function

            # The SAME codes are passed using a single --same flag, but as multiple parameters
            # We append the list containing the SAME codes to the parameter list
            params = ["python", "-u", "/eas-notifier/dsame3/dsame.py", "--msg", line, "--same"] + same + \
                     ["--json", "-"]  # Have dsame output the JSON to stdout instead

            p = subprocess.run(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.returncode == 0:
                try:
                    js = json.loads(p.stdout)
                except json.JSONDecodeError as e:
                    sys.stderr.write(f"Error decoding JSON from dsame: {e}\n")
                    sys.stderr.write(f"Output: {p.stdout}\n")
                    sys.stderr.flush()
                    continue

                sys.stdout.write(js['MESSAGE'] + "\n")
                sys.stdout.flush()
                # Send the stdout of the process to the parse_event function in a new thread
                threading.Thread(target=parse_event, args=(js,)).start()

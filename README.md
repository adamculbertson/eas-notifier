# eas-notifier
Docker container that uses [dsame3](https://github.com/jamieden/dsame3) to parse incoming data from the Emergency Alert System (EAS) via UDP.

## Configuration
The `pipe.py` script looks for three environment variables: `SAME`, `WEBHOOK_URL`, and `WEBHOOK_AUTHORIZATION`. If needed, a `PORT` environment variable may also be specified to use a custom port number. Just remember to change the port in the `docker-compose` file!  

`SAME` is a space-separated list of SAME codes to monitor alerts for. For example: `112233 223344 665544 998877`.  

`WEBHOOK_URL` is a URL to send POST requests to when an alert is received.  

If authorization is required, set the `WEBHOOK_AUTHORIZATION` environment variable, and include `Bearer` or any other term that is needed. For example: `Bearer tokenhere`.

See the `docker-compose.yml` file in the `examples` directory for more information.

## Dependencies
Some sort of source of alerts is required. [RTLSDR-Airband](https://github.com/charlie-foxtrot/RTLSDR-Airband) using a UDP output is one way to do it. See the [wiki page](https://github.com/charlie-foxtrot/RTLSDR-Airband/wiki/Configuring-UDP-outputs) for how to configure it. The port for `eas-notifier` is `4898` by default.

All other software dependencies are installed by the Dockerfile on build. The image is built around Arch Linux, for no real reason other than up-to-date packages and familiarity.

## Output
The output JSON is the raw output from `dsame3`. There are some example outputs in the `examples` directory. The test is output from the sample audio provided by `dsame3`, while the thunderstorm one is from my local office.
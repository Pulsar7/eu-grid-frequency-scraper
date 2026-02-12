<h1>eu-grid-frequency-scraper</h1>

> [!IMPORTANT]
> The script only uses one source of information and depends on a functioning internet-connection.

A simple Python script, that scrapes the current frequency of the **EU-Grid** from this **API**: [https://dat.netzfrequenzmessung.de:9080/frequenz.xml](https://dat.netzfrequenzmessung.de:9080/frequenz.xml).
It sends alert-messages of two different types (**WARNING** or **CRITICAL**) when the parsed frequency has been reached or exceeded the configured thresholds.

## Table of contents

- [Table of contents](#table-of-contents)
- [Alert-Thresholds](#alert-thresholds)
  - [WARNING Alert-Threshold](#warning-alert-threshold)
  - [CRITICAL Alert-Threshold](#critical-alert-threshold)
- [NTFY](#ntfy)
- [Netzfrequenz-API](#netzfrequenz-api)
- [Installation](#installation)
  - [Prepare env \& Install dependencies](#prepare-env--install-dependencies)
- [Usage](#usage)
  - [Create systemd-timed-service (*recommended*)](#create-systemd-timed-service-recommended)
- [Future plans](#future-plans)


## Alert-Thresholds

There are two types of configurable frequency Alert-thresholds:

- **WARNING**
- **CRITICAL**

### WARNING Alert-Threshold

| Env value-name | Default value | Description |
|:---|:--:|:---|
|`WARNING_MIN_HZ_ALERT_THRESHOLD`|`"49.850"`|The minimum frequency (in **Hz**) that triggers a **WARNING** alert.|
|`WARNING_MAX_HZ_ALERT_THRESHOLD`|`"50.150"`|The maximum frequency (in **Hz**) that triggers a **WARNING** alert.|

### CRITICAL Alert-Threshold

| Env value-name | Default value | Description |
|:---|:--:|:---|
|`CRITICAL_MIN_HZ_ALERT_THRESHOLD`|`"49.600"`|The minimum frequency (in **Hz**) that triggers a **CRITICAL** alert.|
|`CRITICAL_MAX_HZ_ALERT_THRESHOLD`|`"50.400"`|The maximum frequency (in **Hz**) that triggers a **CRITICAL** alert.|

## NTFY

> [!NOTE]
>
> [NTFY](https://ntfy.sh/) is a simple HTTP-based pub-sub notification service.
> 
> It can be self-hosted: [https://github.com/binwiederhier/ntfy](https://github.com/binwiederhier/ntfy)

| Env value-name | Default value | Description |
|:---|:--:|:---|
|`ENABLE_NTFY`|`false`|Whether to enable **NTFY**-alerts.|
|`NTFY_TOPIC_URL`|`""`|**URL** to the NTFY-topic where the alerts should be sent to. **Required** when `ENABLE_NTFY=true`.|
|`NTFY_AUTH_TOKEN`|`""`|**Authentication-Token** for the NTFY-topic. **Required** when `ENABLE_NTFY=true`|
|`NTFY_HTTP_REQUEST_TIMEOUT`|`10`|HTTP-request-**timeout** in **seconds**.|
|`NTFY_HTTP_REQUEST_CERT_VERIFY`|`false`|Whether to verify the SSL/TLS-Certificate of **NTFY**.|

## Netzfrequenz-API

| Env value-name | Default value | Description |
|:---|:--:|:---|
|`NETZFREQUENZ_DE_API_URL`|`""`|**URL** to the [netzfrequenzmessung.de](https://www.netzfrequenzmessung.de/)-API.|
|`API_HTTP_REQUEST_TIMEOUT`|`10`|HTTP-request-**timeout** in **seconds**.|
|`API_HTTP_REQUEST_CERT_VERIFY`|`true`|Whether to verify the SSL/TLS-Certificate of the **API**-URL.|

## Installation

### Prepare env & Install dependencies

```BASH
python3 -m venv .venv && source .venv/bin/activate && pip3 install -r requirements.txt
```

## Usage

### Create systemd-timed-service (*recommended*)

```BASH
# /etc/systemd/system/eu-grid-frequency-scraper.service
[Unit]
Description=eu-grid-frequency-scraper
After=network.target

[Service]
Type=simple
User=my-user
Group=my-user
WorkingDirectory=/home/my-user/eu-grid-frequency-scraper
ExecStart=/home/my-user/eu-grid-frequency-scraper/.venv/bin/python /home/my-user/eu-grid-frequency-scraper/scraper.py -l info
Restart=no
StandardOutput=journal
StandardError=journal
```

```BASH
# /etc/systemd/system/eu-grid-frequency-scraper.timer
[Unit]
Description=Run eu-grid-frequency-scraper

[Timer]
# Every two minutes starting from the minute 0
OnCalendar=*:0/2
Unit=eu-grid-frequency-scraper.service
Persistent=true

[Install]
WantedBy=timers.target
```

## Future plans

- [ ] Add **time-values**-database (e.g. **influxdb**)
  - [ ] Store parsed **frequency** and **timestamp** in db
  - [ ] Send (low priority) alert at the end of the day about lowest & highest 'measured' frequency

## Automation Specification: Notify When “Coolie (Tamil)” Tickets Open in Bengaluru

### 1. Overview

Build a headless script that periodically checks one or more ticketing sites for the “Coolie (Tamil)” listings in Bengaluru and alerts the user (via email, SMS, push, Slack, etc.) the moment tickets become available for booking.

### 2. Objectives

* Automate monitoring of ticket availability.
* Support multiple platforms (e.g. BookMyShow, PVR, Paytm Insider).
* Send a real-time notification on first detection.
* Run on a schedule (e.g. every 30 min until release).

### 3. Functional Requirements

1. **Platform Connectivity**

   * Fetch the “Coming Soon” or “Book Tickets” page for Coolie on each target site.
   * Handle authentication if required (API key or user login).
2. **Parsing & Detection**

   * Parse HTML (or JSON) to determine if a “Book Now” / “Buy Tickets” button/link is live.
   * Distinguish between “Coming Soon” vs. “Book Now.”
3. **Notification**

   * On first positive detection, send a one-time alert via one or more channels:

     * Email (SMTP)
     * SMS (Twilio)
     * Push notification (Pushover, Pushbullet)
     * Slack/Webhook
4. **State Management**

   * Persist state between runs to avoid duplicate alerts (e.g. save a file or DB flag).
5. **Scheduling**

   * Run in a cronjob or as a background service: configurable interval (e.g. 30 min).
   * Stop polling automatically once tickets are detected.

### 4. Non-Functional Requirements

* **Robustness:** Retry on transient network errors (exponential backoff).
* **Modularity:** Separate modules for fetch → parse → notify → state.
* **Configurability:** All URLs, selectors, credentials, intervals, and notification endpoints defined in a single config file (JSON/YAML).
* **Logging:** Log successful checks, errors, and notification events.
* **Security:** Securely store any API keys or credentials (e.g. environment variables).

### 5. Data Sources & Selectors

| Platform      | URL (Bengaluru)                                     | Detect Selector (CSS/XPath)                          |
| ------------- | --------------------------------------------------- | ---------------------------------------------------- |
| BookMyShow    | `https://in.bookmyshow.com/bengaluru/movies/coolie` | button\[class\*="btn-primary"] innerText ≈ “Book”    |
| PVR Cinemas   | `https://www.pvrcinemas.com/movies/coolie`          | a.booknow\[href\*="/booking"]                        |
| Paytm Insider | `https://insider.in/coolie-tamil-bengaluru`         | div.reminder-button disappears / “Book Tickets” link |

*(Adjust URLs & selectors as needed.)*

### 6. Notification Channels

Define in config which channel(s) to enable, with corresponding credentials:

```yaml
notify:
  email:
    enabled: true
    smtp_server: smtp.gmail.com
    smtp_port: 587
    user: you@example.com
    pass_env_var: SMTP_PASSWORD
    to: me@example.com
  sms:
    enabled: false
    account_sid: ENV(TWILIO_SID)
    auth_token: ENV(TWILIO_TOKEN)
    from: "+1XXX"
    to: "+91YYY"
  slack:
    enabled: true
    webhook_url: ENV(SLACK_WEBHOOK)
```

### 7. Sequence Flow

1. **Load config & state**
2. **For each platform**

   1. Fetch page
   2. If HTTP error → retry/backoff
   3. Parse DOM for “Book” availability
   4. If available AND not yet alerted for this platform:

      * Send notification(s)
      * Mark state as “alerted”
3. **If any platform alerted → exit**
4. **Else → sleep until next interval**

### 8. Error Handling & Logging

* Log to console and/or file (`app.log`): timestamp, platform, status (OK/ERR), error message.
* On parse failure (selector not found), log warning but continue.
* On repeated HTTP 5xx, escalate or pause polling for that platform.

### 9. Deployment & Scheduling

* **Local:** Use `cron` (e.g. `*/30 * * * * /usr/bin/python3 /path/to/checker.py`).
* **Cloud VM / Docker:** Containerize script; use Cron or systemd timer.
* **Serverless (optional):** AWS Lambda + CloudWatch Events every 30 min.

### 10. Example LLM Prompt

> “Write a Python 3 script `ticket_alert.py` that implements the above spec.
>
> * Use `requests` + `beautifulsoup4` for fetching/parsing.
> * Use environment variables for credentials.
> * Use a local JSON file `state.json` to persist 'alerted' flags.
> * Send email via SMTP, Slack via webhook.
> * Include retry logic with exponential backoff.
> * Provide a sample `config.yaml`.
> * Include comments and logging statements.”

---

**How to use this doc:**

1. Copy the entire spec (all sections).
2. Paste as your prompt to an LLM (e.g. “Please generate the automation code based on this spec”).
3. The model will output a ready-to-run codebase (script + config + README).

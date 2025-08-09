# BookMyShow 403 Error Solutions

## Problem
BookMyShow blocks automated requests from GitHub Actions with 403 Forbidden errors. This is due to anti-bot protection mechanisms like Cloudflare.

## Solutions Implemented

### 1. Enhanced Headers & User-Agent Rotation
**File:** `bookmyshow_monitor_enhanced.py`
- Rotates between multiple user-agents
- Adds browser-like headers (Sec-Ch-Ua, DNT, etc.)
- Implements retry logic with exponential backoff
- Tries to get cookies from main page first

### 2. CloudScraper Library
**File:** `bookmyshow_cloudscraper.py`
- Uses cloudscraper library to bypass Cloudflare protection
- Automatically handles JavaScript challenges
- Simulates real browser behavior

### 3. Selenium with Undetected ChromeDriver
**File:** `bookmyshow_selenium.py`
- Uses real Chrome browser in headless mode
- Undetected-chromedriver bypasses bot detection
- Works well in GitHub Actions with proper setup

### 4. Proxy Support
**File:** `bookmyshow_proxy.py`
- Uses free proxy servers to rotate IP addresses
- Bypasses IP-based rate limiting
- Falls back to direct connection if proxies fail

### 5. Multi-Approach Workflow
**File:** `.github/workflows/ticket-monitor-multi.yml`
- Runs multiple approaches in parallel
- Continues even if one approach fails
- Maximizes chances of successful monitoring

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set GitHub Secrets
- `EMAIL_FROM`: Your email address
- `EMAIL_TO`: Recipient email address
- `EMAIL_PASSWORD`: Email app password

### 3. Run Locally
```bash
# Enhanced version
python bookmyshow_monitor_enhanced.py --once

# CloudScraper version
python bookmyshow_cloudscraper.py

# Selenium version
python bookmyshow_selenium.py

# Proxy version
python bookmyshow_proxy.py
```

### 4. Deploy to GitHub Actions
Use the multi-approach workflow:
```yaml
name: Multi-Approach Ticket Monitor
on:
  schedule:
    - cron: '*/30 * * * *'  # Every 30 minutes
  workflow_dispatch:
```

## Recommendations

1. **Use CloudScraper First**: It's the most reliable for bypassing Cloudflare
2. **Selenium as Backup**: More resource-intensive but very effective
3. **Rotate Approaches**: Don't use the same method repeatedly
4. **Monitor Logs**: Check GitHub Actions logs for which approach works
5. **Use VPN/Proxy Services**: Consider paid proxy services for production

## Alternative Approaches

If automated monitoring continues to fail:

1. **Use Official APIs**: Check if BookMyShow offers official APIs
2. **Mobile App Monitoring**: Monitor mobile app endpoints (often less protected)
3. **Browser Extensions**: Create a browser extension for client-side monitoring
4. **Manual Checks + Notifications**: Set up manual checks with push notifications
5. **Third-Party Services**: Use services like Distill.io or Visualping

## Important Notes

- BookMyShow actively blocks bots to prevent ticket scalping
- Respect rate limits and terms of service
- These solutions are for personal use only
- Consider the ethical implications of automated monitoring
- Always verify availability manually before making purchases

## Troubleshooting

### 403 Errors Continue
- Try different proxy services
- Increase delays between requests
- Use residential proxies instead of datacenter proxies

### Selenium Fails in GitHub Actions
- Ensure Chrome/Chromium is installed
- Use `--no-sandbox` flag for Docker environments
- Check GitHub Actions runner has sufficient resources

### CloudScraper Not Working
- Update to latest version
- Try different browser profiles
- Check if Cloudflare protection has been updated

## Success Metrics

The enhanced solutions should:
- Successfully access BookMyShow pages in 70%+ attempts
- Send email alerts when target screens are detected
- Work reliably in GitHub Actions environment
- Rotate between methods to avoid detection
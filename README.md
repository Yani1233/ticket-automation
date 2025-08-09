# 🎬 Coolie Ticket Monitor

Automated BookMyShow ticket monitoring for Coolie movie in specific PVR screens in Bengaluru.

## 🎯 Target Screens

- **PVR Soul Spirit** (Central Mall, Bellandur)
- **PVR Centro Mall**
- **PVR Nexus Koramangala**  
- **PVR Felicity Mall**

## 🚀 Features

- **Automated Monitoring**: Runs every 5 minutes during booking hours (9 AM - 11 PM IST)
- **Smart Detection**: Detects when booking opens for target screens
- **Email Alerts**: Instant notifications when tickets become available
- **GitHub Actions**: Fully automated cloud monitoring

## ⚙️ Setup

### 1. GitHub Secrets Configuration

Add these secrets to your GitHub repository:

```
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
EMAIL_TO=notification-email@gmail.com
```

### 2. Gmail App Password Setup

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Generate an App Password for "Mail"
4. Use this 16-character password as `EMAIL_PASSWORD`

## 🎬 Monitoring Details

- **Movie**: Coolie (Rajinikanth)
- **Date**: August 14, 2025
- **URL**: https://in.bookmyshow.com/movies/bengaluru/coolie/buytickets/ET00395817/20250814
- **Schedule**: Every 5 minutes during 9 AM - 11 PM IST

## 📧 Alert Types

1. **🚨 BOOKING OPEN**: Your target screens are live with showtimes
2. **⏰ BOOKING OPENING**: Other cinemas are active, targets should be soon
3. **📍 SCREENS DETECTED**: Target screens found but not active yet

## 🔧 Local Usage
```bash
# Install dependencies
pip install -r requirements.txt

# Single check
python bookmyshow_monitor.py --once

# Continuous monitoring (every 5 minutes)
python bookmyshow_monitor.py --continuous 5
```

## 📁 Repository Structure

```
ticket-automation/
├── bookmyshow_monitor.py      # Main monitoring script
├── requirements.txt           # Python dependencies
├── .github/workflows/         # GitHub Actions automation
│   └── coolie-monitor.yml     # Monitoring workflow
├── .env.template              # Environment variables template
└── README.md                  # This file
```

## 🎫 How It Works

1. **Page Analysis**: Scrapes BookMyShow page for cinema listings
2. **Pattern Detection**: Looks for showtimes and booking indicators
3. **Target Matching**: Identifies your preferred PVR screens
4. **Status Evaluation**: Determines booking availability status
5. **Alert System**: Sends email when targets become available

## � GitHub Actions Workflow

The monitor runs automatically via GitHub Actions:

- **Trigger**: Every 5 minutes during booking hours
- **Environment**: Ubuntu with Python 3.11
- **Timeout**: 10 minutes max per run
- **Logs**: Uploaded on failure for debugging

## 🎉 Success Scenario

When booking opens for your target screens:

1. ✅ Monitor detects target screen availability
2. 📧 Email alert sent immediately with details
3. 🎬 Direct booking URL provided
4. ⏰ Showtimes listed (if available)

## �️ Troubleshooting

- **No alerts**: Check GitHub Actions logs for errors
- **Email issues**: Verify Gmail app password and settings
- **False positives**: Monitor may detect cinemas in footer (expected)
- **Rate limiting**: Built-in delays and retry logic included

---

**🎬 Ready to book Coolie tickets as soon as they're available! �**
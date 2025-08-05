# Movie Ticket Alert System

Automated monitoring and alert system for movie ticket availability across multiple platforms. Originally built for "Coolie (Tamil)" but configurable for any movie.

## 📁 Project Structure

```
ticket-alert/
├── src/
│   └── ticket_alert/
│       ├── __init__.py
│       ├── core.py          # Main monitoring logic
│       ├── notifiers.py     # Email/notification handlers
│       └── cli.py           # Command-line interface
├── configs/
│   ├── coolie.yaml          # Coolie movie configuration
│   └── test_movies.yaml     # Test configuration
├── tests/
│   ├── test_email.py        # Email functionality tests
│   ├── test_simulation.py   # Alert simulation tests
│   └── test_integration.py  # Integration tests
├── scripts/
│   └── run.sh              # Convenience runner script
├── logs/                   # Log files (auto-created)
├── .github/
│   └── workflows/
│       └── ticket-monitor.yml
├── requirements.txt
├── setup.py
├── Dockerfile
├── railway.json
└── README.md
```

## 🎬 Features

- **Multi-platform monitoring**: BookMyShow, PVR Cinemas, Paytm Insider
- **Email notifications**: Instant alerts when tickets become available
- **Smart state management**: Prevents duplicate alerts
- **Robust error handling**: Retry logic with exponential backoff
- **Multiple deployment options**: GitHub Actions, Railway, Docker

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/ticket-alert.git
cd ticket-alert
```

2. **Set up environment**:
```bash
# Option 1: Use the convenience script
./scripts/run.sh --once

# Option 2: Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

3. **Configure credentials**:
```bash
cp .env.example .env
# Edit .env with your email credentials
```

### Usage

```bash
# Run once
./scripts/run.sh --once

# Continuous monitoring
./scripts/run.sh

# Use specific config
./scripts/run.sh --config configs/test_movies.yaml

# Test email setup
./scripts/run.sh --test-email

# Verbose logging
./scripts/run.sh --verbose
```

## 📧 Email Setup

### Gmail Configuration (IMPORTANT!)
1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**: 
   - Go to Google Account → Security → 2-Step Verification → App Passwords
   - Select "Mail" and your device
   - Copy the 16-character password (format: xxxx xxxx xxxx xxxx)
3. **Use the App Password** in `EMAIL_PASSWORD` (NOT your regular Gmail password)
   - Remove spaces from the app password when entering it

### Environment Variables
```bash
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@gmail.com  
EMAIL_PASSWORD=your-16-digit-app-password
```

## ☁️ Free Deployment Options

### Option 1: GitHub Actions (Recommended)
**✅ Completely free, runs every 30 minutes**

1. Fork this repository
2. Add secrets in GitHub repo: Settings → Secrets and Variables → Actions
   - `EMAIL_FROM`
   - `EMAIL_TO` 
   - `EMAIL_PASSWORD`
3. The workflow runs automatically every 30 minutes from 9 AM to 11 PM IST

### Option 2: Railway
**✅ 500 hours/month free**

1. Connect GitHub to Railway
2. Deploy from repository
3. Add environment variables in Railway dashboard
4. Set service type to "Worker"

### Option 3: Docker (Any platform)
```bash
docker build -t ticket-alert .
docker run -e EMAIL_FROM=your@email.com -e EMAIL_TO=recipient@email.com -e EMAIL_PASSWORD=password ticket-alert
```

## ⚙️ Configuration

Configuration files are stored in `configs/` directory:

### Example Configuration (configs/coolie.yaml)

```yaml
email:
  smtp_server: smtp.gmail.com
  smtp_port: 587
  from_email: ENV:EMAIL_FROM
  to_email: ENV:EMAIL_TO
  password: ENV:EMAIL_PASSWORD

check_interval_minutes: 30

platforms:
  - name: "BookMyShow"
    url: "https://in.bookmyshow.com/movies/bengaluru/coolie/ET00395817"
    selector: "button[data-phase='postRelease']"
    detection_method: "element_exists"
    keywords: ["book tickets", "show times"]
```

## 📊 Monitoring

- Logs are saved to `ticket_alert.log`
- State is persisted in `state.json`
- GitHub Actions uploads logs as artifacts

## 🔧 Advanced Usage

### Manual Test
```bash
python ticket_alert.py --once
```

### Custom Configuration
```bash
python ticket_alert.py --config custom-config.yaml
```

### Python API

```python
from ticket_alert import TicketAlert

# Create alert system
alert = TicketAlert(config_path="configs/coolie.yaml")

# Run single check
alert.run_check()

# Check status
state = alert.load_state()
print(f"Last check: {state.get('last_check')}")
print(f"Alerted platforms: {state.get('alerted_platforms', [])}")
```

## 🛠️ Troubleshooting

### Common Issues

1. **Email not sending**:
   - Verify Gmail App Password (16 digits, no spaces)
   - Check 2FA is enabled
   - Try with `less secure apps` enabled (not recommended)

2. **Selectors not working**:
   - Movie URLs may change
   - Update selectors in `config.yaml`
   - Check browser developer tools for current selectors

3. **GitHub Actions not running**:
   - Check workflow is enabled in Actions tab
   - Verify secrets are set correctly
   - Check workflow logs for errors

### Update Selectors
When movie pages change, update `config.yaml`:
```yaml
platforms:
  - name: "BookMyShow"
    url: "https://in.bookmyshow.com/bengaluru/movies/coolie"
    selector: ".new-book-button-class"  # Updated selector
```

## 📝 Logs
Monitor the system with:
```bash
tail -f ticket_alert.log
```

## 🔐 Security
- Never commit `.env` file
- Use environment variables for all credentials
- App passwords are safer than regular passwords

## 📱 Future Enhancements
- SMS notifications via Twilio
- Slack/Discord webhooks  
- Telegram bot integration
- Multiple cities support
- Web dashboard

## 🤝 Contributing
Feel free to submit issues and pull requests to improve the system!

---
**Happy movie booking! 🍿**
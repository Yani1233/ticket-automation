# 🎬 Coolie Ticket Monitor

An automated ticket monitoring system for the movie "Coolie" that tracks ticket availability on BookMyShow and District.in platforms and sends instant notifications via email and voice calls when tickets become available at your preferred theaters.

## ✨ Features

- **Dual Platform Monitoring**: Simultaneously monitors BookMyShow and District.in
- **Smart Detection**: Accurately identifies when tickets become available at specific theaters
- **Instant Notifications**: 
  - 📧 Email alerts to multiple recipients
  - 📞 Automated voice calls via Twilio
- **Configurable Targets**: Monitor specific theaters of your choice
- **Anti-Detection**: Built-in session management and rate limiting protection
- **Continuous Operation**: Runs 24/7 with automatic error recovery
- **No False Positives**: Strict validation to ensure only real bookings trigger alerts

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Gmail account for sending notifications
- Twilio account for voice calls (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ticket-automation.git
cd ticket-automation
```

2. **Set up virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure settings**
```bash
cp .env.template .env
# Edit .env with your configuration
```

5. **Run the monitor**
```bash
./run.sh  # On Unix/Mac
# OR
python3 run.py  # On any platform
```

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file from the template and configure:

```bash
# Email Configuration
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password  # Use Gmail App Password
EMAIL_TO=recipient1@gmail.com,recipient2@gmail.com

# Target Theaters (comma-separated)
TARGET_SCREENS=PVR Soul Spirit,PVR Centro Mall,PVR Nexus Koramangala

# Monitoring Settings
CHECK_INTERVAL_MINUTES=5

# Twilio Configuration (Optional for voice calls)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_STUDIO_FLOW_SID=your-studio-flow-sid
TWILIO_PHONE_NUMBER=+1234567890
VOICE_CALL_TO=+919876543210,+919876543211
ENABLE_VOICE_CALLS=true
```

### Gmail App Password Setup

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to Security → 2-Step Verification → App passwords
3. Generate a new app password for "Mail"
4. Use this password in the `EMAIL_PASSWORD` field

### Twilio Setup (Optional)

1. Create a [Twilio account](https://www.twilio.com/try-twilio)
2. Get your Account SID and Auth Token from the Twilio Console
3. Set up a Studio Flow for voice calls or use the default SMS functionality
4. Add your Twilio phone number and recipient numbers

## 📖 Usage

### Running the Monitor

You have multiple options to run the monitor:

#### Option 1: Main Runner (Recommended)
```bash
# Runs both monitors in parallel threads
./run.sh                    # Unix/Mac
python3 run.py              # Cross-platform
.venv/bin/python3 main.py   # Direct execution
```

#### Option 2: Sequential Mode
```bash
# Runs monitors one after another (uses less resources)
python3 run_continuous.py
```

#### Option 3: One-time Check
```bash
# Check once and exit
python3 bookmyshow_monitor.py --once
```

### Monitoring Status

When running, you'll see real-time status updates:

```
======================================================================
🚀 COOLIE TICKET AUTOMATION SYSTEM
======================================================================
📱 Platforms: BookMyShow + District.in
🎬 Movie: Coolie (Tamil)
📍 Location: Bengaluru
======================================================================

🎯 TARGET SCREENS (3):
   • PVR Soul Spirit
   • PVR Centro Mall
   • PVR Nexus Koramangala

📧 EMAIL RECIPIENTS (2):
   • email1@gmail.com
   • email2@gmail.com

⏰ Check Interval: Every 5 minutes
======================================================================

[10:30:15] 🔍 Starting check...
[10:30:16] 📱 Checking BookMyShow...
[10:30:18] ⏳ BookMyShow: No tickets yet
[10:30:20] 🎭 Checking District.in...
[10:30:22] ⏳ District.in: No tickets yet

💤 Next check at 10:35:15 (in 5 minutes)
```

### When Tickets Are Found

The system will:
1. 🎉 Display success message in console
2. 📧 Send detailed email with booking links
3. 📞 Make voice calls (if enabled)
4. Continue monitoring for other screens

## 🏗️ Project Structure

```
ticket-automation/
├── main.py                 # Main runner with threading
├── bookmyshow_monitor.py   # BookMyShow platform monitor
├── district_monitor.py     # District.in platform monitor
├── run_continuous.py       # Sequential runner alternative
├── run.py                  # Cross-platform launcher
├── run.sh                  # Unix/Mac quick start script
├── requirements.txt        # Python dependencies
├── .env.template          # Configuration template
├── .env                   # Your configuration (git-ignored)
└── logs/                  # Application logs (git-ignored)
```

## 🔧 Advanced Configuration

### Adding/Removing Target Theaters

Edit the `TARGET_SCREENS` in your `.env` file:

```bash
# For PVR screens
TARGET_SCREENS=PVR Soul Spirit,PVR VR Mall,PVR Phoenix

# For mixed theaters
TARGET_SCREENS=PVR Forum Mall,INOX Mantri,Cinepolis ETA
```

### Adjusting Check Frequency

Modify `CHECK_INTERVAL_MINUTES` in `.env`:

```bash
CHECK_INTERVAL_MINUTES=3  # Check every 3 minutes (more frequent)
CHECK_INTERVAL_MINUTES=10 # Check every 10 minutes (less frequent)
```

### Disabling Voice Calls

Set `ENABLE_VOICE_CALLS=false` in `.env` to use only email notifications.

## 🐛 Troubleshooting

### Common Issues

1. **No notifications received**
   - Check your Gmail app password is correct
   - Ensure target theaters are spelled correctly
   - Verify internet connectivity

2. **Rate limiting errors**
   - The system has built-in rate limiting protection
   - If persistent, increase `CHECK_INTERVAL_MINUTES`

3. **Session expired errors**
   - The monitors automatically refresh sessions
   - Restart the application if issues persist

### Logs

Check the `logs/` directory for detailed debugging information:
```bash
tail -f logs/monitor_20250811.log
```

## 📝 How It Works

1. **Session Initialization**: Creates authenticated sessions with both platforms
2. **Page Fetching**: Retrieves ticket booking pages every 5 minutes
3. **Smart Detection**: 
   - Searches for target theater names
   - Validates Coolie movie context
   - Confirms booking availability
   - Extracts showtimes
4. **Validation**: Prevents false positives with multi-level checks
5. **Notification**: Sends alerts only for confirmed bookings
6. **Continuous Loop**: Repeats until manually stopped

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## ⚠️ Disclaimer

This tool is for personal use only. Please:
- Respect the platforms' terms of service
- Don't use excessive check frequencies
- Use responsibly and ethically

## 📄 License

MIT License - feel free to use and modify as needed.

## 🙏 Acknowledgments

- Built with Python, BeautifulSoup, and Requests
- Email notifications via SMTP
- Voice calls powered by Twilio

---

**Note**: This tool monitors ticket availability but does not automatically purchase tickets. You'll need to manually complete the booking when notified.
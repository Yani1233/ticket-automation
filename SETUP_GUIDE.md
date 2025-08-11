# 🎬 Coolie Ticket Monitor - Complete Setup Guide

A step-by-step guide for setting up the ticket monitoring system from scratch, including Python installation.

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Step 1: Install Python](#step-1-install-python)
3. [Step 2: Download the Application](#step-2-download-the-application)
4. [Step 3: Set Up Gmail](#step-3-set-up-gmail)
5. [Step 4: Configure the Application](#step-4-configure-the-application)
6. [Step 5: Run the Monitor](#step-5-run-the-monitor)
7. [Troubleshooting](#troubleshooting)

---

## 📱 System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux
- **Internet Connection**: Required for monitoring and notifications
- **Gmail Account**: For sending email alerts
- **Storage**: ~100 MB free space
- **RAM**: Minimum 512 MB

---

## Step 1: Install Python

### 🪟 **For Windows Users**

1. **Download Python**
   - Go to https://www.python.org/downloads/
   - Click the yellow "Download Python 3.12.x" button
   - Save the installer

2. **Install Python**
   - Run the downloaded installer
   - ⚠️ **IMPORTANT**: Check ✅ "Add Python to PATH" at the bottom
   - Click "Install Now"
   - Wait for installation to complete
   - Click "Close"

3. **Verify Installation**
   - Press `Win + R`, type `cmd`, press Enter
   - Type: `python --version`
   - You should see: `Python 3.12.x`

### 🍎 **For Mac Users**

1. **Install Homebrew** (if not already installed)
   - Open Terminal (Cmd + Space, type "Terminal")
   - Paste this command:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   - Follow the prompts

2. **Install Python**
   ```bash
   brew install python3
   ```

3. **Verify Installation**
   ```bash
   python3 --version
   ```

### 🐧 **For Linux Users**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip
```

**Verify:**
```bash
python3 --version
```

---

## Step 2: Download the Application

### Option A: Download as ZIP (Easiest)

1. **Download the Code**
   - Go to the repository: https://github.com/yourusername/ticket-automation
   - Click the green "Code" button
   - Click "Download ZIP"
   - Extract the ZIP file to your Desktop or Documents folder

2. **Open Terminal/Command Prompt in the Folder**
   
   **Windows:**
   - Open the extracted folder
   - Hold Shift + Right-click in the folder
   - Select "Open PowerShell window here" or "Open command window here"
   
   **Mac:**
   - Open Terminal
   - Type `cd ` (with space)
   - Drag the extracted folder to Terminal
   - Press Enter
   
   **Linux:**
   - Right-click in the folder → "Open in Terminal"

### Option B: Using Git (Advanced)

If you have Git installed:
```bash
git clone https://github.com/yourusername/ticket-automation.git
cd ticket-automation
```

---

## Step 3: Set Up Gmail

You need a Gmail "App Password" for the monitor to send emails.

### 📧 Create Gmail App Password

1. **Go to Google Account Settings**
   - Visit: https://myaccount.google.com/
   - Sign in to your Gmail account

2. **Enable 2-Step Verification**
   - Click "Security" in the left menu
   - Find "2-Step Verification"
   - Click it and follow the setup (if not already enabled)

3. **Generate App Password**
   - After enabling 2-Step Verification
   - Go back to Security settings
   - Click "2-Step Verification" again
   - Scroll down and click "App passwords"
   - Select "Mail" from the dropdown
   - Select "Other" for device
   - Type: "Ticket Monitor"
   - Click "Generate"
   - **COPY THE 16-CHARACTER PASSWORD** (looks like: abcd efgh ijkl mnop)
   - Save it somewhere safe!

---

## Step 4: Configure the Application

### 🔧 Create Configuration File

1. **Copy the Template**
   
   **Windows (Command Prompt):**
   ```cmd
   copy .env.template .env
   ```
   
   **Mac/Linux:**
   ```bash
   cp .env.template .env
   ```

2. **Edit the Configuration**
   
   **Windows:**
   - Right-click on `.env` file
   - Open with Notepad
   
   **Mac:**
   - Right-click on `.env` file
   - Open with TextEdit
   
   **Linux:**
   - Use any text editor (gedit, nano, vim)

3. **Fill in Your Details**

   Replace the placeholder values with your actual information:

   ```bash
   # Your Gmail address
   EMAIL_USER=yourname@gmail.com
   
   # The 16-character app password from Step 3 (remove spaces)
   EMAIL_PASSWORD=abcdefghijklmnop
   
   # Email addresses to receive alerts (comma-separated)
   EMAIL_TO=yourname@gmail.com,friend@gmail.com
   
   # Theaters you want to monitor
   TARGET_SCREENS=PVR Soul Spirit,PVR Forum Mall,INOX Mantri
   
   # How often to check (in minutes)
   CHECK_INTERVAL_MINUTES=5
   
   # Leave Twilio settings empty if not using voice calls
   ENABLE_VOICE_CALLS=false
   ```

4. **Save the File**
   - Save and close the editor
   - Make sure the file is named `.env` (not `.env.txt`)

---

## Step 5: Run the Monitor

### 🚀 First-Time Setup

1. **Install Dependencies**
   
   **Windows:**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   
   **Mac/Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the Monitor**
   
   **Windows:**
   ```cmd
   python main.py
   ```
   
   **Mac/Linux:**
   ```bash
   python3 main.py
   ```

### ✅ What You Should See

If everything is working:
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
   • PVR Forum Mall
   • INOX Mantri

📧 EMAIL RECIPIENTS (2):
   • yourname@gmail.com
   • friend@gmail.com

⏰ Check Interval: Every 5 minutes
======================================================================

[10:30:15] 🔍 Starting check...
[10:30:16] 📱 Checking BookMyShow...
[10:30:18] ⏳ BookMyShow: No tickets yet
```

### 🛑 To Stop the Monitor

Press `Ctrl + C` (same on all systems)

---

## 🔄 Running Again Later

After the first setup, running is simpler:

### Windows:
1. Open the folder
2. Double-click `run.py`
OR
3. Open Command Prompt in folder and type: `python run.py`

### Mac/Linux:
1. Open Terminal in the folder
2. Type: `./run.sh` or `python3 run.py`

---

## ❓ Troubleshooting

### Common Issues and Solutions

#### 1. "Python not found" Error
**Solution:** Python isn't installed or not in PATH
- Reinstall Python and check "Add to PATH"
- Restart your computer after installation

#### 2. "No module named 'requests'" Error
**Solution:** Dependencies not installed
```bash
pip install -r requirements.txt
```

#### 3. "Permission denied" Error (Mac/Linux)
**Solution:** Make scripts executable
```bash
chmod +x run.sh
./run.sh
```

#### 4. Gmail Authentication Failed
**Solution:** Check your app password
- Make sure you're using the 16-character app password (not your regular password)
- Remove any spaces from the app password
- Ensure 2-Step Verification is enabled

#### 5. No Emails Received
**Solution:** Check configuration
- Verify EMAIL_TO addresses are correct
- Check spam/junk folder
- Ensure target theater names match exactly

#### 6. ".env file not found" Error
**Solution:** Configuration file missing
- Make sure you copied `.env.template` to `.env`
- Check you're in the right folder

---

## 💡 Tips for Success

1. **Test First**: Run once to ensure everything works before leaving it running
2. **Check Spam**: First emails might go to spam - mark as "Not Spam"
3. **Theater Names**: Must match exactly as shown on BookMyShow/District.in
4. **Keep Running**: Leave the terminal/command prompt window open
5. **Background Running**: On Mac/Linux, use `nohup python3 main.py &` to run in background

---

## 📞 Getting Help

If you encounter issues:

1. **Check the Logs**: Look in the `logs` folder for error details
2. **Verify Configuration**: Double-check your `.env` file
3. **Test Email**: Try with just one email address first
4. **Restart**: Sometimes a fresh start helps

---

## 🎉 Success Checklist

- [ ] Python installed and working
- [ ] Application downloaded and extracted
- [ ] Gmail app password generated
- [ ] `.env` file configured with your details
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Monitor running and checking every 5 minutes
- [ ] Test email received (when tickets are found)

---

## 📝 Quick Command Reference

| Task | Windows | Mac/Linux |
|------|---------|-----------|
| Check Python | `python --version` | `python3 --version` |
| Install deps | `pip install -r requirements.txt` | `pip3 install -r requirements.txt` |
| Run monitor | `python main.py` | `python3 main.py` |
| Stop monitor | `Ctrl + C` | `Ctrl + C` |
| Quick run | Double-click `run.py` | `./run.sh` |

---

**Congratulations! Your ticket monitor is now set up and running! 🎬**

When tickets become available at your target theaters, you'll receive an email alert immediately. Make sure to book quickly as popular shows sell out fast!

---

*Note: This tool only monitors and notifies - it doesn't automatically purchase tickets. You'll need to manually complete the booking when alerted.*
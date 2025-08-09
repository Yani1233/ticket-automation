# GitHub Actions Secrets Setup Guide

## 🔐 Required Secrets for BookMyShow Monitor

To set up automated monitoring via GitHub Actions, add these secrets to your repository:

### 📍 How to Add Secrets:
1. Go to: https://github.com/Yani1233/ticket-automation
2. Click **Settings** tab
3. Navigate to **Secrets and variables** → **Actions**
4. Click **"New repository secret"** for each secret below

### 🔑 Required Secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `EMAIL_USER` | `raja.arun91@gmail.com` | Gmail account for sending alerts |
| `EMAIL_PASSWORD` | `psal kdur pulb emep` | Gmail app password |
| `EMAIL_TO` | `arunrajadh@gmail.com` | Email to receive ticket alerts |
| `EMAIL_SMTP_SERVER` | `smtp.gmail.com` | Gmail SMTP server |
| `EMAIL_SMTP_PORT` | `587` | Gmail SMTP port |

### ⚡ Workflow Features:
- **Automated**: Runs every 5 minutes during booking hours (9 AM - 11 PM IST)
- **Manual trigger**: Can be triggered manually from Actions tab
- **PVR focused**: Monitors your 4 preferred PVR locations
- **Smart alerts**: Only sends email when target screens are ready

### 🎯 Target PVR Screens:
- PVR Soul Spirit (Central Mall, Bellandur)
- PVR Centro Mall
- PVR Nexus Koramangala  
- PVR Felicity Mall

### 🚀 Once configured:
1. Your monitor will run automatically in the cloud
2. You'll receive email alerts when booking opens
3. No need to run anything locally!

### 🧪 Test the Setup:
After adding secrets, you can manually trigger the workflow:
1. Go to **Actions** tab
2. Select "Coolie Ticket Monitor"
3. Click **"Run workflow"**
4. Check logs to verify everything works

Happy booking! 🎬✨

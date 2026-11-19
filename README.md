# 📅 Daily Calendar Telegram Bot

A Python bot that posts the Persian (Jalali) and Gregorian date to a Telegram channel every day at **8:00 AM Tehran time**.

It runs on **GitHub Actions** (no laptop or server needed), and **cron-job.org** handles the exact scheduling.

## Sample message

The bot posts in Persian:

```
📅 تقویم روز
━━━━━━━━━━━━━━

🇮🇷 تاریخ شمسی:
پنجشنبه ۲۸ آبان ۱۴۰۵

🌍 تاریخ میلادی:
Thursday ۱۹ November ۲۰۲۶

✨ روز خوبی داشته باشید ❤️
```

## How it works

```
cron-job.org (every day at 08:00 Tehran time)
        │  POST request to the GitHub API
        ▼
GitHub Actions (runs the workflow)
        │  python bot.py --send-once
        ▼
Calendar message appears in the Telegram channel
```

**Why not use GitHub's own `schedule` trigger?** Scheduled runs on GitHub are not guaranteed to be on time; they can be delayed by hours or skipped entirely. cron-job.org simply triggers the workflow at the exact time you choose.

## Files

| File | Purpose |
|------|---------|
| `bot.py` | The bot code |
| `requirements.txt` | Dependencies (`python-telegram-bot`, `jdatetime`) |
| `.github/workflows/daily-calendar.yml` | GitHub workflow (runs only when triggered externally or manually) |

## Setup

### 1. Create the bot and channel
1. Create a bot with `@BotFather` and copy its token.
2. Add the bot to your channel as an **admin** with permission to post messages.
3. Get the channel ID (`@channelusername` or a number like `-100...`).

### 2. Add Secrets in GitHub
Go to **Settings → Secrets and variables → Actions → New repository secret**:

| Name | Value |
|------|-------|
| `BOT_TOKEN` | Bot token from BotFather |
| `CHANNEL_ID` | Channel ID |

### 3. Manual test
Open the **Actions** tab, select the `Daily Persian Calendar` workflow, and click **Run workflow**. If the message appears in the channel, the token and Secrets are correct.

### 4. Create a GitHub token for cron-job.org
Go to **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**:

- **Repository access:** only this repository (`Only select repositories`)
- **Permissions → Actions:** `Read and write`
- **Expiration:** at most about one year. Note the date.

GitHub shows the token only once, so copy it immediately.

### 5. Create the schedule in cron-job.org
Create a new **Cronjob** with these values:

- **URL:**
  ```
  https://api.github.com/repos/<USERNAME>/<REPO>/actions/workflows/daily-calendar.yml/dispatches
  ```
  (Replace `<USERNAME>` and `<REPO>` with your GitHub username and repository name.)
- **Request method:** `POST`
- **Headers:**
  - `Authorization`: `Bearer <your GitHub token>`
  - `Accept`: `application/vnd.github+json`
  - `Content-Type`: `application/json`
- **Request body:**
  ```json
  {"ref":"main"}
  ```
- **Schedule:** every day at `08:00`, timezone `Asia/Tehran`

Then click **Test run**. A **204** response means success.

## Changing the send time
Just change the time of the job in **cron-job.org**. No code or workflow changes are needed, and no UTC conversion either.

## Renewing the GitHub token
Before the token expires, create a new one and update the `Authorization` header in cron-job.org. Otherwise the daily messages will stop.

## Running locally (optional)

```bash
pip install -r requirements.txt

# Linux / macOS
export BOT_TOKEN="..."
export CHANNEL_ID="..."

# Windows (PowerShell)
$env:BOT_TOKEN="..."
$env:CHANNEL_ID="..."

# Send one message and exit
python bot.py --send-once

# Run continuously with /today and /test commands
python bot.py
```

> The `/today` and `/test` commands only respond while the bot is running continuously (without `--send-once`) somewhere. The GitHub Actions version sends one message and exits.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No message arrived | Check **History** in cron-job.org (should be 204), then the **Actions** tab on GitHub |
| Error `401` or `403` | The token is wrong, expired, or lacks `Actions: Read and write` |
| Error `404` | The URL or workflow file name is wrong |
| Error `422` | The request body must be exactly `{"ref":"main"}` |
| Workflow run failed (red) | Open that run's log; usually `BOT_TOKEN` or `CHANNEL_ID` is wrong, or the bot is not an admin of the channel |
| Message sent twice | Make sure the `schedule:` section is removed from the workflow file |

## Security
- Never put the bot token or GitHub token in the code or repository files.
- Use only **GitHub Secrets** and the cron-job.org settings.
- If a token leaks, revoke it immediately and create a new one.

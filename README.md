<div align="center">

# 🤖 LightCore Discord Bot — Component V2


*A premium multipurpose Discord bot featuring high-end Antinuke, Automod, and next-gen UI.*

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.0+-green.svg)
![License](https://img.shields.io/badge/License-Proprietary-red.svg)

</div>

---

## ✨ What is LightCore?

**LightCore** is a state-of-the-art multipurpose Discord bot designed for performance and security. Powered by the **Component V2** architecture, LightCore delivers a premium user experience with sleek layouts and advanced functionality.

**Current Stats:**
- 🛠️ **99 Cogs** loaded with specialized logic.
- ⚡ **79 Commands** synchronized and ready for action.
- 🎨 **Component V2 UI**: Modern, interactive layouts using high-end Discord UI components.

## 🛡️ Key Features

- **Advanced Antinuke**: Protect your server from malicious actions (Channel/Role creation/deletion, kicks, bans, etc.).
- **Powerful Automod**: Keep your community safe with advanced filters for caps, links, invites, and spam.
- **Robust Moderation**: A full suite of moderation tools including ban, kick, warn, mute, and more.
- **Utility & Fun**: Feature-rich utility commands (Avatar, Userinfo, Membercount) and engaging fun features.
- **Auto-Initializing**: Seamless setup with automatic database and configuration generation.

## Quick Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your bot**
   - Create a `.env` file in the root directory.
   - Add your Discord bot token: `TOKEN=your_token_here`

3. **Owner Identification**
   - Edit `utils/config.py` to add your ID to `OWNER_IDS` for access to no-prefix and owner-only commands.

4. **Run the bot**
   ```bash
   python LightCore.py
   ```

## ☁️ Deploying on Render — Web Service (free tier)

A Discord bot is a background process, so Render's default web-service start command (`gunicorn your_application.wsgi`) fails with `gunicorn: command not found`. LightCore fixes that by opening a real HTTP port while it runs.

| Setting | Value |
| --- | --- |
| Type | **Web Service** |
| Runtime | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python LightCore.py` |
| Health Check Path | `/health` |
| Plan | Free (or higher) |

`render.yaml` in this repo already contains exactly that — **New → Blueprint → pick this repo** and it configures itself.

### Why the health server exists

`utils/health.py` binds `$PORT` (only when the variable is set) and serves:

| Path | Response |
| --- | --- |
| `/` | plain-text "LightCore is running." |
| `/health`, `/healthz` | JSON — `status`, `bot` tag, `guilds`, `latency_ms` |

The bot still talks to Discord over the gateway; the HTTP port exists purely so the host's port scan and health check pass. Locally nothing changes — no `PORT`, no listener.

### Environment variables

```env
TOKEN=your_bot_token        # required
OWNER_IDS=123456789012345678 # required for owner commands
BOT_PREFIX=&                 # optional, defaults to &
WEBHOOK_URL=                 # optional, command logging off when unset
GROQ_API_KEY=                # optional, AI commands
```

### Free-tier caveats (important)

1. **Spin-down.** Free instances sleep after a period without inbound traffic, which also drops the Discord gateway — commands go silent. Set a keep-alive so LightCore pings itself:
   ```env
   RENDER_EXTERNAL_URL          # set automatically by Render
   KEEP_ALIVE=1                 # default; set 0 to disable
   KEEP_ALIVE_INTERVAL=600      # seconds
   ```
   Or add a Render **Cron Job** hitting `https://<service>.onrender.com/health` every 10 minutes.
2. **Ephemeral disk.** SQLite files in `db/` reset on every deploy, so prefixes, levels and tickets vanish. Render → your service → **Disks** → Add Disk (mount e.g. `/var/data`, 1 GB). This repo reads the `db/` paths from the working directory, so the simplest fix is to create a symlink at build time:
   ```bash
   # Build Command
   pip install -r requirements.txt && mkdir -p /var/data/db && ln -sfn /var/data/db db
   ```
   Without a disk the bot still runs — it just forgets state between deploys.
3. **One service only.** Run a single instance — two processes sharing one bot token will double-respond to commands.
4. **Shutdown.** `SIGTERM` is handled so deploys close the gateway cleanly instead of crashing.

### Other hosts (Railway / Fly / VPS)

Any long-lived process works — no port or web framework required:

```bash
pip install -r requirements.txt
python LightCore.py
```

`Procfile` declares both `web:` and `worker:` entries, so platforms that read it pick the right one. `runtime.txt` pins Python 3.11.9.

## ⚙️ Configuration Guide

### ⚡ Bot Prefix 
Edit `BOT_PREFIX` in your `.env` file and restart the bot:
```env
BOT_PREFIX=!
```

### 📁 File Organization
- **Database files (.db)**: Automatically generated and located in the `db/` folder.
- **JSON Data**: Configuration and persistence data in `jsondb/`.

---

## 🏆 Credits

<div align="center">

### 👨‍💻 Development Team

**Developer:** LightCore  
**Discord:** `lightcore`  
**Community:** LightCore Development  
**Discord Server:** [discord.gg/8qe98sAGs9](https://discord.gg/8qe98sAGs9)

---

### 🏛️ Original Olympus Project

**🛡️ Olympus Bot License Agreement**

Based on the original Olympus Bot by Olympus Development.  
**Original Repository:** [olympus-bot](https://github.com/sonujana26/olympus-bot)  
**Discord Server:** [discord.gg/odx](https://discord.gg/odx) (Olympus Server)

*Original Olympus Bot © 2025 Olympus Development — All rights reserved.*

**License Terms:**
- Commercial Use: ❌ Not allowed without paid license from Olympus Team
- Redistribution: ❌ Forbidden. Do not host this code elsewhere  
- Modification: ❌ Not allowed unless licensed
- Patents/Derivatives: ❌ No rights to publish forks under any name

For licensing inquiries: https://discord.gg/odx

---

**Made with ❤️ by [LightCore Development](https://discord.gg/8qe98sAGs9)**

*Based on Olympus • Powered by Python & Discord.py • Component V2 Interface*

</div>

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

## ☁️ Deploying (Render / Railway / Fly)

A Discord bot is a **background worker**: it connects outbound to Discord and never opens a port. If your host runs `gunicorn your_application.wsgi` and dies with `gunicorn: command not found`, it is configured as a **web service** — there is no WSGI app here.

### Render — two supported setups

**Option A — Background Worker (recommended, paid instances)**

| Setting | Value |
| --- | --- |
| Type | **Background Worker** (not Web Service) |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python LightCore.py` |
| Plan | Starter or higher (workers are not on the free tier) |

**Option B — Web Service (works on the free tier)**

Set Type to **Web Service** and use the same commands. LightCore detects `$PORT`, serves `/` and `/health` on it, and runs the bot in the same process — so the health check passes and the deploy stays alive.

A `render.yaml` blueprint ships both options; keep one and delete the other.

### Environment variables (either option)

```env
TOKEN=your_bot_token            # required
OWNER_IDS=123456789012345678    # required for owner commands
BOT_PREFIX=&                    # optional, defaults to &
WEBHOOK_URL=                    # optional, command logging disabled if unset
GROQ_API_KEY=                   # optional, AI commands
```

`TOKEN` is the only hard requirement — the bot no longer refuses to start when `WEBHOOK_URL` or `BOT_PREFIX` are missing.

### Railway / Fly / VPS

Anywhere you can run a long-lived process:

```bash
pip install -r requirements.txt
python LightCore.py
```

No port or web framework is required.

### Notes

- `runtime.txt` pins Python 3.11.9 (3.12+ can break some dependencies).
- Data lives in local SQLite files under `db/`; on ephemeral filesystems (Render, Railway) attach a disk if you need persistence across deploys.


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

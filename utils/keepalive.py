"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )

    Optional self-ping keep-alive.

    Free web-service plans suspend an instance after a period without inbound
    HTTP traffic, which also stops the Discord gateway connection - commands go
    silent. Set KEEP_ALIVE_URL (or let it default to Render's
    RENDER_EXTERNAL_URL) and this task pings /health on an interval.

    Disable with KEEP_ALIVE=0.
"""

import asyncio
import os

import aiohttp

from utils.logger import logger

DEFAULT_INTERVAL = 600  # seconds


def _target():
    url = os.environ.get("KEEP_ALIVE_URL") or os.environ.get("RENDER_EXTERNAL_URL")
    if not url:
        return None
    url = url.rstrip("/")
    if not url.endswith("/health"):
        url = f"{url}/health"
    return url


async def start():
    """Start the keep-alive loop if configured. Returns the task or None."""
    if os.environ.get("KEEP_ALIVE", "1").strip().lower() in ("0", "false", "no"):
        return None
    url = _target()
    if url is None:
        return None

    try:
        interval = max(60, int(os.environ.get("KEEP_ALIVE_INTERVAL", DEFAULT_INTERVAL)))
    except ValueError:
        interval = DEFAULT_INTERVAL

    async def _loop():
        await asyncio.sleep(30)  # let the bot finish starting first
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                        logger.debug("KEEPALIVE", f"{url} -> {resp.status}")
            except Exception as e:
                logger.warn("KEEPALIVE", f"Ping failed: {e}")
            await asyncio.sleep(interval)

    logger.info("KEEPALIVE", f"Pinging {url} every {interval}s")
    return asyncio.create_task(_loop(), name="lightcore-keepalive")

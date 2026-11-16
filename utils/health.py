"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )

    Tiny HTTP health server.

    A Discord bot is a background worker and never binds a port, which means it
    can only run as a Render *worker* (paid). Hosts that only offer *web*
    services - Render free tier included - require the process to listen on
    $PORT or the deploy is killed.

    This module satisfies that requirement: when PORT is set we serve a few
    health endpoints while the bot keeps running in the same event loop.
    Nothing here is required for local use.
"""

import os

import logging

from aiohttp import web

# Render's health checks would otherwise flood the logs every few seconds.
logging.getLogger("aiohttp.access").setLevel(logging.WARNING)


async def _health(request):
    client = request.app["client"]
    try:
        user = client.user
    except Exception:
        user = None
    try:
        guilds = len(client.guilds)
    except Exception:
        guilds = 0
    return web.json_response({
        # 200 once the gateway is connected and the bot is not closed, so the
        # host's health check reflects the bot, not just a live port.
        "status": "ok" if user else "starting",
        "service": "lightcore",
        "bot": str(user) if user else None,
        "guilds": guilds,
        "latency_ms": round(client.latency * 1000) if user else None,
    })


async def _root(request):
    return web.Response(
        text="LightCore is running.\n"
             "This endpoint exists only so the host sees an open port.\n",
        content_type="text/plain",
    )


def _make_app(client=None):
    app = web.Application()
    app["client"] = client
    app.router.add_get("/", _root)
    app.router.add_get("/health", _health)
    app.router.add_get("/healthz", _health)
    return app


async def start(client=None):
    """Start the health server if PORT is set. Returns the runner or None."""
    port = os.environ.get("PORT")
    if not port:
        return None
    runner = web.AppRunner(_make_app(client))
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=int(port))
    await site.start()
    return runner

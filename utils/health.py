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

from aiohttp import web


async def _health(request):
    return web.json_response({"status": "ok", "service": "lightcore"})


async def _root(request):
    return web.Response(
        text="LightCore is running.\n"
             "This endpoint exists only so the host sees an open port.\n",
        content_type="text/plain",
    )


def _make_app():
    app = web.Application()
    app.router.add_get("/", _root)
    app.router.add_get("/health", _health)
    app.router.add_get("/healthz", _health)
    return app


async def start():
    """Start the health server if PORT is set. Returns the runner or None."""
    port = os.environ.get("PORT")
    if not port:
        return None
    runner = web.AppRunner(_make_app())
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=int(port))
    await site.start()
    return runner

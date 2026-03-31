import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import logging
from src.config import PORT

async def handle_root(request):
    return web.Response(text="Bot is running (Webhook Mode)")

async def start_webhook_server(bot: Bot, dp: Dispatcher):
    """
    Sets up and starts the aiohttp server for Webhooks within the existing event loop.
    """
    app = web.Application()
    
    # Add a simple health check route for Render
    app.router.add_get("/", handle_root)
    
    # Configure the webhook handler
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    # Register the webhook handler with the application
    webhook_handler.register(app, path="/webhook")
    
    # Final configuration for the aiohttp application
    setup_application(app, dp, bot=bot)
    
    # Start the runner
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    
    logging.info(f"Starting webhook server on port {PORT}")
    await site.start()
    
    # Keep the server running forever without blocking the main loop's other tasks
    await asyncio.Event().wait()

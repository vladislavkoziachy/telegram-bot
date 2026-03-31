import asyncio
from aiohttp import web
from src.config import PORT

async def handle_root(request):
    return web.Response(text="Bot is alive!")

async def start_keep_alive():
    app = web.Application()
    app.router.add_get("/", handle_root)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Фиктивный сервер запущен на порту {PORT}")

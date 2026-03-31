import asyncio
from gtts import gTTS
import os

async def generate_audio(text: str, filename: str) -> str:
    def _create_tts():
        # Force English as we only support EN learning now
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filename)
    
    await asyncio.to_thread(_create_tts)
    return filename

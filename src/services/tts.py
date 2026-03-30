import asyncio
from gtts import gTTS
import os

async def generate_audio(text: str, filename: str, lang: str = 'en') -> str:
    def _create_tts():
        # lang mapping: en -> en, pl -> pl, es -> es
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)
    
    await asyncio.to_thread(_create_tts)
    return filename

import os
import asyncio
import uuid
from gtts import gTTS
from aiogram import types

async def send_voice_pronunciation(message: types.Message, text: str):
    """Генерирует и отправляет голосовое сообщение с английским произношением."""
    # Создаем временное имя файла
    filename = f"voice_{uuid.uuid4()}.mp3"
    
    try:
        # Генерируем аудио (всегда на английском) в отдельном потоке
        tts = gTTS(text=text, lang='en')
        await asyncio.to_thread(tts.save, filename)
        
        # Отправляем аудио из файла
        voice_file = types.FSInputFile(filename)
        await message.answer_voice(voice_file)
        
    except Exception as e:
        print(f"Ошибка озвучки: {e}")
    finally:
        # Удаляем временный файл, если он существует
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

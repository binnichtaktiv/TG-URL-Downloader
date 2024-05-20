import os
import shutil
import requests
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

api_id = 'change-this'
api_hash = 'change-this'
bot_token = "change-this"
download_path = "change to you path"

app = Client("url-downloader", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text("Hello! Send me a URL and I will download the file for you")

@app.on_message(filters.text & filters.private)
async def download_file(client, message: Message):
    url = message.text
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        #get filename
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)

        with NamedTemporaryFile(delete=False) as temp_file:
            total_size = int(response.headers.get('content-length', 0))

            progress_message = await message.reply_text(f"Started downloading\n{filename}")

            downloaded_size = 0
            block_size = 1024
            last_update_time = time.time()
            for chunk in response.iter_content(chunk_size=block_size):
                downloaded_size += len(chunk)
                if chunk:
                    temp_file.write(chunk)

                if time.time() - last_update_time > 6 or downloaded_size == total_size:
                    progress = (downloaded_size / total_size) * 100
                    await progress_message.edit_text(f"Download progress: {progress:.2f}%")
                    last_update_time = time.time()

            final_file_path = os.path.join(download_path, filename)

        shutil.move(temp_file.name, final_file_path)
        await progress_message.edit_text(f"File downloaded successfully:\n{final_file_path}")

    except Exception as e:
        await message.reply_text(f"Error downloading file: {e}")

app.run()

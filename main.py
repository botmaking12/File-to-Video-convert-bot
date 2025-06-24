from pyrogram import Client, filters
from config import Config
from helpers.convert import convert_to_video, convert_to_file
from pymongo import MongoClient
import os
import asyncio
from datetime import datetime

bot = Client("convert-bot",
             api_id=Config.API_ID,
             api_hash=Config.API_HASH,
             bot_token=Config.BOT_TOKEN)

mongo = MongoClient(Config.MONGO_URI)
db = mongo[Config.MONGO_URI.split("/")[-1].split("?")[0]]
logs = db.logs

if not os.path.exists(Config.DOWNLOAD_DIR):
    os.makedirs(Config.DOWNLOAD_DIR)

@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 Welcome to File/Video Converter Bot.\nSend me any video or file.")

@bot.on_message(filters.video)
async def video_handler(client, message):
    if message.from_user.id not in Config.ADMINS:
        return await message.reply("⛔ Only authorized users can use this bot.")

    video = message.video
    filename = video.file_name or f"{datetime.now().timestamp()}.mp4"
    input_path = os.path.join(Config.DOWNLOAD_DIR, filename)

    status = await message.reply("📥 Downloading video...")
    await message.download(file_name=input_path)

    output_path = input_path.replace(".mp4", "_file.mp4")
    await convert_to_file(input_path, output_path)

    await status.edit("📤 Uploading as file...")
    await message.reply_document(output_path, caption="Converted from video to file 📁")

    os.remove(output_path)
    await status.delete()

@bot.on_message(filters.document)
async def document_handler(client, message):
    if message.from_user.id not in Config.ADMINS:
        return await message.reply("⛔ Only authorized users can use this bot.")

    doc = message.document
    filename = doc.file_name or f"{datetime.now().timestamp()}.bin"
    input_path = os.path.join(Config.DOWNLOAD_DIR, filename)

    status = await message.reply("📥 Downloading file...")
    await message.download(file_name=input_path)

    output_path = input_path.rsplit(".", 1)[0] + "_converted.mp4"
    await convert_to_video(input_path, output_path)

    await status.edit("📤 Uploading video...")
    await message.reply_video(output_path, caption="Converted from file to video 🎬")

    os.remove(input_path)
    os.remove(output_path)
    await status.delete()

@bot.on_message(filters.command("log"))
async def log_command(client, message):
    await client.send_message(Config.LOG_CHANNEL, f"User: {message.from_user.id} used /log command")

bot.run()

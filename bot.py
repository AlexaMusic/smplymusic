from pyrogram import Client, filters
from pyrogram.types import Message, Voice
import asyncio
import os
import time
import ffmpeg
from pytube import YouTube


# Create bot instance
api_id = int(os.environ.get("APP_ID")
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")
bot = Client(':memory:', api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Dictionary to store active voice chats
active_voice_chats = {}

# Handle "/play" command
@bot.on_message(filters.command('play'))
async def play_song(bot: Client, message: Message):
    # Check if the message is a reply to another message with a YouTube URL
    if message.reply_to_message and message.reply_to_message.video:
        youtube_url = message.reply_to_message.text
    else:
        youtube_url = message.text.split(' ', 1)[1]

    # Download the video using PyTube
    video = YouTube(youtube_url)
    video_stream = video.streams.filter(only_audio=True).first()
    video_stream.download(output_path='downloads', filename='song')

    # Convert the video to PCM format using ffmpeg
    input_file = ffmpeg.input('downloads/song.mp4')
    output_file = ffmpeg.output(input_file, 'pipe:', format='s16le', acodec='pcm_s16le', ac=2, ar='48k')
    process = output_file.run_async(pipe_stdout=True)

    # Start the voice chat and play the song
    chat_id = message.chat.id
    voice_chat = await bot.join_chat(chat_id)
    active_voice_chats[chat_id] = voice_chat
    while not voice_chat.is_connected:
        await asyncio.sleep(1)
    audio_stream = Voice(process.stdout)
    await voice_chat.play(audio_stream, title=video.title)

    # Delete the downloaded video file
    os.remove('downloads/song.mp4')

# Handle "/skip" command
@bot.on_message(filters.command('skip'))
async def skip_song(bot: Client, message: Message):
    chat_id = message.chat.id
    if chat_id in active_voice_chats:
        voice_chat = active_voice_chats[chat_id]
        await voice_chat.stop_playout()
        message.reply_text('Skipped the current song.')

# Handle "/end" command
@bot.on_message(filters.command('end'))
async def end_song(bot: Client, message: Message):
    chat_id = message.chat.id
    if chat_id in active_voice_chats:
        voice_chat = active_voice_chats[chat_id]
        await voice_chat.stop_playout()
        await voice_chat.leave()
        del active_voice_chats[chat_id]
        message.reply_text('Ended the song and left the voice chat.')

# Start the bot
bot.run()

from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient

# Create bot instance
bot = Client('5893160347:AAHfrd5QESVn1twJlt8m2kEEOwIhjponk3g')

# Connect to MongoDB
MONGODB_URL = "mongodb+srv://AlexaMusic:AlexaMusic@cluster0.ev6cioc.mongodb.net/?retryWrites=true&w=majority" # Replace with your MongoDB URL
client = MongoClient(MONGODB_URL)
db = client.telegram_bot_db
banned_users = db.banned_users

# Handle "/ban" command
@bot.on_message(filters.command('ban'))
def ban_user(bot: Client, message: Message):
    user_id = message.text.split(' ')[1] # Get user ID from command argument
    banned_user = {'user_id': user_id}
    banned_users.insert_one(banned_user) # Add user to banned users collection

    # Ban user in all groups and count the number of groups where the user was banned
    count = 0
    for chat in bot.iter_dialogs():
        if chat.chat.type == 'supergroup':
            try:
                bot.kick_chat_member(chat.chat.id, user_id)
                count += 1
            except:
                pass

    message.reply_text(f'{user_id} has been banned in {count} groups.')

# Handle "/unban" command
@bot.on_message(filters.command('unban'))
def unban_user(bot: Client, message: Message):
    user_id = message.text.split(' ')[1] # Get user ID from command argument
    banned_users.delete_one({'user_id': user_id}) # Remove user from banned users collection

    # Unban user in all groups and count the number of groups where the user was unbanned
    count = 0
    for chat in bot.iter_dialogs():
        if chat.chat.type == 'supergroup':
            try:
                bot.unban_chat_member(chat.chat.id, user_id)
                count += 1
            except:
                pass

    message.reply_text(f'{user_id} has been unbanned in {count} groups.')

# Handle "/broadcast" command
@bot.on_message(filters.command('broadcast'))
def broadcast_message(bot: Client, message: Message):
    text = message.text.split(' ', 1)[1] # Get message text from command argument

    # Send message to all groups and count the number of groups where the message was sent
    count = 0
    for chat in bot.iter_dialogs():
        if chat.chat.type == 'supergroup':
            try:
                bot.send_message(chat.chat.id, text)
                count += 1
            except:
                pass

    message.reply_text(f'Message sent to {count} groups.')
bot.run()

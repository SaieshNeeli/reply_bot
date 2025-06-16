from pyrogram import idle
from pyrogram import Client, filters
from openai import OpenAI
import nest_asyncio
import asyncio
import os
nest_asyncio.apply()


# === CONFIGURATION ===
api_id = 27389385
api_hash = "197c0ad085bee635bb7ef12a500923f8"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


ALLOWED_USERNAMES = ["Saiesh149", "Mr_Nayudu"]

# === OpenAI setup ===
client = OpenAI(api_key=OPENAI_API_KEY)

# === Pyrogram client ===
app = Client("my_account", api_id=api_id, api_hash=api_hash)


# === Generate GPT-style message history from Telegram ===
async def build_context_from_history(chat_id):
    messages = []
    async for msg in app.get_chat_history(chat_id, limit=10):
        if msg.from_user and msg.text:
            role = "assistant" if msg.from_user.is_self else "user"
            messages.append({"role": role, "content": msg.text})
    messages.reverse()  # chronological order
    return messages
# === GPT Reply with context ===
async def get_gpt_reply_with_context(chat_id):
    try:
        history = await build_context_from_history(chat_id)

        # Insert the system prompt first
        history.insert(0, {
            "role": "system",
            "content": (
                "You are Prakash, a 20-year-old funny and chill B.Tech 3rd year student. "
                "Reply like the user you're talking to — use Tenglish (Telugu+English), be short and casual, "
                "and always sound natural, like chatting with a close friend. Mimic their tone and writing style. "
                "Make your replies seem as human as possible so the user doesn’t suspect it’s a bot."
            )
        })

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"


# === Handle incoming private messages ===
@app.on_message(filters.private & filters.text)
async def handle_private_msg(client, message):
    username = message.from_user.username
    if username in ALLOWED_USERNAMES:
        reply = await get_gpt_reply_with_context(message.chat.id)
        await message.reply_text(reply)
    else:
        print(f"Ignored message from unauthorized user: {username}")



# === Main run ===
async def main():
    print("🚀 Userbot is running. Waiting for allowed users' messages...")
    await app.start()
    await idle()
    await app.stop()

# === Start the bot ===
asyncio.run(main())
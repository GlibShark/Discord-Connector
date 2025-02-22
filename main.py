import discord
from discord.ext import commands
from discord import Webhook
import aiohttp

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

CHANNEL_ID_1 = 1
CHANNEL_ID_2 = 1

async def get_or_create_webhook(channel):
    webhooks = await channel.webhooks()
    if webhooks:
        return webhooks[0]
    return await channel.create_webhook(name="Bridge Bot")

@bot.event
async def on_ready():
    print(f'Бот {bot.user} готовий!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id not in [CHANNEL_ID_1, CHANNEL_ID_2]:
        return

    target_channel_id = CHANNEL_ID_2 if message.channel.id == CHANNEL_ID_1 else CHANNEL_ID_1
    target_channel = bot.get_channel(target_channel_id)

    if not target_channel:
        return

    webhook = await get_or_create_webhook(target_channel)
    avatar_url = message.author.display_avatar.url

    async with aiohttp.ClientSession() as session:
        discord_webhook = Webhook.from_url(webhook.url, session=session)
        
        files = []
        for attachment in message.attachments:
            files.append(await attachment.to_file())
        
        await discord_webhook.send(
            content=message.content,
            username=f"{message.author.display_name} ({message.guild.name})",
            avatar_url=avatar_url,
            files=files,
            suppress_embeds=False
        )

    await bot.process_commands(message)

bot.run('1')
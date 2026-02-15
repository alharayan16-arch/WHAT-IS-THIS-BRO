import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import datetime
import math
import aiohttp
import io
import os

TOKEN = os.getenv("TOKEN")
WELCOME_CHANNEL_ID = 1472224372382109905  # change if needed

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print("WELCOME BOT READY")
    print(f"Logged in as {bot.user}")


# ---------------- GIF CREATION ----------------
async def create_welcome_gif(member):
    width, height = 900, 300
    frames = []

    try:
        font_big = ImageFont.truetype("arial.ttf", 64)
        font_small = ImageFont.truetype("arial.ttf", 30)
        font_logo = ImageFont.truetype("arial.ttf", 170)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_logo = ImageFont.load_default()

    username = member.name
    member_count = f"Member #{member.guild.member_count}"
    join_time = datetime.datetime.utcnow().strftime("%H:%M UTC")

    # Download avatar
    async with aiohttp.ClientSession() as session:
        async with session.get(member.display_avatar.url) as resp:
            avatar_bytes = await resp.read()

    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar = avatar.resize((65, 65))

    mask = Image.new("L", (65, 65), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 65, 65), fill=255)
    avatar.putalpha(mask)

    total_frames = 40

    for i in range(total_frames):

        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Welcome text
        draw.text((120, 60), f"Welcome {username}", font=font_big, fill=(255, 255, 255, 255))

        # Avatar
        img.paste(avatar, (120, 150), avatar)

        # Member info
        draw.text((200, 155), member_count, font=font_small, fill=(180, 180, 255, 255))
        draw.text((200, 190), join_time, font=font_small, fill=(180, 180, 255, 255))

        # AS logo
        movement_range = 3
        offset_x = int(math.sin(i / 12) * movement_range)

        logo_x = width - 280 + offset_x
        logo_y = 50

        pulse = (math.sin(i / 8) + 1) / 2
        glow_alpha = int(160 + pulse * 95)

        glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)

        glow_draw.text(
            (logo_x, logo_y),
            "AS",
            font=font_logo,
            fill=(255, 255, 255, glow_alpha)
        )

        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(8))
        img = Image.alpha_composite(img, glow_layer)

        draw = ImageDraw.Draw(img)
        draw.text(
            (logo_x, logo_y),
            "AS",
            font=font_logo,
            fill=(255, 255, 255, 255)
        )

        frames.append(img)

    gif_path = f"welcome_{member.id}.gif"

    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=60,
        loop=0,
        disposal=2
    )

    return gif_path


# ---------------- EVENTS ----------------
async def send_welcome(channel, member):
    gif = await create_welcome_gif(member)

    message_text = (
        f"{member.mention}, Welcome to Arab’s Studio — we’re glad to have you here!\n\n"
        "Take a look around and explore the server 🚀"
    )

    await channel.send(
        content=message_text,
        file=discord.File(gif)
    )


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    await send_welcome(channel, member)


@bot.command()
async def testwelcome(ctx):
    await send_welcome(ctx.channel, ctx.author)


bot.run(TOKEN)

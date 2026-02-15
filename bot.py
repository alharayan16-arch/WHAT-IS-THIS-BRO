import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import datetime
import math
import aiohttp
import io
import os

TOKEN = os.getenv("TOKEN")  # Use Railway variable
WELCOME_CHANNEL_ID = 1472224372382109905

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print("BOT STARTED CLEAN")
    print(f"Logged in as {bot.user}")


# ---------------- GIF CREATION ----------------
async def create_welcome_gif(member):
    width, height = 900, 300
    frames = []

    try:
        font_big = ImageFont.truetype("arial.ttf", 75)
        font_small = ImageFont.truetype("arial.ttf", 34)
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
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 65, 65), fill=255)
    avatar.putalpha(mask)

    total_frames = 40

    for i in range(total_frames):

        img = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(img)

        # BIG WELCOME TEXT
        draw.text((80, 70), f"Welcome {username}.", font=font_big, fill=(255, 255, 255))

        # AVATAR
        img.paste(avatar, (80, 165), avatar)

        # MEMBER INFO
        draw.text((165, 170), member_count, font=font_small, fill=(180, 180, 255))
        draw.text((165, 205), join_time, font=font_small, fill=(180, 180, 255))

        # AS LOGO MOVEMENT
        movement_range = 2
        offset_x = int(math.sin(i / 16) * movement_range)

        logo_x = width - 300 + offset_x
        logo_y = 40

        # Glow pulse
        pulse = (math.sin(i / 8) + 1) / 2
        glow_alpha = int(180 + pulse * 60)

        glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)

        glow_draw.text((logo_x, logo_y), "AS", font=font_logo, fill=(255, 255, 255, glow_alpha))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(8))

        img = Image.alpha_composite(img, glow_layer)

        draw = ImageDraw.Draw(img)
        draw.text((logo_x, logo_y), "AS", font=font_logo, fill=(255, 255, 255))

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
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    gif = await create_welcome_gif(member)

    await channel.send(
        content=f"{member.mention} , Welcome to Arab’s Studio — we’re glad to have you here!",
        file=discord.File(gif)
    )


@bot.command()
async def testwelcome(ctx):
    member = ctx.author

    gif = await create_welcome_gif(member)

    await ctx.send(
        content=f"{member.mention} , Welcome to Arab’s Studio — we’re glad to have you here!",
        file=discord.File(gif)
    )


bot.run(TOKEN)



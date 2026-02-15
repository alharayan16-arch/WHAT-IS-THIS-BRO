import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import datetime
import math
import aiohttp
import io
import os

TOKEN = os.getenv("TOKEN")  # Railway env variable
WELCOME_CHANNEL_ID = 1472224372382109905

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print("NEW CLEAN VERSION LOADED")
    print(f"Logged in as {bot.user}")


# ---------------- GIF CREATION (MEMORY ONLY) ----------------
async def create_welcome_gif(member):
    width, height = 900, 300
    frames = []

    try:
        font_big = ImageFont.truetype("arial.ttf", 70)
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

    # Circular mask
    mask = Image.new("L", (65, 65), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 65, 65), fill=255)
    avatar.putalpha(mask)

    total_frames = 40

    for i in range(total_frames):

        # Transparent background
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # --- TEXT ---
        draw.text((80, 70), f"Welcome {username}", font=font_big, fill=(255, 255, 255, 255))

        img.paste(avatar, (80, 160), avatar)

        draw.text((160, 170), member_count, font=font_small, fill=(170, 170, 255, 255))
        draw.text((160, 205), join_time, font=font_small, fill=(170, 170, 255, 255))

        # --- AS LOGO (RIGHT SIDE) ---
        movement = int(math.sin(i / 18) * 2)  # subtle movement
        logo_x = width - 280 + movement
        logo_y = 50

        pulse = (math.sin(i / 8) + 1) / 2
        glow_alpha = int(150 + pulse * 100)

        glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)

        glow_draw.text((logo_x, logo_y), "AS", font=font_logo, fill=(255, 255, 255, glow_alpha))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(8))

        img = Image.alpha_composite(img, glow_layer)

        draw = ImageDraw.Draw(img)
        draw.text((logo_x, logo_y), "AS", font=font_logo, fill=(255, 255, 255, 255))

        frames.append(img)

    # Save to memory (NOT FILE)
    gif_bytes = io.BytesIO()
    frames[0].save(
        gif_bytes,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=60,
        loop=0,
        disposal=2,
        transparency=0
    )

    gif_bytes.seek(0)
    return gif_bytes


# ---------------- EVENTS ----------------
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    gif_bytes = await create_welcome_gif(member)

    await channel.send(
        content=f"{member.mention} , Welcome to Arab’s Studio — we’re glad to have you here!",
        file=discord.File(fp=gif_bytes, filename="welcome.gif")
    )


@bot.command()
async def testwelcome(ctx):
    member = ctx.author

    gif_bytes = await create_welcome_gif(member)

    await ctx.send(
        content=f"{member.mention} , Welcome to Arab’s Studio — we’re glad to have you here!",
        file=discord.File(fp=gif_bytes, filename="welcome.gif")
    )


bot.run(TOKEN)

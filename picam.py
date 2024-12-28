import discord
from discord.ext import commands, tasks
from discord.ui import Button, View, Modal, TextInput
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput
import cv2
from numpy import count_nonzero
from datetime import datetime, timezone, timedelta
import socket
from os import popen

# Discord variables
token = "Your key"
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

discord_ids = {"server": None, "interface_ch": None, "alert_ch": None, "command_ch": None, "interface_msg": None}

# Motion variables
cam = Picamera2()
cam.start()

diff_thresh = 128
motion_thresh = 512

vid_buffer = 10
vid_cutoff = [0, 60]
wait = -1

md_active = False

md_start = None
md_end = None

new = cam.capture_array()

# MD command
@bot.tree.command(name="md", description="Enables/disables motion detection and motion alerts.")
async def md_toggle(interaction: discord.Interaction, option: str):
    global md_active

    if option == "enable":
        md_active = True
        await interaction.response.send_message("Motion detection **enabled**!")
    else:
        md_active = False
        await interaction.response.send_message("Motion detection **disabled**!")

    await update_inter(True)

@md_toggle.autocomplete("option")
async def option_autocomplete(interaction: discord.Interaction, current: str):
    options = ["enable", "disable"]
    return [discord.app_commands.Choice(name=opt, value=opt) for opt in options]

# MD schedule command
@bot.tree.command(name="mdschedule", description="Schedules motion detection and motion alerts.")
async def mdschedule(interaction: discord.Interaction, option: str):
    global md_start, md_end

    if option == "set":
        modal = Modal(title="MD Schedule")
        modal.add_item(TextInput(label="Start time", placeholder="07 34", max_length=5))
        modal.add_item(TextInput(label="End time", placeholder="18 32", max_length=5))
        modal.on_submit = mdsm_callback

        await interaction.response.send_modal(modal)
    else:
        md_start = None
        md_end = None

        await interaction.response.send_message(f"Motion detection schedule **disabled**!")

        await update_inter(True)

@mdschedule.autocomplete("option")
async def option_autocomplete(interaction: discord.Interaction, current: str):
    options = ["set", "disable"]
    return [discord.app_commands.Choice(name=opt, value=opt) for opt in options]

async def mdsm_callback(interaction: discord.Interaction):
    global md_start, md_end

    start = interaction.data["components"][0]["components"][0]["value"]
    end = interaction.data["components"][1]["components"][0]["value"]

    try:
        md_start = datetime.strptime(start, "%H %M").time()
        md_end = datetime.strptime(end, "%H %M").time()

        await interaction.response.send_message(f"Motion detection scheduled from **{str(md_start)[:-3]}** to **{str(md_end)[:-3]}**!")
    except:
        md_start = None
        md_end = None

        await interaction.response.send_message(f"Invalid time, use **HH MM** format!")

    await update_inter(True)

def is_between():
    now = datetime.now().time()

    if md_start == None or md_end == None:
        return True
    else:
        if md_start < md_end:
            return md_start <= now < md_end
        else:
            return md_start <= now or now < md_end

# Capture command
@bot.tree.command(name="capture", description="Takes a photo and displays it.")
async def capture(interaction: discord.Interaction):
    cam.capture_file("photo.jpg")
    file = discord.File("photo.jpg", filename=f"{datetime.now().strftime('%H-%M')}.jpg")

    await interaction.response.send_message(f"Photo captured at **{datetime.now().strftime('%H:%M')}**!", file=file)

# Temp command
@bot.tree.command(name="temp", description="Gets the temperature of Pi Cam and sends it.")
async def temp(interaction: discord.Interaction):
    temp = popen("vcgencmd measure_temp").readline()

    await interaction.response.send_message(f"Pi Cam is currently running at **{temp[5:-1]}**!")

# Endpoint command
@bot.tree.command(name="endpoint", description="Connects/disconnects to alert endpoint server.")
async def endpoint(interaction: discord.Interaction, option: str):
    global client

    if option == "connect":
        modal = Modal(title="Endpoint Setup")
        modal.add_item(TextInput(label="IP Address", placeholder="192.168.3.167", max_length=15))
        modal.on_submit = endm_callback

        await interaction.response.send_modal(modal)
    else:
        try:
            client.close()
            client = None

            await interaction.response.send_message("Disconnected from endpoint!")
        except:
            await interaction.response.send_message("No endpoint to disconnect from!")

@endpoint.autocomplete("option")
async def option_autocomplete(interaction: discord.Interaction, current: str):
    options = ["connect", "disconnect"]
    return [discord.app_commands.Choice(name=opt, value=opt) for opt in options]

async def endm_callback(interaction: discord.Interaction):
    global client

    ip = interaction.data["components"][0]["components"][0]["value"]

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(1)
        client.connect((ip, 11000))

        await interaction.response.send_message(f"Connected to endpoint at **{ip}**!")
    except:
        await interaction.response.send_message("Endpoint server offline or invalid ip address!")


# Shutdown command
@bot.tree.command(name="shutdown", description="Shuts down the bot.")
async def shutdown(interaction: discord.Interaction):
    await interaction.response.send_message("Shutting down server...")

    await update_inter(False)
    cam.close()
    await bot.close()

# Main loop for motion detection
@tasks.loop(seconds=0.5)
async def motion():
    global old, new, vid_cutoff, wait, client

    if (md_active and is_between()) or wait != -1:
        old = new
        new = cam.capture_array()

        abs_diff = cv2.absdiff(cv2.cvtColor(old, cv2.COLOR_RGB2GRAY), cv2.cvtColor(new, cv2.COLOR_RGB2GRAY))
        _, diff_mask = cv2.threshold(abs_diff, diff_thresh, 255, cv2.THRESH_BINARY)
        diff_count = count_nonzero(diff_mask)

        if wait == 0 or vid_cutoff[0] >= vid_cutoff[1]:
            cam.stop_recording()
            cam.start()
            file = discord.File("output.mp4", filename=f"{datetime.now().strftime('%H-%M')}.mp4")

            await bot.get_channel(discord_ids["alert_ch"]).send(file=file)

            vid_cutoff[0] = 0
            wait = -1
        elif diff_count >= motion_thresh:
            if wait == -1:
                cam.start_recording(H264Encoder(), FfmpegOutput("output.mp4", audio=False), quality=Quality.LOW)

                await bot.get_channel(discord_ids["alert_ch"]).send(f"Motion detected at **{datetime.now().strftime('%H:%M')}**!")

                try:
                    client.send("Motion detected!".encode("utf-8"))
                except:
                    try:
                        client.close()
                        client = None
                    except:
                        pass

            vid_cutoff[0] += 1
            wait = vid_buffer
        elif wait > 0:
            vid_cutoff[0] += 1
            wait -= 1

# Interface function
async def update_inter(status):
    embed = discord.Embed(title="Interface")
    embed.add_field(name="Camera Status", value="Online" if status else "Offline", inline=False)
    embed.add_field(name="Motion Detection", value="Active" if md_active and status else "Disabled", inline=True)
    embed.add_field(name="Schedule", value=f"{str(md_start)[:-3]} to {str(md_end)[:-3]}" if md_start and status else "Disabled", inline=True)

    view = View(timeout=None)

    md_button = Button(label="MD Off" if md_active and status else "MD On", style=discord.ButtonStyle.danger if md_active and status else discord.ButtonStyle.success)
    md_button.callback = md_bcallback
    view.add_item(md_button)
    mds_button = Button(label="MDS Off" if md_start and status else "Set MDS", style=discord.ButtonStyle.danger if md_start and status else discord.ButtonStyle.success)
    mds_button.callback = mds_bcallback
    view.add_item(mds_button)
    cap_button = Button(label="Capture", style=discord.ButtonStyle.primary)
    cap_button.callback = cap_bcallback
    view.add_item(cap_button)

    updated = await bot.get_channel(discord_ids["interface_ch"]).fetch_message(discord_ids["interface_msg"])
    await updated.edit(embed=embed, view=view)

# Button callbacks
async def md_bcallback(interaction: discord.Interaction):
    global md_active

    await interaction.response.defer()

    if md_active == False:
        md_active = True
    else:
        md_active = False

    await update_inter(True)

async def mds_bcallback(interaction: discord.Interaction):
    global md_start, md_end

    modal = Modal(title="MD Schedule")
    
    modal.add_item(TextInput(label="Start time", placeholder="07 34", max_length=5))
    modal.add_item(TextInput(label="End time", placeholder="18 32", max_length=5))

    modal.on_submit = mdsm_bcallback

    if md_start:
        await interaction.response.defer()

        md_start = None
        md_end = None

        await update_inter(True)
    else:
        await interaction.response.send_modal(modal)

async def mdsm_bcallback(interaction: discord.Interaction):
    global md_start, md_end

    await interaction.response.defer()

    start = interaction.data["components"][0]["components"][0]["value"]
    end = interaction.data["components"][1]["components"][0]["value"]

    try:
        md_start = datetime.strptime(start, "%H %M").time()
        md_end = datetime.strptime(end, "%H %M").time()
    except:
        md_start = None
        md_end = None

    await update_inter(True)

async def cap_bcallback(interaction: discord.Interaction):
    await interaction.response.defer()

    cam.capture_file("photo.jpg")
    file = discord.File("photo.jpg", filename=f"{datetime.now().strftime('%H-%M')}.jpg")

    await bot.get_channel(discord_ids["command_ch"]).send(f"Photo captured at **{datetime.now().strftime('%H:%M')}**!", file=file)

# Message auto delete loop
@tasks.loop(hours=1)
async def auto_delete():
    for channel in [ch for ch in bot.get_guild(discord_ids["server"]).channels if isinstance(ch, discord.TextChannel)]:
        now = datetime.now(timezone.utc)

        async for message in channel.history(limit=None):
            if not message.pinned and not message.id in discord_ids.values() and (now - message.created_at) > timedelta(hours=24):
                try:
                    await message.delete()
                except:
                    pass

# Init command
@bot.event
async def on_ready():
    # Setup code
    interface_id = None

    view = View(timeout=None)
    bot.get_channel(interface_id).send(view=view)

    # End of setup code

    await update_inter(True)

    try:
        motion.start()
        auto_delete.start()
    except:
        pass
    
    await bot.tree.sync()
    await auto_delete()

bot.run(token)

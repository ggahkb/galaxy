import discord
from discord.ext import commands
from discord import app_commands

TOKEN = "YOUR_BOT_TOKEN"

intents = discord.Intents.default()
intents.bans = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

class ConfirmView(discord.ui.View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=30)
        self.author = author
        self.result = None

    @discord.ui.button(label="✅ Confirm Unban", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("⚠️ This is not your button.", ephemeral=True)
            return
        self.result = True
        await interaction.response.edit_message(content="🔄 Unbanning all users...", view=None)
        self.stop()

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("⚠️ This is not your button.", ephemeral=True)
            return
        self.result = False
        await interaction.response.edit_message(content="❌ Cancelled unban.", view=None)
        self.stop()

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot ready: {bot.user}")

@bot.tree.command(name="unbanall", description="Unban ALL banned users in the server")
@app_commands.checks.has_permissions(administrator=True)
async def unbanall(interaction: discord.Interaction):
    view = ConfirmView(interaction.user)
    await interaction.response.send_message(
        content="⚠️ Are you sure you want to unban **ALL** banned users?",
        view=view,
        ephemeral=True
    )
    await view.wait()

    if view.result:
        bans = await interaction.guild.bans()
        count = 0
        for entry in bans:
            try:
                await interaction.guild.unban(entry.user)
                count += 1
            except Exception as e:
                print(f"Failed to unban {entry.user}: {e}")
        await interaction.followup.send(f"✅ Unbanned {count} users.", ephemeral=True)
    elif view.result is False:
        # Already handled inside the cancel button
        pass
    else:
        await interaction.followup.send("❌ You didn't respond in time.", ephemeral=True)

bot.run(TOKEN)

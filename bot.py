import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.guilds = True
intents.bans = True

bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = "YOUR_BOT_TOKEN_HERE"

class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.value = None

    @discord.ui.button(label="✅ Confirm Unban All", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced. Ready as {bot.user}.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="unbanall", description="🚫 Unban all banned users in the server.")
@app_commands.checks.has_permissions(administrator=True)
async def unbanall(interaction: discord.Interaction):
    await interaction.response.send_message(
        "⚠️ Are you sure you want to unban **all banned users**?",
        view=ConfirmView(),
        ephemeral=True
    )

    view = ConfirmView()
    await view.wait()

    if view.value:
        bans = await interaction.guild.bans()
        count = 0
        for ban_entry in bans:
            try:
                await interaction.guild.unban(ban_entry.user)
                count += 1
            except Exception as e:
                print(f"Error unbanning {ban_entry.user}: {e}")

        await interaction.followup.send(f"✅ Successfully unbanned `{count}` users.", ephemeral=True)
    else:
        await interaction.followup.send("❌ Unban all cancelled.", ephemeral=True)

bot.run(TOKEN)

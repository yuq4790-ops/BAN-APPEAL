import discord
import os
from discord.ext import commands
from discord import app_commands
import io
os.getenv("TOKEN")
ROLE_ID = 1515387713715441715


intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="ban", description="Schickt den user in Ban Modus")
@app_commands.checks.has_permissions(administrator=True)
async def setrole(interaction: discord.Interaction, user: discord.Member):
    role = interaction.guild.get_role(ROLE_ID)
    if role is None:
        await interaction.response.send_message(
            "Rolle nicht gefunden.",
            ephemeral=True
        )
        return

    roles_to_remove = [
        r for r in user.roles
        if r != interaction.guild.default_role
    ]
    await user.remove_roles(*roles_to_remove, reason="Slash Command Role Reset")
    await user.add_roles(role, reason="Slash Command Role Set")
    await interaction.response.send_message(
        f" {user.mention} wurde in den Ban Modus geschickt."
    )


#ban appeal Ticket öffnen

CATEGORY_ID = 1514356048457240688
STAFF_ROLE_ID = 1512564428338630796
LOG_CHANNEL_ID = 1515389646337474610
BANNER_URL = "https://media.discordapp.net/attachments/1292435237653184554/1512944176856170516/tppm6zd.webp?ex=6a2e8050&is=6a2d2ed0&hm=4fb94bfc46b8c0a7f37ef48a93500288b56f66cf3646812060f5a01fbd4bb383&=&format=webp"


class AppealTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Transcript",
        style=discord.ButtonStyle.secondary
    )
    async def transcript(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)

        if not log_channel:
            await interaction.response.send_message(
                "Log Channel nicht gefunden.",
                ephemeral=True
            )
            return

        messages = []

        async for msg in interaction.channel.history(
                limit=None,
                oldest_first=True
        ):
            messages.append(
                f"[{msg.created_at.strftime('%d.%m.%Y %H:%M')}] "
                f"{msg.author} : {msg.content}"
            )

        transcript_text = "\n".join(messages)

        file = discord.File(
            io.BytesIO(transcript_text.encode("utf-8")),
            filename=f"{interaction.channel.name}.txt"
        )

        await log_channel.send(
            content=(
                f"Transcript von {interaction.channel.mention}\n"
                f"Erstellt von {interaction.user.mention}"
            ),
            file=file
        )

        await interaction.response.send_message(
            f"Transcript wurde in {log_channel.mention} gesendet.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Close",
        style=discord.ButtonStyle.red
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "Ticket wird geschlossen...",
            ephemeral=True
        )

        await interaction.channel.delete()

    @discord.ui.button(
        label="Declined",
        style=discord.ButtonStyle.danger
    )
    async def declined(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.channel.send(
            "**Dein Ban Appeal wurde abgelehnt.**\n\n"
            "Falls du Fragen hast, kontaktiere das Team."
        )

        await interaction.response.send_message(
            "Appeal wurde abgelehnt.",
            ephemeral=True
        )


class BanAppealView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Appeal erstellen",
        style=discord.ButtonStyle.red
    )
    async def create_appeal(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        existing = discord.utils.get(
            interaction.guild.channels,
            name=f"appeal-{interaction.user.name.lower()}"
        )

        if existing:
            await interaction.response.send_message(
                f"Du hast bereits ein Appeal offen: {existing.mention}",
                ephemeral=True
            )
            return

        category = interaction.guild.get_channel(CATEGORY_ID)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),

            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),

            interaction.guild.get_role(STAFF_ROLE_ID):
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
        }

        channel = await interaction.guild.create_text_channel(
            name=f"appeal-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="Ban Appeal",
            description=(
                "**Bitte beantworte folgende Fragen:**\n\n"
                "1. Discord Name:\n"
                "2. Warum wurdest du gebannt?\n"
                "3. Warum sollten wir dich entbannen?\n"
                "4. Weitere Informationen:"
            ),
            color=discord.Color.brand_red()
        )

        await channel.send(
            content=f"{interaction.user.mention}",
            embed=embed,
            view=AppealTicketView()
        )

        await interaction.response.send_message(
            f"Dein Appeal wurde erstellt: {channel.mention}",
            ephemeral=True
        )

    @discord.ui.button(
        label="Informationen",
        style=discord.ButtonStyle.secondary
    )
    async def informationen(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "**Warum wurde ich gebannt?**\n\n"
            "• Toxic Verhalten\n"
            "• Spam\n"
            "• Scamming\n"
            "• DM Advertisments\n"
            "• Trolling\n"
            "• Mehrfache Verwarnungen\n\n"
            
            
            "**Ban Appeal Informationen**\n\n"
            "• Bitte beantworte alle Fragen ehrlich.\n"
            "• Ein Appeal garantiert keine Entbannung.\n"
            "• Beleidigungen oder Troll-Antworten führen zur Ablehnung.\n"
            "• Das Team entscheidet endgültig.",
            ephemeral=True
        )


@bot.tree.command(
    name="banappeal",
    description="Sendet das Ban Appeal Panel"
)
@app_commands.checks.has_permissions(administrator=True)
async def banappeal(interaction: discord.Interaction):

    embed = discord.Embed(
        title="BAN APPEAL",
        color=discord.Color.brand_red()
    )

    embed.description = (

        "> **Warum wurde ich gebannt?**\n"
        "> Klicke auf die Information um dies zu erfahren\n\n"
        "> Wurde dein Ban zu Unrecht ausgesprochen?\n"
        "> Dann kannst du hier einen Appeal erstellen.\n\n"
        "> Bitte mache wahrheitsgemäße Angaben.\n"
        "> Falsche Angaben können zur Ablehnung führen.\n\n"

    )

    embed.set_image(url=BANNER_URL)

    await interaction.channel.send(
        embed=embed,
        view=BanAppealView()
    )

    await interaction.response.send_message(
        "Ban Appeal Panel gesendet.",
        ephemeral=True
    )


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


bot.run(TOKEN)

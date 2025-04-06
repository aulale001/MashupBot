import random
import os
import utils
import discord
import re
from dotenv import load_dotenv
from discord import Intents, Client, Message, Reaction, Embed, app_commands
from typing import Final
from utils import get_spec, Spec

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
GUILD_IDS = [
    discord.Object(id=int(gid.strip()))
    for gid in os.getenv('GUILD_IDS', '').split(',') if gid.strip().isdigit()
]
# BOT SETUP
active_events = {}  # guild_id: bool
event_creators = {}
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
intents.reactions = True  # NOQA
intents.members = True  # NOQA
client: Client = Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(
    name="mashup",
    description="Start a round of Mythic Mashup",
    guilds=GUILD_IDS
)
async def fist_command(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    if active_events.get(guild_id):
        await interaction.response.send_message("A Mashup-Event is already active in this server. Please end it first.",
                                                ephemeral=True)
        return
    active_events[guild_id] = True
    event_creators[guild_id] = interaction.user.id
    await interaction.response.send_message("Mythic Mashup has started!")
    await send_mashup(interaction.channel)


@tree.command(
    name="advancedmashup",
    description="Start a round of Mythic Mashup",
    guilds=GUILD_IDS
)
async def second_command(interaction: discord.Interaction):
    guild_id = interaction.guild.id

    if active_events.get(guild_id):
        await interaction.response.send_message(
            "A Mashup-Event is already running in this server. Please end it before starting a new one.",
            ephemeral=True
        )
        return

    active_events[guild_id] = True
    event_creators[guild_id] = interaction.user.id
    await interaction.response.send_message("Mythic Mashup has started!")
    await send_advancedmashup(interaction.channel)


async def on_ready() -> None:
    await tree.sync(guild=discord.Object(id=1300478687665455145))
    await tree.sync(guild=discord.Object(id=924284241141977089))
    print(f'{client.user} is now running')

async def clear_bot_messages(channel: discord.TextChannel, bot_user: discord.User) -> int:
    """
    Deletes all messages sent by the bot in the specified channel.

    Args:
        channel (discord.TextChannel): The channel to search and purge.
        bot_user (discord.User): The bot's user object (usually client.user).

    Returns:
        int: The number of messages deleted.
    """
    deleted = await channel.purge(limit=None, check=lambda msg: msg.author == bot_user)
    return len(deleted)




# region mashupcomand
# === Global Variables (MASHUP) ===
players: list = []  # Stores Player objects for the basic mashup
mashup_event = None  # Discord message object for the active mashup embed
class Player:
    """
    Represents a player in the basic Mythic Mashup.
    Stores display name and role reaction preferences.
    """

    def __init__(self, user: str, reaction: str):
        self.display_name = user
        self.reactions = list()
        if reaction != "":
            self.reactions.append(reaction)

        def append_reaction(self, reaction: str):
            """
            Add a role reaction to the player's list.
            """

        if reaction != "":
            self.reactions.append(reaction)


# Button class to add clickable buttons to the embedded message
class ButtonMash(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label='Start Round', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        if event_creators.get(guild_id) != interaction.user.id:
            await interaction.response.send_message("Only the event creator can start the round!", ephemeral=True)
            return

        if not players:
            await interaction.response.send_message("Not enough players to start the mashup.", ephemeral=True)
            return

        self.stop()
        await interaction.response.defer()
        await send_newmashup(interaction.channel, interaction.message)

    @discord.ui.button(label='End Mashup', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Defer to avoid interaction timeout
        try:
            await interaction.response.defer(thinking=True)
        except discord.InteractionResponded:
            pass  # Interaction already acknowledged

        # Delete all bot messages in the channel
        await clear_bot_messages(interaction.channel, interaction.client.user)

        # Clean up mashup state
        users.clear()
        players.clear()
        active_events.pop(interaction.guild.id, None)
        self.stop()


"""Handle new role reaction added by a user. Adds or updates them in the players list."""


@client.event
async def on_reaction_add(reaction: Reaction, user: Message.author) -> None:
    print(str(reaction))
    if reaction.message.guild:
        if user == client.user:
            return
        if reaction.message.author != client.user:
            return
        if str(reaction) == "<:tank:1301197903028817980>" or str(reaction) == "<:healer:1301201583408808018>" or str(
                reaction) == "<:DPS:1301204877900382229>" or str(reaction) == "<:hero:1301202360403759164>" or str(
                reaction) == "🪦":
            for player in players:
                if player.display_name == str(user.display_name):
                    player.append_reaction(str(reaction))
                    break
            else:
                players.append(Player(str(user.display_name), str(reaction)))
        else:
            await reaction.remove(user)


"""Handle reaction removal. Removes the role or the player if no roles remain."""


@client.event
async def on_reaction_remove(reaction: Reaction, user: Message.author) -> None:
    if user == client.user:
        return
    if reaction.message.author != client.user:
        return
    if str(reaction) == "<:tank:1301197903028817980>" or str(reaction) == "<:healer:1301201583408808018>" or str(
            reaction) == "<:DPS:1301204877900382229>" or str(reaction) == "<:hero:1301202360403759164>" or str(
            reaction) == "🪦":
        for player in players:
            if str(player.display_name) == str(user.display_name):
                player.reactions.remove(str(reaction))
                if len(player.reactions) == 0:
                    players.remove(player)
                break


"""Sends the initial embed for role reaction in the basic mashup."""


async def send_mashup(channel: discord.channel):
    embedVar = Embed(title="MYTHIC MASHUP",
                     description="React with the roles you want to participate with in the next round of mashup",
                     color=0x00ff00)
    embeded_message = embedVar
    global mashup_event
    mashup_event = await channel.send(embed=embeded_message, view=ButtonMash())
    emoji = '\N{HEADSTONE}'
    await  mashup_event.add_reaction("<:tank:1301197903028817980>")
    await  mashup_event.add_reaction("<:healer:1301201583408808018>")
    await  mashup_event.add_reaction("<:DPS:1301204877900382229>")
    await  mashup_event.add_reaction("<:hero:1301202360403759164>")
    await  mashup_event.add_reaction(emoji)


"""Sends updated embed with new round of generated groups for mashup."""


async def send_newmashup(channel: Message.channel, message: Message):
    embedVar = Embed(title="MYTHIC MASHUP",
                     description="Round has started! React with the roles you want to participate with in the next round of mashup",
                     color=0x00ff00)
    p = players
    for pl in players:
        if pl.reactions.count("<:tank:1301197903028817980>") == 0 and pl.reactions.count(
                "<:healer:1301201583408808018>") == 0 and pl.reactions.count("<:DPS:1301204877900382229>") == 0:
            if pl.reactions.count("<:hero:1301202360403759164>") == 1 or pl.reactions.count("🪦") == 1:
                players.remove(pl)
    if (len(p) > 0):
        i = 1
        while len(p) > 0:
            p = await generate_groups(p, embedVar, i)
            i = i + 1
    else:
        embedVar.description = "React with the roles you want to participate with in the next round of mashup"
    await message.edit(embed=embedVar, view=ButtonMash())
    await message.clear_reactions()
    emoji = '\N{HEADSTONE}'
    await message.add_reaction("<:tank:1301197903028817980>")
    await  message.add_reaction("<:healer:1301201583408808018>")
    await  message.add_reaction("<:DPS:1301204877900382229>")
    await  message.add_reaction("<:hero:1301202360403759164>")
    await  message.add_reaction(emoji)
    players.clear()


# get a tank out of the reacted player list
def get_tank(tanks):
    tank: Player = Player("", "")
    hasbr: bool = False
    addedtank = False
    for player in tanks:
        tank = player
        addedtank = True
        if player.reactions.count("🪦") == 1:
            hasbr = True
        break
    if not addedtank:
        tank = Player("PUG TANK", "<:tank:1301197903028817980>")
    return tank, hasbr


# get a healer out of the reacted player list
def get_healer(healers, Hasbr):
    healer = Player("", "")
    hasbr = Hasbr
    hashero = False
    addedheal = False
    # 1st itteration only add healer when br is in group and heal does not have br
    for heal in healers:
        if hasbr:
            if heal.reactions.count("🪦") == 0:
                healer = heal
                addedheal = True
                if heal.reactions.count("<:hero:1301202360403759164>") == 1:
                    hashero = True
                break
    # 2cnd itteration only add healer when br is not in group and heal does have br
    for heal in healers:
        if not hasbr:
            if heal.reactions.count("🪦") == 1:
                healer = heal
                hasbr = True
                addedheal = True
                if heal.reactions.count("<:hero:1301202360403759164>") == 1:
                    hashero = True
                break
    # 3rd itteration when no healer could be added due to restrictions take 1st available healer
    if not addedheal:
        for heal in healers:
            healer = heal
            addedheal = True
            if heal.reactions.count("<:hero:1301202360403759164>") == 1:
                hashero = True
            if heal.reactions.count("🪦") == 1:
                hasbr = True
            break
    # 4th itteration when still no heal added a pug
    if not addedheal:
        healer = Player("PUG Healer", "<:healer:1301201583408808018>")
    return healer, hasbr, hashero


# get 3 dps out of the reacted player list
def get_dps(dps, hasbr, hashero):
    dps1 = Player("", "")
    dps2 = Player("", "")
    dps3 = Player("", "")
    addeddps1 = False
    # only add dps when br and hero in group and dps has none
    if hasbr and hashero:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 0 and d.reactions.count("🪦") == 0:
                dps1 = d
                addeddps1 = True
                dps.remove(d)
                break
    # only add dps when br is and hero is not in group and dps has hero
    if hasbr and not hashero and not addeddps1:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 1 and d.reactions.count("🪦") == 0:
                dps1 = d
                addeddps1 = True
                hashero = True
                dps.remove(d)
                break
    # only add dps when br is not and hero is in group and dps has br
    if not hasbr and hashero and not addeddps1:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 0 and d.reactions.count("🪦") == 1:
                dps1 = d
                addeddps1 = True
                hasbr = True
                dps.remove(d)
                break
    # only add dps when br and hero are not in group and dps has hero
    if not hasbr and not hashero and not addeddps1:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 1 and d.reactions.count("🪦") == 0:
                dps1 = d
                addeddps1 = True
                hashero = True
                dps.remove(d)
                break
    # only add dps when br and hero are not in group and dps has br
    if not hasbr and not hashero and not addeddps1:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 0 and d.reactions.count("🪦") == 1:
                dps1 = d
                addeddps1 = True
                hashero = True
                dps.remove(d)
                break
    # if no dps added due to restrictions take 1st one
    if not addeddps1:
        for d in dps:
            dps1 = d
            dps.remove(d)
            addeddps1 = True
            if d.reactions.count("<:hero:1301202360403759164>"):
                hashero = True
            if d.reactions.count("🪦"):
                hasbr = True
            break
    # if still no dps add pug dps
    if not addeddps1:
        dps1 = Player("PUG DPS", "<:DPS:1301204877900382229>")
    addeddps2 = False
    # only add dps when br and hero in group and dps has none
    if hasbr and hashero:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 0 and d.reactions.count("🪦") == 0:
                dps2 = d
                dps.remove(d)
                addeddps2 = True
                break
                # only add dps when br is and hero is not in group and dps has hero
    if hasbr and not hashero and not addeddps2:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 1 and d.reactions.count("🪦") == 0:
                dps2 = d
                dps.remove(d)
                addeddps2 = True
                hashero = True
                break
    # only add dps when br is not and hero is in group and dps has br
    if not hasbr and hashero and not addeddps2:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 0 and d.reactions.count("🪦") == 1:
                dps2 = d
                dps.remove(d)
                addeddps2 = True
                hasbr = True
                break
    # only add dps when br and hero are not in group and dps has hero
    if not hasbr and not hashero and not addeddps2:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 1 and d.reactions.count("🪦") == 0:
                dps2 = d
                dps.remove(d)
                addeddps2 = True
                hashero = True
                break
    # only add dps when br and hero are not in group and dps has br
    if not hasbr and not hashero and not addeddps2:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 0 and d.reactions.count("🪦") == 1:
                dps2 = d
                dps.remove(d)
                addeddps2 = True
                hashero = True
                break
    # if no dps added due to restrictions take 1st one
    if not addeddps2:
        for d in dps:
            dps2 = d
            dps.remove(d)
            addeddps2 = True
            if d.reactions.count("<:hero:1301202360403759164>"):
                hashero = True
            if d.reactions.count("🪦"):
                hasbr = True
            break
    # if still no dps add pug dps
    if not addeddps2:
        dps2 = Player("PUG DPS", "<:DPS:1301204877900382229>")
    addeddps3 = False
    # only add dps when br and hero in group and dps has none
    if hasbr and hashero:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 0 and d.reactions.count("🪦") == 0:
                dps3 = d
                dps.remove(d)
                addeddps3 = True
                break
                # only add dps when br is and hero is not in group and dps has hero
    if hasbr and not hashero and not addeddps3:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 1 and d.reactions.count("🪦") == 0:
                dps3 = d
                dps.remove(d)
                addeddps3 = True
                hashero = True
                break
    # only add dps when br is not and hero is in group and dps has br
    if not hasbr and hashero and not addeddps3:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 0 and d.reactions.count("🪦") == 1:
                dps3 = d
                dps.remove(d)
                addeddps3 = True
                hasbr = True
                break
    # only add dps when br and hero are not in group and dps has hero
    if not hasbr and not hashero and not addeddps3:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 1 and d.reactions.count("🪦") == 0:
                dps3 = d
                dps.remove(d)
                addeddps3 = True
                hashero = True
                break
    # only add dps when br and hero are not in group and dps has br
    if not hasbr and not hashero and not addeddps3:
        for d in dps:
            if d.reactions.count("<:hero:1301202360403759164>") == 0 and d.reactions.count("🪦") == 1:
                dps3 = d
                dps.remove(d)
                addeddps3 = True
                hashero = True
                break
    # if no dps added due to restrictions take 1st one
    if not addeddps3:

        for d in dps:

            dps3 = d
            dps.remove(d)
            addeddps3 = True
            if d.reactions.count("<:hero:1301202360403759164>"):
                hashero = True
            if d.reactions.count("🪦"):
                hasbr = True
            break
    # if still no dps add pug dps
    if not addeddps3:
        dps3 = Player("PUG DPS", "<:DPS:1301204877900382229>")
    return dps1, dps2, dps3, hashero, hasbr


"""Builds groups of players based on their roles and adds them to the embed."""


async def generate_groups(players, embedVar, i):
    dungeon = list()
    hasbr = False
    hashero = False
    tanks = list()
    # Tank
    random.shuffle(players)
    for player in players:
        if player.reactions.count("<:tank:1301197903028817980>") == 1:
            tanks.append(player)
    tank, hasbr = get_tank(tanks)
    dungeon.append(tank)

    for player in players:
        if str(player.display_name) == str(tank.display_name):
            players.remove(player)
            break
    # Heal
    healers = list()
    for player in players:
        if player.reactions.count("<:healer:1301201583408808018>"):
            healers.append(player)
    healer, hasbr, hashero = get_healer(healers, hasbr)
    dungeon.append(healer)
    for player in players:
        if str(player.display_name) == str(healer.display_name):
            players.remove(player)
            break
    # dps
    dps = list()
    for player in players:
        if player.reactions.count("<:DPS:1301204877900382229>"):
            dps.append(player)
    damage1, damage2, damage3, hashero, hasbr = get_dps(dps, hasbr, hashero)
    dungeon.append(damage1)
    dungeon.append(damage2)
    dungeon.append(damage3)
    for player in players:
        if str(player.display_name) == str(damage1.display_name):
            players.remove(player)
            break
    for player in players:
        if str(player.display_name) == str(damage2.display_name):
            players.remove(player)
            break
    for player in players:
        if str(player.display_name) == str(damage3.display_name):
            players.remove(player)
            break
    embedVar.add_field(name=f"Group {i}:",
                       value=f"{'<:tank:1301197903028817980>'} {dungeon[0].display_name}\n{'<:healer:1301201583408808018>'} {dungeon[1].display_name}\n{'<:DPS:1301204877900382229>'} {dungeon[2].display_name}\n{'<:DPS:1301204877900382229>'} {dungeon[3].display_name}\n{'<:DPS:1301204877900382229>'} {dungeon[4].display_name}",
                       inline=False)
    return players


# endregion
# region advancedmashup
# === Global Variables (ADVANCED MASHUP) ===
users = []  # List of users in the advanced mashup
advancedPlayers = []  # List of AdvancedPlayer objects
advancedmashup_event = None


class AdvancedPlayer:
    """
    Represents a player in Advanced Mashup mode, with chosen specs and metadata.
    """

    def __init__(self, user: Message.author, reactions: list[int]):
        self.user = user.display_name if hasattr(user,
                                                 'display_name') else user.display_name  # Use nickname if available
        self.reactions = [get_spec(r).get_icon() for r in reactions]  # Convert ints to spec icons
        self.specs = self.generate_specs()

    def generate_specs(self) -> list[Spec]:
        return [Spec(reaction) for reaction in self.reactions]

    def __repr__(self):
        return f"AdvancedPlayer(user={self.user}, specs={self.specs})"


def generate_advancedgroups(players: list[AdvancedPlayer]):
    """
    Create balanced groups from advanced players based on spec roles and utility.
    """
    groups = []
    remaining_players = players[:]
    random.shuffle(remaining_players)  # Shuffle players to mix up groupings

    while len(remaining_players) > 0:  # Ensure even small groups are created
        group = {
            "tank": None,
            "healer": None,
            "dps": [],
            "br": False,
            "hero": False
        }

        assigned_players = []  # Track assigned players to remove them later

        # Assign roles properly
        for player in remaining_players:
            for spec in player.specs:
                if spec.role == "tank" and group["tank"] is None:
                    group["tank"] = (player.user, spec)
                    assigned_players.append(player)
                    break
                elif spec.role == "heal" and group["healer"] is None:
                    group["healer"] = (player.user, spec)
                    assigned_players.append(player)
                    break
                elif spec.role == "dps" and len(group["dps"]) < 3:
                    group["dps"].append((player.user, spec))
                    assigned_players.append(player)
                    break

        # Ensure at least one BR and one Hero
        for role in ["tank", "healer"]:
            if group[role]:
                _, spec = group[role]
                if spec.br:
                    group["br"] = True
                if spec.hero:
                    group["hero"] = True

        for dps_player in group["dps"]:
            _, spec = dps_player
            if spec.br:
                group["br"] = True
            if spec.hero:
                group["hero"] = True

        # Ensure players are actually being assigned, or break loop to prevent infinite run
        if len(assigned_players) == 0:
            print("Warning: No players could be assigned. Breaking loop to prevent freeze.")
            break

        # Remove assigned players from remaining list
        for p in assigned_players:
            remaining_players.remove(p)

        # Add PUGs if needed
        if not group["tank"]:
            group["tank"] = ("PUG", Spec("Tank PUG"))  # ✅ Correct usage
        if not group["healer"]:
            group["healer"] = ("PUG", Spec("Healer PUG"))  # ✅ Correct usage
        while len(group["dps"]) < 3:
            group["dps"].append(("PUG", Spec("DPS PUG")))  # ✅ Correct usage

        groups.append(group)

    return groups


def format_groups_as_embed(groups, embedVar):
    """
    Formats generated groups into a Discord embed.
    """
    embedVar = Embed(title="Generated Groups", description="Here are the groups for the event:")
    for i, group in enumerate(groups, start=1):
        print(i)
        dungeon = [group["tank"], group["healer"]] + group["dps"]
        embedVar.add_field(
            name=f"Group {i}:",
            value=(
                f"<:tank:1301197903028817980> {dungeon[0][0]} ({dungeon[0][1].get_icon()})\n"
                f"<:healer:1301201583408808018> {dungeon[1][0]} ({dungeon[1][1].get_icon()})\n"
                f"<:DPS:1301204877900382229> {dungeon[2][0]} ({dungeon[2][1].get_icon()})\n"
                f"<:DPS:1301204877900382229> {dungeon[3][0]} ({dungeon[3][1].get_icon()})\n"
                f"<:DPS:1301204877900382229> {dungeon[4][0]} ({dungeon[4][1].get_icon()})"
            ),
            inline=False
        )
    return embedVar


async def send_advancedmashup(channel):
    """
    Sends the main advanced mashup embed with join button.
    """
    advancedPlayers.clear()
    embedVar = Embed(title="MYTHIC MASHUP",
                     description='Click the "Join Mashup" button to join',
                     color=0x00ff00)
    embeded_message = embedVar
    embeded_message.add_field(name="Players", value="")
    global advancedmashup_event
    advancedmashup_event = await channel.send(embed=embeded_message, view=Buttonstartup())


async def send_newadvancedmashup(channel: Message.channel, message: Message):
    """
    Sends the next round's embed for the advanced mashup with grouped results.
    """

    groups = generate_advancedgroups(advancedPlayers)
    temp = format_groups_as_embed(groups, message.embeds)
    await message.edit(embed=temp, view=Buttonstartup())


async def decode_response(message: str):
    """
    Parses a comma-separated string of spec IDs and returns validity + int list.
    """
    int_string = message.split(",")
    ints = []
    for i in int_string:
        try:
            ints.append(int(i))
        except ValueError:
            return False, ints
    for i in ints:
        if i < 1 or i > 39:
            return False
    return True, ints


def remove_player(user):
    """
    Removes a user from the advancedPlayers list by nickname.
    """
    global advancedPlayers
    advancedPlayers = [p for p in advancedPlayers if p.user != user.display_name]


class Buttonstartup(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label='Start Round', style=discord.ButtonStyle.green)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        if event_creators.get(guild_id) != interaction.user.id:
            await interaction.response.send_message("Only the event creator can start the round!", ephemeral=True)
            return

        if not advancedPlayers:
            await interaction.response.send_message("Not enough players to start the mashup.", ephemeral=True)
            return

        await send_newadvancedmashup(interaction.channel, interaction.message)
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label='Join Mashup', style=discord.ButtonStyle.blurple)
    async def join(self, interaction: discord.Interaction, button: discord.ui.button()):
        embedVar = Embed(title="Mythic Mashup",
                         description="Respond to this message with the specs you want to join with. You can choose multiple at once.",
                         color=0x00ff00)
        embedVar.add_field(name="Specs", inline=False,
                           value="1: <:Hunter_Marksmanship:1302704567485726730> Marksmanship Hunter \n2: <:Hunter_Beastmastery:1302704152488448020> Beastmastery Hunter \n3: <:Hunter_Survival:1302704155965788190> Survival Hunter \n4: <:Deathknight_Blood:1302704136575258818> Blood Deathknight \n5: <:Deathknight_Frost:1302704137888338053> Frost Deathknight \n6: <:Deathknight_Unholy:1302704139352145961> Unholy Deathknight \n7: <:Druid_Balance:1302704140916625521> Balance Druid \n8: <:Druid_Feral:1302704142111866880> Feral Druid \n9: <:Druid_Guardian:1302704143613296750> Guardian Druid \n10: <:Druid_Restoration:1302704144817197157> Restoration Druid \n11: <:Evoker_Augmentation:1302704563442417715> Augmentation Evoker \n12: <:Evoker_Devestation:1302704148118241351> Devestation Evoker \n13: <:Evoker_Preservation:1302704565749153802> Preservation Evoker")
        embedVar.add_field(name="", inline=False,
                           value="14: <:Deamonhunter_Havoc:1302704133371072614> Havoc Deamonhunter \n15: <:Deamonhunter_Vengeance:1302704135186944140> Vengeance Deamonhunter \n16: <:Mage_Arcane:1302704568752406578> Arcane Mage \n17: <:Mage_Fire:1302704159337742336> Fire Mage \n18: <:Mage_Frost:1302704570069155870> Frost Mage \n19: <:Monk_Brewmaster:1302704162466955377> Brewmaster Monk \n20: <:Monk_Mistweaver:1302704571403075614> Mistweaver Monk \n21: <:Monk_Windwalker:1302704165645975633> Windwalker Monk \n22: <:Paladin_Holy:1302704572652851290> Holy Paladin \n23: <:Paladin_Protection:1302704169026715700> Protection Paladin \n24: <:Paladin_Retribution:1302704574544613397> Retribution Paladin \n25: <:Priest_Discepline:1302704173493518478> Discepline Priest \n26: <:Priest_Holy:1302704175867625592> Holy Priest")
        embedVar.add_field(name="", inline=False,
                           value="27: <:Priest_Shadow:1302704179080335532> Shadow Priest \n28: <:Rogue_Assasination:1302704575832391742> Assasination Rogue \n29: <:Rogue_Outlaw:1302704183786602597> Outlaw Rogue \n30: <:Rogue_Subtlety:1302704186122702848> Subtlety Rogue \n31: <:Shaman_Elemental:1302706706383638648> Elemental Shaman \n32: <:Shaman_Enhancement:1302704189918679190> Enhancement Shaman \n33: <:Shaman_Restoration:1302704579221127268> Restoration Shaman \n34: <:Warlock_Affliction:1302704193970241627> Affliction Warlock \n35: <:Warlock_Demonologie:1302704581259690015> Demonologie Warlock \n36: <:Warlock_Destruction:1302704197225021532> Destruction Warlock \n37: <:Warrior_Arms:1302704659961741436> Arms Warrior \n38: <:Warrior_Fury:1302704201943617599> Fury Warrior \n39: <:Warrior_Protection:1302704585437085788> Protection Warrior")
        embedVar.set_footer(text="Respond with 3,6,20 for example")
        if users.count(interaction.user) != 1:
            users.append(interaction.user)
            await interaction.response.defer()
            await interaction.user.send(embed=embedVar)
            embedVAr = await self.edit_Field(interaction.user, "join")
            await advancedmashup_event.edit(embed=embedVAr, view=Buttonstartup())
        else:
            await interaction.response.defer()
            await interaction.user.send("You are already in this mashup")
            await advancedmashup_event.edit(view=Buttonstartup())
        self.stop()

    import re
    async def edit_Field(self, user, action):
        embedVar = advancedmashup_event.embeds[0]
        field_index = 0  # Assuming "Players" is at index 0

        # Get current players from embed
        field = embedVar.fields[field_index]
        players_list = field.value.split("\n") if field.value else []

        # Function to match names, ignoring emojis
        def match_user(display_name, players):
            for player in players:
                if re.match(re.escape(display_name) + r".*", player):
                    return player
            return None

        existing_entry = match_user(user.display_name, players_list)

        if action == "join":
            if not existing_entry:
                players_list.append(user.display_name)  # Add new name
        elif action == "leave":
            if existing_entry:
                players_list.remove(existing_entry)  # Remove matching name

        # Update the embed field with the new players list
        embedVar.set_field_at(field_index, name="Players", value="\n".join(players_list) or "No players yet")

        return embedVar

    @discord.ui.button(label='Leave Mashup', style=discord.ButtonStyle.gray)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.button()):
        if (len(users)) == 0:
            await interaction.user.send("You not in this mashup")
            await interaction.response.defer()
            return
        for u in users:
            if u.id == interaction.user.id:
                users.remove(u)

                embedVAr = await self.edit_Field(interaction.user, "leave")
                await advancedmashup_event.edit(embed=embedVAr, view=Buttonstartup())
                await interaction.response.defer()
                remove_player(interaction.user)
                break
            else:
                await interaction.user.send("You not in this mashup")
                await interaction.response.defer()
        self.stop()

    @discord.ui.button(label='End Mashup', style=discord.ButtonStyle.red)
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(thinking=True)
        except discord.InteractionResponded:
            pass

        # Delete all bot messages in the channel
        await clear_bot_messages(interaction.channel, interaction.client.user)

        # Clean up memory/state
        users.clear()
        advancedPlayers.clear()
        active_events.pop(interaction.guild.id, None)
        self.stop()


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return
    if users.count(message.author) == 1 and isinstance(message.channel, discord.DMChannel):
        check: bool
        roles: []
        check, roles = await  decode_response(str(message.content))
        if check:
            temp = advancedmashup_event.embeds[0].fields[0].value
            print(temp)
            s = temp.split(message.author.display_name)
            temp = s[0] + message.author.display_name
            temp1 = ""
            for r in roles:
                print(utils.get_spec(r).get_icon())
                temp1 = temp1 + utils.get_spec(r).get_icon()
            val = temp + temp1 + s[1]
            advancedPlayers.append(AdvancedPlayer(message.author, roles))
            print(len(advancedPlayers))
            await advancedmashup_event.edit(
                embed=advancedmashup_event.embeds[0].set_field_at(0, name="Players", value=val), view=Buttonstartup())
            await message.author.send("Added you to the Event")
        else:
            await message.author.send("Your response can only include numbers from 1-39 separated by ','")


# endregion
# main function that "starts" the bot
def main() -> None:
    client.run(token=TOKEN)


if __name__ == '__main__':
    main()
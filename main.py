#some code has been altered due to privacy concerns

import discord
import aiohttp
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix='-', description="", intents=intents)


@client.event #message to confirm the bot woke up correctly
async def on_ready():
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game("Terraria"))
    print("this bot is working correctly.")
    print("------------------------------")


@client.event
async def archive_msg(pinned): #archives a pinned message after it is detected in any given text channel this bot is in and uploads this message as an embedded message in a channel named 'archives' 
    guild = pinned.guild
    channel_name = "archives"
    archive_channel = discord.utils.get(guild.channels, name=channel_name)

    if not archive_channel: #create a text channel named 'archives' if this text channel does not currently exist in a given server.
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        archive_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)

    if archive_channel:
        timestamp = pinned.created_at.strftime("%Y-%m-%d")
        original_link = pinned.jump_url
        embed = discord.Embed(
            title=f"Pinned message from {pinned.author.display_name}",
            description=pinned.content,
            color=0xFF0000
    )
        embed.set_author(name=pinned.author.display_name, icon_url=pinned.author.avatar.url)
        embed.add_field(name="Timestamp", value=timestamp, inline=False)
        embed.add_field(name="Jump to Original Pinned Message", value=f"[Link]({original_link})", inline=False)
        await archive_channel.send(embed=embed)
    else:
        print("Error: Couldn't find the dedicated channel.")


@client.event #detects specific keywords or actions any given users sends in the server
async def on_message(message):

    profanity = ["enter profanity that is unfit for your server here."]
    profanity_length = len(profanity)
    for i in range(profanity_length):
        if profanity[i] in message.content:
            await message.delete()
            await message.channel.send("The message above this one has been deleted due to it containing certain disrespectful words.")

    await client.process_commands(message)

    if message.pinned:
        await archive_msg(message)


@client.event
async def on_message_edit(before, after):
    if after.pinned:
        await archive_msg(after)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Unknown command. Please try again or input the help command for further assistance.")


@client.command()
async def motd(ctx): #message of the day
    await ctx.send("enter a message of the day here.")


@client.command()
async def wotd(ctx): #word of the day
    url = f'https://api.wordnik.com/v4/words.json/wordOfTheDay?api_key=APIKEY'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                word_of_the_day = data.get('word')
                definition = data.get('definitions', [{}])[0].get('text', 'No definition available.')

                await ctx.send(f"Word of the Day: {word_of_the_day}\nDefinition: {definition}")

            else:
                await ctx.send("Failed to retrieve Word of the Day.")


class CustomHelpCommand(commands.HelpCommand):
    def __init__ (self):
        super().__init__()

    async def send_bot_help(self, mapping):

        embed = discord.Embed(
            title=f"{client.display_name}",
            description="Hello, here is a quick rundown on how each command works.\n"
                    "-motd #this command displays today's message of the day.\n"
                    "-wotd #this command displays today's word of the day.\n"
                    "-myhelp #this command displays all of the commands that are currently available and what they do.\n"
                    "-kick #this command kicks a given user if the command prompter has the permissions to.\n"
                    "-ban #this command bans a given user if the command prompter has the permissions to.",
            color=0xFF0000
    )

        for cog, commands in mapping.items():
            if cog:
                command_names = [command.name for command in commands]
                embed.add_field(name=cog.qualified_name, value=", ".join(command_names), inline=False)
        embed.set_author(name=client.display_name, icon_url=client.avatar.url)
        await self.context.send(embed=embed)


bot = commands.Bot(command_prefix='-', intents=intents, help_command=CustomHelpCommand())


@client.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="enter a reason here."):
    try:
        await member.kick(reason=reason)
        await ctx.send(f'User {member} has been kicked')
    except discord.Forbidden:
        await ctx.send("can't do that please try again.")


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to kick people.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Couldn't find specified user.")
    else:
        await ctx.send("An error occurred during the kicking process.\nPlease try again.")


@client.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="enter a reason here"):
    try:
        await member.ban(reason=reason)
        await ctx.send(f'User {member} has been banned')
    except discord.Forbidden:
        await ctx.send("can't do that please try again.")


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to ban people.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Couldn't find specified user.")
    else:
        await ctx.send("An error occurred during the banning process.\nPlease try again.")


client.run('BOT KEY')
bot.run('BOT KEY')

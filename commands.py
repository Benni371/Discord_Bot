
from decouple import config
import discord
from discord.ext import commands
import subprocess
from datetime import datetime

TOKEN = config("DISCORD_TOKEN")
bot = commands.Bot(intents=discord.Intents.all(), command_prefix='!')
bot.help_command = commands.DefaultHelpCommand()

# Commands that relate to the community
class CommunityCog(commands.Cog, name='Community'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def guidelines(self, ctx):
        """
        Outputs community guidlines
        """
        await ctx.send(
            """This server was created to help facilitate a clean atmosphere for gaming. Here are some general guidelines you should follow:
            - Try to keep swearing and foul language to a minimum
            - Trash talking is permitted but don't get out of hand
            - Keep GIFs clean and appropriate"""
            )
        return

class CreateCog(commands.Cog, name='Create'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role('The Bros', 'The Big Hoss')
    async def create_channel(ctx, arg1, arg2):
        """
        Those with The Bros role can create voice and text channels
        :param: type --> -v (voice) or -t (text)
        :param: name --> desired name for channel

        Example: !create_channel -v Bloodborne
        ** If the name has spaces, enclose the name in quotes **
        """
        if arg1 == "-t":
            guild = ctx.guild
            cat = discord.utils.get(guild.categories, name = "Chat Channels")
            await guild.create_text_channel(arg2, category = cat)
        elif arg1 == "-v":
            guild = ctx.guild
            cat = discord.utils.get(guild.categories, name = "Voice Channels")
            await guild.create_voice_channel(arg2, category = cat)
        
        return

    @commands.command(pass_context=True)
    async def poll(self, ctx, question, *options: str):
        """
        Any user can create a poll

        :param: question --> If it contains spaces wrap the question in quotes
        :param: options --> you can have up to 10 options. If the option contains a space wrap it in quotes

        Example: !poll "What is the best video game?" Skyrim "League of Legends" Fortnite "Elden Ring"
        """
        if len(options) <= 1:
            await ctx.send('You need more than one option to make a poll!')
            return
        if len(options) > 10:
            await ctx.send('You cannot make a poll for more than 10 things!')
            return

        if len(options) == 2 and options[0] == 'yes' and options[1] == 'no':
            reactions = ['✅', '❌']
        else:
            reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

        description = []
        for x, option in enumerate(options):
            description += '\n {} {}'.format(reactions[x], option)
        embed = discord.Embed(title=question, description=''.join(description))
        react_message = await ctx.send(embed=embed)
        for reaction in reactions[:len(options)]:
            await react_message.add_reaction(reaction)
        embed.set_footer(text='Poll ID: {}'.format(react_message.id))
        await react_message.edit(embed=embed)

    @commands.command(pass_context=True)
    async def tally(self, ctx, id=None):
        poll_message = await ctx.channel.fetch_message(id)
        embed = poll_message.embeds[0]
        unformatted_options = [x.strip() for x in embed.description.split('\n')]
        print(f'unformatted{unformatted_options}')
        opt_dict = {x[:2]: x[3:] for x in unformatted_options} if unformatted_options[0][0] == '1' \
            else {x[:1]: x[2:] for x in unformatted_options}
        # check if we're using numbers for the poll, or x/checkmark, parse accordingly
        voters = [self.bot.user.id]  # add the bot's ID to the list of voters to exclude it's votes

        tally = {x: 0 for x in opt_dict.keys()}
        for reaction in poll_message.reactions:
            if reaction.emoji in opt_dict.keys():
                reactors = await reaction.users().flatten()
                for reactor in reactors:
                    if reactor.id not in voters:
                        tally[reaction.emoji] += 1
                        voters.append(reactor.id)
        output = f"Poll Results for **{embed.title}**:\n" + '\n'.join(['{}: {}'.format(opt_dict[key], tally[key]) for key in tally.keys()])
        await ctx.send(output)

@bot.command()
async def restart(ctx: commands.Context):
    """
    Restarts the minecraft server container (hard stop)
    """
    now = datetime.now()
    exec_time = (now.strftime("%b-%d %I:%M %p"))
    await ctx.send("Restart command has been received. The server should do a full restart shortly")
    subprocess.run(("./server_commands.sh","0"), capture_output=True)
    msg = (f"{ctx.author.mention} restarted the server at {exec_time}")
    user = await bot.fetch_user(532684925208363017) #finds me
    await user.send(msg)
@bot.command()
async def stop(ctx: commands.Context):
    """
    Stops the minecraft server; Saves the server files (graceful stop)
    """
    now = datetime.now()
    exec_time = (now.strftime("%b-%d %I:%M %p"))
    await ctx.send("Stop command has been received. Please wait 5 minutes to allow the server time to save the files. You can check periodically for the servers status by using the `!status` command. If the command returns that the server is no longer running. You can restart it with the `!restart` command")
    subprocess.run(("./server_commands.sh","1"), capture_output=True)
    msg = (f"{ctx.author.mention} stopped the server at {exec_time}")
    user = await bot.fetch_user(532684925208363017) #finds me
    await user.send(msg) #sends me who reset the button

    return 0
@bot.command()
async def status(ctx: commands.Context):
    """
    Returns the status of the server
    """
    message = subprocess.check_output(["./server_commands.sh","3"])
    await ctx.send(message.decode().strip())



@bot.command()
@commands.has_any_role('The Bros', 'The Big Hoss')
async def flag(ctx, message_id):
    """
    To flag content that is deemed inappropriate. Owner will be DM'd

    :param: message_id --> message id can be retrieved by clicking the three dots while hovering over a message and clickng "copy id" at the bottom
    
    Example: !flag 982082516871675944
    """
    msg = await ctx.fetch_message(message_id)
    flagged_content = (f"{ctx.author.mention} reported {msg.author.mention} as saying:\n```{msg.content}```")
    user = await bot.fetch_user(532684925208363017) #finds me
    await user.send(flagged_content) # dms me the content

async def setup(bot):
    await bot.add_cog(CreateCog(bot))
    await bot.add_cog(CommunityCog(bot))
setup(bot)
bot.run(TOKEN)
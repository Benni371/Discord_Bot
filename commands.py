
from decouple import config
import discord
from discord.ext import commands


TOKEN = config("DISCORD_TOKEN")
bot = commands.Bot(command_prefix='!')
bot.help_command = commands.DefaultHelpCommand()

# Commands that relate to the community
class CommunityCog(commands.Cog, name='Community'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def guidelines(ctx):
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

    # @commands.command()
    # @commands.has_any_role('The Bros', 'The Big Hoss')
    # async def create_poll(ctx)

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

bot.add_cog(CreateCog(bot))
bot.add_cog(CommunityCog(bot))
bot.run(TOKEN)
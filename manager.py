# bot.py
from decouple import config
import discord

TOKEN = config('DISCORD_TOKEN')

class ManagerBotClient(discord.Client):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.guideline_msg = 981025601790046288
        
    async def on_raw_reaction_add(self, payload: discord.raw_models.RawReactionActionEvent):
        if payload.message_id != self.guideline_msg:
            return
        
        guild = client.get_guild(payload.guild_id)
        accepted_reactions = ['✅','👍','👌']
        print(f"{payload.member} reacted with {payload.emoji.name}")
        if payload.emoji.name in accepted_reactions:
            role = discord.utils.get(guild.roles, name='Newcomers')
            await payload.member.add_roles(role)
	    f = open("member_logs.txt","a")
            f.write(f"Newcomer Role added to {payload.member}")
            channel = client.get_channel(981026422732783656)
            await channel.send(f"{payload.member.mention} welcome to the server! We are glad to have you here 🎉")
        
    async def on_ready(self):
        print("Bot Online")

intents = discord.Intents.default()
intents.members = True
client = ManagerBotClient(intents=intents)
client.run(TOKEN)

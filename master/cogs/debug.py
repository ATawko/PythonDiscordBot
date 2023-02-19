from discord.ext import commands
import json

class Debug(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        #Run through config and assign variables
        with open(r'Misc/conf.json') as json_file:
            config  = json.load(json_file)
            self.APPROVED_USERS = config['APPROVED_USERS']
            self.BOT_OWNER = config['BOT_OWNER']

    #Shutdown Bot
    @commands.hybrid_command(pass_context=True, name="shutdown", help="Shutdown The Bot")
    async def shutdown(self, ctx):
        if ctx.message.author.id in self.APPROVED_USERS:
            await ctx.reply("Shutting Down. :(")
            await self.bot.close()
        else:
            await ctx.reply("You are not authorized to run this command.", ephemeral=True)

    #Echo back user's message
    @commands.hybrid_command(pass_context=True, name="echo", help='Returns Your Input')
    async def echo(self, ctx, content:str):
        await ctx.reply(content)

    @commands.hybrid_command(pass_context=True, name="rmmsg", help="Remove a message from the bot. Approved users only")
    async def rmmsg(self, ctx, channel:str, message: str):
        await ctx.defer(ephemeral=True)

        if str(ctx.message.author.id) == self.BOT_OWNER:
            channel_element = self.bot.get_channel(int(channel))
            msg = await channel_element.fetch_message(int(message))
            await msg.delete()

            await ctx.reply(f"Compleated")
        else:
            await ctx.reply("You are not authorized to run this command.")



    #Try to sync
    @commands.command(pass_context=True, name="sync", hidden=True)
    async def sync(self, ctx) -> None:
        if str(ctx.message.author.id) == self.BOT_OWNER:
            await ctx.defer(ephemeral=True)
            fmt = await ctx.bot.tree.sync(guild=ctx.guild)
            await ctx.reply(f"Synced {len(fmt)} commands to the current server.")
            return
        else:
            await ctx.reply("You are not authorized to run this command.")


async def setup(bot):
    await bot.add_cog(Debug(bot))
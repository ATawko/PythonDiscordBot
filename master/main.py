from discord.ext import commands
import discord, json, os, asyncio


#Run through config and assign variables
with open(r'Misc/conf.json') as json_file:
    config          = json.load(json_file)
    TOKEN           = config['TOKEN']
    PREFIX          = config['PREFIX']
    TRACKED_SERVERS = config['TRACKED_SERVERS']
    BOT_USER        = config['BOT_USER']
    BOT_OWNER       = config['BOT_OWNER']


help_command = commands.DefaultHelpCommand(
    no_category = 'Help'
)

#Load Extensions
async def load_extensions(bot):
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            name = file[:-3]
            await bot.load_extension(f"cogs.{name}")
            print(f"Loaded: cogs.{name}")


#Build Bot Object
#New Testing - Slash Commands
class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        #intents.message_content = True #Used for tracking, you will need to enable the Message Content Intent 
        #intents.members = True
        super().__init__(command_prefix=PREFIX, intents=intents, help_command=help_command)

    async def setup_hook(self):
        await self.tree.sync()#Don't sync too often it is rate limited
        print('Synced {0.user}'.format(bot))
    
    async def on_command_error(self, ctx, error):
        try:
            if not error.retry_after == None:
                await ctx.reply(f'This command is rate limited. Please try again in {int(error.retry_after)} seconds')
        except:
            await ctx.reply("It's not you it's me... Something broke", ephemeral=True)


        print(error)

bot = DiscordBot()

#####################
#                   #
#     Bot Hooks     #
#                   #
#####################

#Login Confirmation
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

    print("\nI'm in the following guilds!")
    for guild in bot.guilds:
        print(guild)
    print()

    #Start scheduled tasks
    asyncio.get_event_loop().create_task(bot.cogs['Scheduled'].scheduledTasks(), name="ScheduledTasks")
    asyncio.get_event_loop().create_task(bot.cogs['Music'].queuedMusic(), name="MusicQueue")
    #await bot.change_presence(activity=discord.Game(name="with your Mom"))


# #ALWAYS LISTENING
@bot.listen('on_message')
async def my_message(message):

    try:
        #This requires the Message Content Intent - You also have to uncomment the intent above
        # if not message.guild == None:
        #     #Totally Optional Tracking - Remove if unnecessary
        #     if (message.guild.id in TRACKED_SERVERS) and (not message.author.id == BOT_USER):
        #         await bot.cogs['Tracking'].messageProcessing(message)

        #DM Handling - Will Auto Forward DM's to BOT_OWNER in Config
        if (message.guild == None) and (not message.author.id == BOT_USER):
            user = bot.get_user(BOT_OWNER)
            await user.send(f"User: {message.author.display_name}#{message.author.discriminator} sent me the DM:\n```{message.content}```")
            
    except Exception as e:
        print(f"Failed to process message: {e}")




#Start Bot
asyncio.run(load_extensions(bot))
bot.run(TOKEN)
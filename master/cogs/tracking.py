import time
from discord.ext import commands

class Tracking(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def messageProcessing(self, message):
        #Start Tracking Execution Time
        startTime = time.time()

        #Print message & Server to console
        if len(message.attachments) > 0:
            print(f"\nServer: {message.guild.name} | Channel: {message.channel.name} | Author: {message.author.name}\nMessage: {message.content}")
            for attachment in message.attachments:
                print(f"Attachment(s): {attachment.url}")
        else:
            print(f"\nServer: {message.guild.name} | Channel: {message.channel.name} | Author: {message.author.name}\nMessage: {message.content}")

        endTime = time.time()
        print(f"Execution Time: {round(endTime - startTime, 5)} seconds")



async def setup(bot):
    await bot.add_cog(Tracking(bot))
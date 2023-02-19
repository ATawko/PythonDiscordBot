import discord, yt_dlp, asyncio, time
from discord.ext import commands

checksWithNoAudio = []

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_command(name="play", help='Will play the requested song. Use non-links at your own risk')
    async def newNewPlay(self, ctx, song: str):

        await ctx.defer()
        startTime = time.time()
        alreadyInVoice = False
        queuedChannelID = 0
        
        # Validate that the user is in a voice channel
        if not ctx.author.voice:
            return await ctx.reply("You are not currently in a voice channel.")
        
        try:
            # Connect to the user's voice channel
            channel = ctx.author.voice.channel
            vc = await channel.connect()
        except Exception as e:
            if not e.args[0] == "Already connected to a voice channel.":                    
                print(f"Error Joining Voice\n{e}")
                return await ctx.reply("Error Joining voice")
            else:
                alreadyInVoice = True
                queuedChannelID = ctx.author.voice.channel.id

        #Download Song
        musicInfo = await YTDLPSource.from_url(song, loop=self.bot.loop)

        #Build an Embed to Confirm Now Playing Song
        try:
            embed = discord.Embed(
                title=f"Now Playing: {musicInfo['title']}", 
                description=f"""Uploader: {musicInfo['uploader']}\nDuration: {musicInfo['duration_string']}\nViews: {musicInfo['view_count']:,}""", 
                url=musicInfo['webpage_url'],
                color=0xff0000)
            embed.set_thumbnail(url=musicInfo['thumbnail'])
                
        except Exception as e:
            print("Failed to generate Embed - Falling back to default")
            embed = discord.Embed(
                title=f"Now Playing: {musicInfo['filename'][6:]}",
            )

        #Play Music
        if alreadyInVoice:
            embed.title=f"Queued Song: {musicInfo['title']}"
            with open('Misc/MusicQueue.txt', 'a') as f:
                f.seek(0, 2)
                if f.tell() == 0:
                    f.write(f"{song}|{queuedChannelID}")
                else:
                    f.write(f'\n{song}|{queuedChannelID}')
        else:
            vc.play(discord.FFmpegPCMAudio(musicInfo['filename']))
            vc.source = discord.PCMVolumeTransformer(vc.source)

        endTime = time.time()
        embed.set_footer(text=f"Completed in {round(endTime - startTime, 2)} seconds")
        await ctx.reply(embed=embed)


 
    #Stop Music
    @commands.hybrid_command(name='stop', help='Stops the current song')
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            await ctx.reply("Stopped Playing")
        else:
            await ctx.reply("The bot is not playing anything at the moment.", ephemeral=True)

    #Disconnect from Voice
    @commands.hybrid_command(name="disconnect", help="Disconnects the bot from Voice")
    async def disconnect(self, ctx):
        try:
            voice_client = ctx.message.guild.voice_client
            if voice_client.is_connected():
                await voice_client.disconnect()
                await ctx.reply("Disconnected Bot")
            else:
                await ctx.reply("The bot is not connected to a voice channel.", ephemeral=True)

        except Exception as e:
            await ctx.reply("Not Connected To Voice", ephemeral=True)
            return

    #Song Queue
    async def queuedMusic(self):

        while True:
            #print("\nRunning Music Queue")
            startTime = time.time()
            global checksWithNoAudio
            startedPlaying = False

            #IDK What users are going to do, so just in case they break it
            try:
                if len(self.bot.voice_clients) > 0:
                    songs = []
                    removeFromQueue = []

                    #Get songs from queue
                    with open('Misc/MusicQueue.txt', 'r+') as queueInput:
                        if queueInput is not None:
                            for line in queueInput:
                                if not line == "\n": 
                                    songs.append(line)
                    queueInput.close()

                    print(f"{len(songs)} Songs in queue | {songs}")
                    if len(songs) > 0: #Songs in queue
                        #Sort through queued songs
                        for song in songs:
                            parts = song.split('|')

                            #For each voice client, see if there's a queued song & play it
                            for vc in self.bot.voice_clients:
                                print(f"Checking Queue. | ChannelID: {vc.channel.id} | Song Queue ID: {int(parts[1])}")
                                if (vc.channel.id == int(parts[1][:-1])) or (vc.channel.id == int(parts[1])):
                                    if not vc.is_playing() and not startedPlaying:
                                        print(f"Trying to Play Song: {song}")
                                        musicInfo = await YTDLPSource.from_url(parts[0], loop=self.bot.loop)

                                        vc.play(discord.FFmpegPCMAudio(musicInfo['filename']))
                                        vc.source = discord.PCMVolumeTransformer(vc.source)
                                        
                                        removeFromQueue.append(song)
                                        startedPlaying = True
                            
                    #Try to clean up rogue sessions? Anything queued should have played
                    for vc2 in self.bot.voice_clients:
                        print(f"Checking VC ID: {vc2.channel.id} | Playing Status: {vc2.is_playing()} | Current Checks: {checksWithNoAudio}")
                        if len(checksWithNoAudio) > 0: 
                            for i in range(0, len(checksWithNoAudio)):
                                if checksWithNoAudio[i][0] == vc2.channel.id:
                                    if (not vc2.is_playing()) and (checksWithNoAudio[i][1] == 2): 
                                        await vc2.disconnect()
                                        print(f"Disconnecting Due To Non Use From Channel: {vc2.channel.id}")
                                        del checksWithNoAudio[i]
                                    elif (not vc2.is_playing()) and (checksWithNoAudio[i][1] < 2):
                                        print(f"VC2 Playing Status: {vc2.is_playing()} | Under 2 Checks")
                                        checksWithNoAudio[i][1] += 1
                                    elif vc2.is_playing():
                                        print(f"We're playing now, removing channel from checks. {checksWithNoAudio}")
                                        del checksWithNoAudio[i]
                                    else:
                                        print("IDK")
                                        print(f"VC2 Playing: {vc2.is_playing()} | Channel: {vc2.channel.id} | checksWithNoAudio: {checksWithNoAudio}")
                        elif not vc2.is_playing():
                            #Add server to checks
                            print(f"We're not playing: {vc2.is_playing()} | Current Channel Is: {vc2.channel.id}")
                            checksWithNoAudio.append([vc2.channel.id, 1])

                    #If there's something to remove from the queue remove it
                    if len(removeFromQueue) > 0:
                        for toUpdate in removeFromQueue:
                            with open('Misc/MusicQueue.txt', 'r+') as file:
                                lines_to_keep = []
                                for line in file:
                                    if line != toUpdate:
                                        lines_to_keep.append(line)
                                file.seek(0)
                                file.writelines(lines_to_keep)
                                file.truncate()
                            file.close()

                else:
                    #print("No VC Clients, Goodbye Queue")
                    open('Misc/MusicQueue.txt', 'w').close()

                    #endTime = time.time()
                    #print(f"Music Execution Time: {round(endTime - startTime, 5)} seconds\n")

            except:
                print(f"Music Queue Failed. IDK Why")
            

            #Lets do the time warp again!
            #print("And here we go again")
            await asyncio.sleep(30)


#Youtube DL Stuff - Don't fuck with it I guess
yt_dlp.utils.bug_reports_message = lambda: ''

ytdlp_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'outtmpl' : 'Music/%(extractor)s-%(id)s-%(title)s.%(ext)s'
}

ffmpeg_options = {'options': '-vn'}
ytdlp = yt_dlp.YoutubeDL(ytdlp_format_options)

class YTDLPSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdlp.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdlp.prepare_filename(data)
        data['filename'] = filename
        return data



async def setup(bot):
    await bot.add_cog(Music(bot))
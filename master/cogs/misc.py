import discord, random, json, requests, sqlite3, time, re
from enum import Enum
from discord.ext import commands

class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        #Run through config and assign variables
        with open(r'Misc/conf.json') as json_file:
            config  = json.load(json_file)
            self.WEATHER_API_KEY   = config['WEATHER_API_KEY']

    @commands.hybrid_command(name="randomcommander", help="Returns a random MTG commander from Scryfall")
    async def randCommander(self, ctx):
        await ctx.defer()

        request = requests.get("https://api.scryfall.com/cards/random?q=is%3Acommander")
        card = json.loads(request.text)

        embed = discord.Embed(title=f"{card['name']} {card['mana_cost']}", description="", url=card['scryfall_uri'], color=0x0000ff)
        embed.add_field(name='Type', value=card['type_line'], inline=False)
        embed.add_field(name="Oracle Text", value=card['oracle_text'], inline=False)

        try: embed.add_field(name="P/T", value=f"{card['power']} / {card['toughness']}", inline=False)
        except: pass
        
        try: embed.add_field(name="Loyalty", value=card['loyalty'], inline=True)
        except: pass
        
        embed.set_image(url=card['image_uris']['normal'])

        await ctx.reply(embed=embed)

    #Retrieve a random joke from API
    @commands.hybrid_command(name="joke", help="Makes a Joke")
    async def randomJoke(self, ctx):
        await ctx.defer()

        request = requests.get("https://official-joke-api.appspot.com/random_joke")
        joke = json.loads(request.text)

        if request.status_code == 200:
            await ctx.reply(f"{joke['setup']}\n||{joke['punchline']}||")
        else:
            await ctx.reply("What do you get when the Joke API fails?\n||This Message||")

    #Pull weather data
    #This requires a OpenWeatherMap API key saved in the config
    @commands.hybrid_command(name="weather", help="Provides the weather. Usage: weather [location]")
    async def getWeather(self, ctx, location:str):

        #Acknowledge command
        await ctx.defer()

        r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&APPID={self.WEATHER_API_KEY}")
        weather = json.loads(r.text)

        if r.status_code == 200:

            #Convert Kelvin to Celsius 
            weather['main']['temp']         = round(weather['main']['temp'] - 273.15, 2)
            weather['main']['feels_like']   = round(weather['main']['feels_like'] - 273.15, 2)
            weather['main']['temp_min']     = round(weather['main']['temp_min'] - 273.15, 2)
            weather['main']['temp_max']     = round(weather['main']['temp_max'] - 273.15, 2)

            #Build reply as Embed
            embed = discord.Embed(title=f"{weather['name']}", description=f"Lat: {weather['coord']['lat']} Lon: {weather['coord']['lon']}", color=0xff0000)
            embed.add_field(name="Current", value=weather['weather'][0]['description'], inline=True)
            embed.add_field(name="Temp", value=f"{weather['main']['temp']}°c", inline=True)
            embed.add_field(name="Feels Like", value=f"{weather['main']['feels_like']}°c", inline=True)
            embed.add_field(name="Extra Details:", value=f"MaxTemp: **{weather['main']['temp_max']}°c**\nMinTemp: **{weather['main']['temp_min']}°c**\nPressure: **{weather['main']['pressure']}hPa**\nHumidity: **{weather['main']['humidity']}%**\nWind Speed: **{weather['wind']['speed']}km/h**", inline=True)
            await ctx.reply(embed=embed)

        else:
            await ctx.reply("Error Fetching", ephemeral=True)

    #Random Pokemon
    class PokemonOptions(str, Enum):
        Shiny       = "s"
        Not_Shiny   = ""
    
    @commands.hybrid_command(name='pkmn', help='Usage: pk [name/id] [shiny (s)] Name & Shiny Optional')
    async def rand_pokemon(
        self, 
        ctx, 
        name: str = "",
        shiny: PokemonOptions = ""
        ):

        #Acknowledge Command
        await ctx.defer()

        #If no name supplied, pick a random Pokemon
        if name == "" or name == " ":
            pkID = random.randint(1, 1008)

            # 1% chance for the random to be Shiny
            if random.randint(1, 100) == 1:
                shiny = "s"

            #Call API & parse into List
            r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pkID}")
            pokemon = json.loads(r.text)
        else: #Pokemon was provided - search for this one
            r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}")
            
            #API Failed to return - assuming Pokemon doesn't exist
            if not r.status_code == 200:
                await ctx.message.channel.send("Feeling Existential Dread? So Is This Pokemon, It Doesn't Exist")
                return

            pokemon = json.loads(r.text)
 
        #Sift through types
        pkmnTypes = ""
        for type in pokemon['types']:
            pkmnTypes = (pkmnTypes + type['type']['name'].title() + ", " )

        #Sift through Abilities
        pkmnAbilities = ""
        for ability in pokemon['abilities']:
            pkmnAbilities = (pkmnAbilities + ability['ability']['name'].title() + ", " )

        #Build Stats
        pkmnStats = ""
        for stat in pokemon['stats']:
            pkmnStats = (pkmnStats + str(stat['base_stat']) + "/")

        #Set Embed Colour
        if shiny == "s":
            colour = 0xC0C0C0
        else:
            colour = 0xff0000

        #Start the Embed
        embed = discord.Embed(
            title=f"{pokemon['name'].title()}", 
            description=f"""
            Dex Number: {pokemon['id']}
            Type(s): {pkmnTypes[:-2]}
            Abilities: {pkmnAbilities[:-2]}
            Stats: {pkmnStats[:-1]}
            """, 
            url=f"https://bulbapedia.bulbagarden.net/wiki/{pokemon['name']}_(Pokémon)",
            color=colour)

        #Set Image
        if not shiny == "s":
            embed.set_image(url=pokemon['sprites']['front_default'])
        else:
            embed.set_image(url=pokemon['sprites']['front_shiny'])
        
        #Send
        await ctx.reply(embed=embed)


    class ReminderOptions(str, Enum):
        Minutes = "Mins"
        Hours   = "Hours"
        Days    = "Days"

    @commands.hybrid_command(name="remindme", with_app_command=True, help="Set a Reminder! T")
    async def remindme(
        self, 
        ctx: commands.Context, 
        duration: int,
        classification: ReminderOptions, 
        message: str
    ):
        await ctx.defer(ephemeral=True)
        
        currentEpoch = time.time()
        scheduledEpoch = 0
        reminder = re.sub('[^A-Za-z0-9]+', ' ', message)

        if classification == "Mins":
            scheduledEpoch = (currentEpoch + (int(duration) * 60))
        elif classification == "Hours":
            scheduledEpoch = (currentEpoch + (int(duration) * 3600))
        elif classification == "Days":
            scheduledEpoch = (currentEpoch + (int(duration) * 86400))

        conn = sqlite3.connect("Misc/reminders.db")
        sql = f"INSERT INTO scheduled (userID,dateTime,message,completed) VALUES ('{ctx.author.id}', '{int(scheduledEpoch)}', '{reminder}','0')"
        
        conn.execute(sql)
        conn.commit()
        conn.close()


        await ctx.reply(f"Reminder Set for: {duration} {classification} from now with message: {message}")

async def setup(bot):
    await bot.add_cog(Misc(bot))


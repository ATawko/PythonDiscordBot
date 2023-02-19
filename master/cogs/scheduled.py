import sqlite3, time, asyncio, os
from discord.ext import commands

class Scheduled(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.scheduledFrequency = 30
        self.dailyFinished = False

    #Scheduled Reminders
    async def scheduledReminders(self, startTime):
        scheduledMessages = []

        #Fetch Messages
        sql = f"""SELECT id, userID, dateTime, message FROM scheduled WHERE completed IS 0"""
        conn    = sqlite3.connect("Misc/reminders.db")
        cursor  = conn.execute(sql)

        #Build Message List
        for row in cursor:
            scheduledMessages.append({
                "id":       row[0],
                "userID":   row[1],
                "dateTime": row[2],
                "message":  row[3]
            })

        #Close DB for now
        conn.close()

        #Send Messages
        for message in scheduledMessages:
            if time.time() > int(message["dateTime"]):
                user = self.bot.get_user(int(message["userID"]))
                await user.send(f"This is your scheduled reminder for: \n{message['message']}")

                #Update Database so we don't keep sending messages
                conn    = sqlite3.connect("Misc/reminders.db")
                sql = f"""UPDATE scheduled SET completed = 1 WHERE id IS {int(message['id'])}"""
                cursor  = conn.execute(sql)
                conn.commit()
                conn.close()

                print(f"Sent Following Message: \n {message}")
                endTime = time.time()
                print(f"Reminders Execution Time: {round(endTime - startTime, 5)} seconds")

    async def dailyTasks(self, startTime):
        #Start Daily Tasks
        if (not self.dailyFinished) or (time.strftime("%H:%M") == "12:00"):
            print(f'Starting Tasks: {time.strftime("%H:%M")}\n')

            #Clear Data from Folders
            folders = ["Music"]
            for folder in folders:
                path = os.path.abspath(folder)
                print(f"----- Deleting {folder} Folder -----")
                for file_name in os.listdir(path):
                    # construct full file path
                    file = path + "\\" + file_name
                    if os.path.isfile(file):
                        print('Deleting file:', file)
                        os.remove(file)
                print()

            #Make MusicQueue File If Not Exists
            if not os.path.exists("Misc/MusicQueue.txt"):
                with open("Misc/MusicQueue.txt", "w") as f:
                    f.close()

            endTime = time.time()
            print(f"Dailys Execution Time: {round(endTime - startTime, 5)} seconds")
            self.dailyFinished = True

        #Reset daily flag at noon
        if time.strftime("%H:%M") == "12:00":
            self.dailyFinished = False


    #Scheduled Tasks!
    async def scheduledTasks(self):
        while True:
            #Start Tracking Execution Time
            startTime = time.time()

            try:
                #Check For & Send Reminders
                await self.scheduledReminders(startTime)
                await self.dailyTasks(startTime)
    
            except Exception as e:
                print(e)

                endTime = time.time()
                print(f"\nErrored Tasks Execution Time: {round(endTime - startTime, 5)} seconds")

                await asyncio.sleep(self.scheduledFrequency)

            #Lets do the time warp again!
            await asyncio.sleep(self.scheduledFrequency)



async def setup(bot):
    await bot.add_cog(Scheduled(bot))
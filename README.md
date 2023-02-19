# DiscordBot_Py
This is a self hostable Discord bot! This is currently under development and is a side project for servers with friends 

This repository is intended to serve as a reference with some example files have been provided along with some example commands


# Discord
You will need to create a Discord Application and Bot user for this to function
Discord's documentation is available here: https://discord.com/developers/applications
This bot does not require any of the privlaged intents by default
For message tracking you will need to enable the Message Content Intent


# Docker
This bot was intended to run inside a docker container, a dockerfile has been provided to easily build the image
You will need to specify the Time Zone in the dockerfile

For ease of use, I've included both the build command and a run command below:
- docker build -t [IMAGE_NAME] .
- docker run -d --name [CONTAINER_NAME] [IMAGE_NAME]
You are required to give the image and container a unique name
So far, I've tested the build on the following platforms:
- ARM (RaspberryPi 4)
- Intel (2019 Macbook Pro)
- AMD (Ryzen 7 3800X)

### conf.json Example
A blank Configuration has been provided for ease of use
You will need to enter the required fields before starting
```
{
    "TOKEN":"BOT_TOKEN",
    "PREFIX":"^",
    "APPROVED_USERS": [USER_ID],
    "WEATHER_API_KEY": "OPEN_WEATHER_MAP_API_KEY",
    "TRACKED_SERVERS": [GUILD_ID],
    "BOT_USER": BOT_USER_ID,
    "BOT_OWNER": BOT_OWNER_ID
}
```

### reminders.db Create Statement
A blank DB has been included for ease of use
```
CREATE TABLE "scheduled" (
	"id"	INTEGER NOT NULL UNIQUE,
	"userID"	INTEGER NOT NULL,
	"dateTime"	TEXT NOT NULL,
	"message"	TEXT NOT NULL,
	"completed"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
)
```

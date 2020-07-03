import discord
import configuration
import requests # For get rest api
import json
import os
import datetime
import asyncio

from datetime import datetime
from discord.ext import commands

from deezerDownloader import deezerDownloaderCommand

# ------------------------ COGS ------------------------ #  

class TrackCog(commands.Cog, name="TrackCog"):
    def __init__(self, bot):
        self.bot = bot

# ------------------------------------------------------- #

    @commands.command(name = 'track')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def track (self, ctx, *args):

        args = str(args); args = args.replace(',',''); args = args.replace("'",""); args = args.replace("(",""); args = args.replace(")","")
        music = args

        requestSearch = requests.get(f'https://api.deezer.com/search/track?q={music}&index=0&limit=10&output=json') # Limit : 10
        data = requestSearch.json()

        if data['data'] == []:
            embed = discord.Embed(title = f"**NO MUSIC FOUND**", description = f"No music found with your research : ``\"{music}\"``", color = 0xff0000)
            embed.set_footer(text = "Bot Created by Darkempire#8245")
            await ctx.channel.send(embed = embed)
            ctx.command.reset_cooldown(ctx) # Reset the cooldown
        else:
            numberOfMusicInList = 0
            musicList = ""
            for x in data['data']:
                numberOfMusicInList +=1
                musicList = f"{musicList}**{numberOfMusicInList})** {x['title']} - {x['artist']['name']}\n"
            
            # Send music List
            embed = discord.Embed(title = f"**LIST OF FOUND MUSICS**", description = "[**GitHub**](https://github.com/Darkempire78/DeezerDownloader-Discord-Bot)", color = 0xea8700)
            embed.add_field(name = "**CHOOSE THE NUMBER THAT CORRESPONDS TO THE MUSIC :**", value = f"{musicList}\n**0) To exit (pass the cooldown)**", inline=False)
            embed.set_footer(text = "Bot Created by Darkempire#8245")
            await ctx.channel.send(embed = embed)

            def check(message):
                try:
                    message.content = int(message.content)
                    if ((message.content >= 0) and (message.content <= numberOfMusicInList)):
                        message.content = str(message.content)
                        return message.content
                    else:
                        pass
                except:
                    pass
            try:
                msg = await self.bot.wait_for('message', timeout=15.0, check=check)
                if (int(msg.content) == 0):
                    # Stop and reset the cooldown
                    embed = discord.Embed(title = f"", description = "You stopped your search. ", color = 0xff0000)
                    embed.set_footer(text = "Bot Created by Darkempire#8245")
                    await ctx.channel.send(embed = embed)
                    ctx.command.reset_cooldown(ctx) # Reset the cooldown
                else:
                    # Loading message send 
                    embed = discord.Embed(title = f"", description = "Loading music in progress...", color = 0xea8700)
                    embed.set_footer(text = "Bot Created by Darkempire#8245")
                    embedDownloading = await ctx.channel.send(embed = embed)

                    msg.content = int(msg.content)
                    msg.content = msg.content - 1
                    # Find data
                    musicId = data['data'][msg.content]['id']
                    musicUrl = data['data'][msg.content]['link']
                    longMusicName = data['data'][msg.content]['title']
                    musicName = data['data'][msg.content]['title_short']
                    musicAuthor = data['data'][msg.content]['artist']['name']
                    musicDuration = data['data'][msg.content]['duration']
                    musicCover = data['data'][msg.content]['album']['cover_big']
                    musicAlbum = data['data'][msg.content]['album']['title']
                    musicPreview = data['data'][msg.content]['preview']
                    
                    # Find album date 
                    requestTrack = requests.get(f'https://api.deezer.com/track/{musicId}') 
                    dataTrack = requestTrack.json()
                    
                    albumDate = dataTrack['album']['release_date']

                    # Find music duration
                    musicDurationMin = 0
                    while musicDuration > 60:
                        musicDuration -= 60
                        musicDurationMin += 1
                    if musicDuration < 10:
                        musicDuration = f"0{musicDuration}"

                    # Download preview
                    url = musicPreview
                    r = requests.get(url, allow_redirects=True)
                    open(f'downloads\PREVIEW {musicName}.mp3', 'wb').write(r.content)

                    # Set up embed 
                    embed = discord.Embed(title = f"**{longMusicName} - {musicAuthor}**", description = "[**GitHub**](https://github.com/Darkempire78/DeezerDownloader-Discord-Bot)", color = 0x2f9622)
                    embed.set_thumbnail(url = f"{musicCover}")
                    embed.add_field(name = "**MUSIC INFORMATIONS :**", value = f"**Artist :** {musicAuthor}\n**Album :** {musicAlbum} ({albumDate[:4]})\n**Duration :** {musicDurationMin}:{musicDuration} min", inline=False)
                    embed.set_footer(text = "Bot Created by Darkempire#8245")
                    file = discord.File(f'downloads\PREVIEW {musicName}.mp3')
                    await ctx.channel.send(file=file, embed=embed) # Send embed
                    await embedDownloading.delete() # Remove downloading message

                    os.remove(f"downloads\PREVIEW {musicName}.mp3") # remove preview

                    
            except (asyncio.TimeoutError):
                embed = discord.Embed(title = f"**TIME IS OUT**", description = "You exceeded the response time (15s)", color = 0xff0000)
                embed.set_footer(text = "Bot Created by Darkempire#8245")
                await ctx.channel.send(embed = embed)
                ctx.command.reset_cooldown(ctx) # Reset the cooldown

# ------------------------ BOT ------------------------ #  

def setup(bot):
    bot.add_cog(TrackCog(bot))
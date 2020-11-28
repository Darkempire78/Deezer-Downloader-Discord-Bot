import discord
import configuration
import requests # For get rest api
import json
import os
import datetime
import asyncio

from datetime import datetime
from discord.ext import commands

from deezloader2 import Login2


# ------------------------ COGS ------------------------ #  

class DownloadCog(commands.Cog, name="DownloadCog"):
    def __init__(self, bot):
        self.bot = bot

# ------------------------------------------------------- #

    @commands.command(name = 'download')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def download (self, ctx, *args):

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
                    embed = discord.Embed(title = f"", description = "Downloading music in progress...", color = 0xea8700)
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
                    
                    # Find album date 
                    requestTrack = requests.get(f'https://api.deezer.com/track/{musicId}') 
                    dataTrack = requestTrack.json()
                    
                    albumDate = dataTrack['album']['release_date']

                    def musicSize(duration):
                        size = duration*320/8
                        return size
                    
                    size = musicSize(musicDuration)
                    # Choose the good music quality
                    musicQuality = None
                    if size < 7800:
                        musicQuality = "320"
                    else:
                        musicQuality = "128"

                    # Download
                    downloa = Login2(configuration.arl)
                    
                    try:
                        downloa.download_trackdee(
                            musicUrl,
                            output = "downloads",
                            quality = f"MP3_{musicQuality}",
                            recursive_quality = False,
                            recursive_download = True
                        )
                    except:
                        embed = discord.Embed(title = f"**ERROR**", description = "Error during the track downloding...", color = 0xff0000)
                        embed.set_footer(text = "Bot Created by Darkempire#8245")
                        await ctx.channel.send(embed = embed)
                        await embedDownloading.delete() # Remove downloading message
                        return # Stop the function

                    # Check if file is not too big that 8 Mo (Discord limit)
                    musicSize = os.path.getsize(f'downloads\{musicName} {musicAuthor} ({musicQuality}).mp3')
                    if musicSize > 8000000:
                        # Remove last files
                        os.remove(f"downloads\{musicName} {musicAuthor} ({musicQuality}).mp3")
                        try:
                            os.remove(f"downloads\{musicName}.lrc")
                        except:
                            pass
                        if musicQuality == "128":
                            embed = discord.Embed(title = f"**THE FILE IS TOO BIG**", description = "The music file exceeds the maximum size of Discord.", color = 0xff0000)
                            embed.set_footer(text = "Bot Created by Darkempire#8245")
                            await ctx.channel.send(embed = embed)
                            await embedDownloading.delete() # Remove downloading message
                            return # Stop the function
                        else:
                            musicQuality = "128"
                            try:
                                downloa.download_trackdee(
                                    musicUrl,
                                    output = "downloads",
                                    quality = f"MP3_{musicQuality}",
                                    recursive_quality = False,
                                    recursive_download = True
                                )
                            except:
                                embed = discord.Embed(title = f"**ERROR**", description = "Error during the track downloding...", color = 0xff0000)
                                embed.set_footer(text = "Bot Created by Darkempire#8245")
                                await ctx.channel.send(embed = embed)
                                await embedDownloading.delete() # Remove downloading message
                                return # Stop the function
                            if musicSize > 8000000:
                                embed = discord.Embed(title = f"**THE FILE IS TOO BIG**", description = "The music file exceeds the maximum size of Discord.", color = 0xff0000)
                                embed.set_footer(text = "Bot Created by Darkempire#8245")
                                await ctx.channel.send(embed = embed)
                                await embedDownloading.delete() # Remove downloading message
                                # Remove last files
                                os.remove(f"downloads\{musicName}.mp3")
                                try:
                                    os.remove(f"downloads\{musicName}.lrc")
                                except:
                                    pass
                                return # Stop the function
                    # If the file is not too big
                    # Check if lyrics exist
                    lyricsPath = f"downloads\{musicName}.lrc"
                    musicLyricsExist = None

                    if os.path.exists(lyricsPath):
                        musicLyricsExist = True
                    else:
                        musicLyricsExist = False 

                    # Set up embed 
                    embed = discord.Embed(title = f"**{longMusicName} - {musicAuthor}**", description = "[**GitHub**](https://github.com/Darkempire78/DeezerDownloader-Discord-Bot)", color = 0x2f9622)
                    embed.set_thumbnail(url = f"{musicCover}")
                    embed.add_field(name = "**MUSIC INFORMATIONS :**", value = f"**Artist :** {musicAuthor}\n**Album :** {musicAlbum} ({albumDate[:4]})\n**Lyrics :** {musicLyricsExist}\n**Quality :** {musicQuality} Kbps", inline=False)
                    embed.set_footer(text = "Bot Created by Darkempire#8245")

                    # Send embed with / without lyrics
                    if musicLyricsExist == False:
                        file = discord.File(f'downloads\{musicName} {musicAuthor} ({musicQuality}).mp3')
                        await ctx.channel.send(file=file, embed=embed) # Send embed
                        await embedDownloading.delete() # Remove downloading message
                    else: #embedDownloading.edit
                        file = [
                            discord.File(f'downloads\{musicName} {musicAuthor} ({musicQuality}).mp3'),
                            discord.File(f'downloads\{musicName}.lrc')
                        ]
                        await ctx.channel.send(files=file, embed=embed) # Send embed
                        await embedDownloading.delete() # Remove downloading message

                    # Delete track and lyrics (if they exist) after posting
                    os.remove(f"downloads\{musicName} {musicAuthor} ({musicQuality}).mp3")
                    try:
                        os.remove(f"downloads\{musicName}.lrc")
                    except:
                        pass
                    
            except (asyncio.TimeoutError):
                embed = discord.Embed(title = f"**TIME IS OUT**", description = "You exceeded the response time (15s)", color = 0xff0000)
                embed.set_footer(text = "Bot Created by Darkempire#8245")
                await ctx.channel.send(embed = embed)
                ctx.command.reset_cooldown(ctx) # Reset the cooldown

# ------------------------ BOT ------------------------ #  

def setup(bot):
    bot.add_cog(DownloadCog(bot))
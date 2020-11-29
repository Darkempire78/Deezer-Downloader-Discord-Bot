import discord
import configuration
import requests # For get rest api
import json
import os
import datetime
import asyncio

from datetime import datetime
from discord.ext import commands
from zipfile import ZipFile
from os.path import basename

from deezloader2 import Login2

# ------------------------ COGS ------------------------ #  

class DownloadAlbumCog(commands.Cog, name="DownloadAlbumCog"):
    def __init__(self, bot):
        self.bot = bot

# ------------------------------------------------------- #

    @commands.command(name = 'downloadalbum', aliases = ['da'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def downloadalbum (self, ctx, *args):

        args = str(args); args = args.replace(',',''); args = args.replace("'",""); args = args.replace("(",""); args = args.replace(")","")
        album = args

        requestSearch = requests.get(f'https://api.deezer.com/search/album?q={album}&index=0&limit=10&output=json') # Limit : 10
        data = requestSearch.json()

        if data['data'] == []:
            embed = discord.Embed(title = f"**NO ALBUM FOUND**", description = f"No album found with your research : ``\"{album}\"``", color = 0xff0000)
            embed.set_footer(text = "Bot Created by Darkempire#8245")
            await ctx.channel.send(embed = embed)
            ctx.command.reset_cooldown(ctx) # Reset the cooldown
        else:
            numberOfAlbumInList = 0
            albumList = ""
            for x in data['data']:
                numberOfAlbumInList +=1
                albumList = f"{albumList}**{numberOfAlbumInList})** {x['title']} - {x['artist']['name']}\n"
            
            # Send music List
            embed = discord.Embed(title = f"**LIST OF FOUND ALBUMS**", description = "[**GitHub**](https://github.com/Darkempire78/DeezerDownloader-Discord-Bot)", color = 0xea8700)
            embed.add_field(name = "**CHOOSE THE NUMBER THAT CORRESPONDS TO THE ALBUM :**", value = f"{albumList}\n**0) To exit (pass the cooldown)**", inline=False)
            embed.set_footer(text = "Bot Created by Darkempire#8245")
            await ctx.channel.send(embed = embed)

            def check(message):
                try:
                    message.content = int(message.content)
                    if ((message.content >= 0) and (message.content <= numberOfAlbumInList)):
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

                    msg.content = int(msg.content)
                    msg.content = msg.content - 1

                    # Find album data
                    albumId = data['data'][msg.content]['id']
                    requestTrack = requests.get(f'https://api.deezer.com/album/{albumId}') 
                    albumData = requestTrack.json()
                    
                    musicListId = []
                    for x in albumData["tracks"]["data"]:
                        musicListId.append(x["id"])

                    for musicIdFromList in musicListId:
                        # Loading message send 
                        embed = discord.Embed(title = f"", description = "Downloading album music in progress...", color = 0xea8700)
                        embed.set_footer(text = "Bot Created by Darkempire#8245")
                        embedDownloading = await ctx.channel.send(embed = embed)

                        requestTrack = requests.get(f'https://api.deezer.com/track/{musicIdFromList}') 
                        musicData = requestTrack.json()

                        # Find data
                        musicId = musicData['id']
                        musicUrl = musicData['link']
                        longMusicName = musicData['title']
                        musicName = musicData['title_short']
                        musicAuthor = musicData['artist']['name']
                        musicDuration = musicData['duration']
                        musicCover = musicData['album']['cover_big']
                        musicAlbum = musicData['album']['title']
                        
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
                        
                        # Download music file and lyrics
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
                        musicSize = os.path.getsize(f'downloads\{longMusicName} {musicAuthor} ({musicQuality}).mp3')
                        if musicSize > 8000000:
                            # Remove last files
                            os.remove(f"downloads\{longMusicName} {musicAuthor} ({musicQuality}).mp3")
                            try:
                                os.remove(f"downloads\{longMusicName}.lrc")
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
                                # Download
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
                                    os.remove(f"downloads\{longMusicName} {musicAuthor} ({musicQuality}).mp3")
                                    try:
                                        os.remove(f"downloads\{longMusicName}.lrc")
                                    except:
                                        pass
                                    return # Stop the function

                        # Remove bad caracters
                        longMusicName = (
                            longMusicName
                            .replace("\\", "")
                            .replace("/", "")
                            .replace(":", "")
                            .replace("*", "")
                            .replace("?", "")
                            .replace("\"", "")
                            .replace("<", "")
                            .replace(">", "")
                            .replace("|", "")
                            .replace("&", "")
                        )

                        # Send track
                        file = discord.File(f'downloads\{longMusicName} {musicAuthor} ({musicQuality}).mp3')
                        await ctx.channel.send(file=file) # Send embed
                        await embedDownloading.delete() # Remove downloading message
                      
                        # Delete track
                        os.remove(f"downloads\{longMusicName} {musicAuthor} ({musicQuality}).mp3")
                    
                    # After album sending
                    # Create zip file
                    with ZipFile(f'downloads\{musicAlbum} LYRICS.zip', 'w') as zipfile:
                        try:
                            for musicIdFromList in musicListId:
                                requestTrack = requests.get(f'https://api.deezer.com/track/{musicIdFromList}') 
                                musicData = requestTrack.json()
                                musicName = musicData['title_short']
                                # Write
                                filePath = f"downloads\{longMusicName}.lrc"
                                zipfile.write(filePath, basename(filePath))
                                # Remove
                                os.remove(f"downloads\{longMusicName}.lrc")
                        except:
                            pass

                    # Send lrc
                    file = discord.File(f'downloads\{musicAlbum} LYRICS.zip')
                    await ctx.channel.send(file=file) # Send embed
                    os.remove(f'downloads\{musicAlbum} LYRICS.zip')

                    # Send embed 
                    requestAlbum = requests.get(f'https://api.deezer.com/album/{albumId}') 
                    dataAlbum = requestAlbum.json()

                    albumTitle = dataAlbum['title']
                    albumCover = dataAlbum['cover_big']                    
                    albumAuthor = dataAlbum['artist']['name']
                    albumLabel = dataAlbum['label']
                    albumTracksNumber = dataAlbum['nb_tracks']
                    albumReleaseDate = dataAlbum['release_date']
                    albumFans = dataAlbum['fans']
                    # Find genres
                    albumGenres = ""
                    for x in dataAlbum['genres']['data']:
                        albumGenres = f"{albumGenres}{x['name']} - "
                    albumGenres = albumGenres[:-2]

                    # Find tracks list
                    albumTracks = ""
                    trackNumber =  0
                    for x in dataAlbum['tracks']['data']:
                        trackNumber +=1
                        albumTracks = f"{albumTracks}{trackNumber}. **{x['title']}**\n"
                    

                    # Send album informations
                    embed = discord.Embed(title = f"**{albumTitle} - {albumAuthor}**", description = "[**GitHub**](https://github.com/Darkempire78/DeezerDownloader-Discord-Bot)", color = 0x2f9622)
                    embed.set_thumbnail(url = f"{albumCover}")
                    embed.add_field(name = "**ALBUM INFORMATIONS :**", value = f"**Genres :** {albumGenres}\n**Release Date :** {albumReleaseDate}\n**Number of tracks :** {albumTracksNumber}\n**Fans :** {albumFans}\n**Label :** {albumLabel}", inline=False)
                    embed.add_field(name = "**MUSIC LIST :**", value = f"{albumTracks}", inline=False)
                    embed.set_footer(text = "Bot Created by Darkempire#8245")
                    await ctx.channel.send(embed = embed)


            except (asyncio.TimeoutError):
                embed = discord.Embed(title = f"**TIME IS OUT**", description = "You exceeded the response time (15s)", color = 0xff0000)
                embed.set_footer(text = "Bot Created by Darkempire#8245")
                await ctx.channel.send(embed = embed)
                ctx.command.reset_cooldown(ctx) # Reset the cooldown

# ------------------------ BOT ------------------------ #  

def setup(bot):
    bot.add_cog(DownloadAlbumCog(bot))
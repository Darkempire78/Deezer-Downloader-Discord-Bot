import discord
import random 
import asyncio
import time
import requests # For get rest api
import json
import os

from datetime import datetime
from discord.ext import commands

# ------------------------ COGS ------------------------ #  

class AlbumCog(commands.Cog, name="AlbumCog"):
    def __init__(self, bot):
        self.bot = bot

# ------------------------------------------------------- #

    @commands.command(name = 'album')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def album (self, ctx, *args):

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
            
            # Send album List
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
    bot.add_cog(AlbumCog(bot))
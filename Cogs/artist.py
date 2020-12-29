import discord
import random 
import asyncio
import time
import configuration
import requests # For get rest api
import json
import os
import platform
import datetime

from datetime import datetime
from discord.ext import commands

# ------------------------ COGS ------------------------ #  

class ArtistCog(commands.Cog, name="ArtistCog"):
    def __init__(self, bot):
        self.bot = bot

# ------------------------------------------------------- #

    @commands.command(name = 'artist')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def artist (self, ctx, *args):

        artist = " ".join(args)

        requestSearch = requests.get(f'https://api.deezer.com/search/artist?q={artist}&index=0&limit=3&output=json') # Limit : 1
        data = requestSearch.json()

        if data['data'] == []:
            embed = discord.Embed(title = f"**NO ARTIST FOUND**", description = f"No artist found with your research : ``\"{artist}\"``", color = 0xff0000)
            embed.set_footer(text = "Bot Created by Darkempire#8245")
            await ctx.channel.send(embed = embed)
            ctx.command.reset_cooldown(ctx) # Reset the cooldown
        else:
            numberOfArtistInList = 0
            artistList = ""
            for x in data['data']:
                numberOfArtistInList +=1
                artistList = f"{artistList}**{numberOfArtistInList})** {x['name']}\n"
            
            # Send album List
            embed = discord.Embed(title = f"**LIST OF FOUND ARTISTS**", description = "[**GitHub**](https://github.com/Darkempire78/DeezerDownloader-Discord-Bot)", color = 0xea8700)
            embed.add_field(name = "**CHOOSE THE NUMBER THAT CORRESPONDS TO THE ARTIST :**", value = f"{artistList}\n**0) To exit (pass the cooldown)**", inline=False)
            embed.set_footer(text = "Bot Created by Darkempire#8245")
            await ctx.channel.send(embed = embed)

            def check(message):
                try:
                    message.content = int(message.content)
                    if ((message.content >= 0) and (message.content <= numberOfArtistInList)):
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
                    # Find data
                    artistId = data['data'][msg.content]['id']
                    artistUrl = data['data'][msg.content]['link']
                    artistName = data['data'][msg.content]['name']
                    artistImage = data['data'][msg.content]['picture_xl']

                    # Find 3 most famous tracks at the moment
                    requestTopTracks = requests.get(f'https://api.deezer.com/artist/{artistId}/top?limit=3') # Limit : 3
                    dataTopTracks = requestTopTracks.json()
                    
                    try:
                        musicName1 = dataTopTracks['data'][0]['title']
                        musicLink1 = dataTopTracks['data'][0]['link']
                    except:
                        musicName1 = ""; musicLink1 = ""
                    try:
                        musicName2 = dataTopTracks['data'][1]['title']
                        musicLink2 = dataTopTracks['data'][1]['link']
                    except:
                        musicName2 = ""; musicLink2 = ""
                    try:
                        musicName3 = dataTopTracks['data'][2]['title']
                        musicLink3 = dataTopTracks['data'][2]['link']
                    except:
                        musicName3 = ""; musicLink3 = ""

                    # Find artist
                    artistRequest = requests.get(f'https://api.deezer.com/artist/{artistId}') 
                    dataArtist = artistRequest.json()
                    # Find albums 
                    requestArtistAlbums = requests.get(f'https://api.deezer.com/artist/{artistId}/albums') 
                    dataAlbums = requestArtistAlbums.json()

                    # Find fans and albums data
                    artistFans = dataArtist['nb_fan']
                    artistAlbums = dataArtist['nb_album']

                    # Find album names and links
                    albums = ""
                    othersAlbums = 0
                    for x in dataAlbums['data']:
                        albumName = x['title']  
                        albumLink = x['link'] 
                        if (len(albums) > 900):
                            othersAlbums += 1
                        else: 
                            albums = albums + f"[{albumName}]({albumLink}) - "
                    albums = albums[:-2]
                    if othersAlbums > 0:
                        albums = albums + f"and {othersAlbums} others..."

                    # Set up embed 
                    embed = discord.Embed(title = f"**{artistName}**", description = "[**GitHub**](https://github.com/Darkempire78/DeezerDownloader-Discord-Bot)", color = 0x2f9622)
                    embed.set_thumbnail(url = f"{artistImage}")
                    embed.add_field(name = "**ARTIST INFORMATIONS :**", value = f"**Artist :** [{artistName}]({artistUrl})\n**Fans :** {artistFans}\n**Number of albums :** {artistAlbums}", inline=False)
                    embed.add_field(name = "**ACTUALLY MOST FAMOUS TRACKS :**", value = f"**1)** [{musicName1}]({musicLink1})\n**2)** [{musicName2}]({musicLink2})\n**3)** [{musicName3}]({musicLink3})", inline=False)
                    embed.add_field(name = "**ALBUMS :**", value = f"{albums}", inline=False)
                    embed.set_footer(text = "Bot Created by Darkempire#8245")
                    await ctx.channel.send(embed = embed)
            
            except (asyncio.TimeoutError):
                embed = discord.Embed(title = f"**TIME IS OUT**", description = "You exceeded the response time (15s)", color = 0xff0000)
                embed.set_footer(text = "Bot Created by Darkempire#8245")
                await ctx.channel.send(embed = embed)
                ctx.command.reset_cooldown(ctx) # Reset the cooldown

# ------------------------ BOT ------------------------ #  

def setup(bot):
    bot.add_cog(ArtistCog(bot))
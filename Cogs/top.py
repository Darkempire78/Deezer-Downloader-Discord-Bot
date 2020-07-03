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

class TopCog(commands.Cog, name="TopCog"):
    def __init__(self, bot):
        self.bot = bot

# ------------------------------------------------------- #

    @commands.command(name = 'top')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def top (self, ctx):

        # Send Top List
        topList = "**1)** Top Worldwide\n**2)** Top USA\n**3)** Top France\n**4)** Top UK\n**5)** Top Brazil\n**6)** Top Germania\n**7)** Top Belgium\n**8)** Top Spain\n**9)** Top Italia\n**10)** Top Canada\n"

        embed = discord.Embed(title = f"**LIST OF COUNTRY TOPS**", description = "[**GitHub**](https://github.com/Darkempire78/DeezerDownloader-Discord-Bot)", color = 0xea8700)
        embed.add_field(name = "**CHOOSE THE NUMBER THAT CORRESPONDS TO THE TOP :**", value = f"{topList}\n**0) To exit (pass the cooldown)**", inline=False)
        embed.set_footer(text = "Bot Created by Darkempire#8245")
        await ctx.channel.send(embed = embed)

        def check(message):
            try:
                message.content = int(message.content)
                if ((message.content >= 0) and (message.content <= 10)):
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
                # Find the good top 
                if msg.content == 1:
                    top = 3155776842 # 1) Top Worldwide
                elif msg.content == 2:
                    top = 1313621735 # 2) Top USA
                elif msg.content == 3:
                    top = 1109890291 # 3) Top France
                elif msg.content == 4:
                    top = 1111142221 # 4) Top UK
                elif msg.content == 5:
                    top = 1111141961 # 5) Top Brazil
                elif msg.content == 6:
                    top = 1111143121 # 6) Top Germania
                elif msg.content == 7:
                    top = 1266968331 # 7) Top Belgium
                elif msg.content == 8:
                    top = 1116190041 # 8) Top Spain 
                elif msg.content == 9:
                    top = 1116187241 # 9) Top Italia
                elif msg.content == 10:
                    top = 1652248171 # 10) Top Canada


                # Find Top
                requestTopTracks = requests.get(f'https://api.deezer.com//playlist/{top}')
                dataTop = requestTopTracks.json()

                topTitle = dataTop['title']
                topFans = dataTop['fans']
                topImage = dataTop['picture_big']
                
                musicTop = ""
                numberOfMusicInList = 0
                for x in dataTop['tracks']['data']:
                    if numberOfMusicInList < 20:
                        numberOfMusicInList +=1
                        musicTop = f"{musicTop}**{numberOfMusicInList})** {x['title']} - {x['artist']['name']}\n"
                    else:
                        break
                
                # Set up embed 
                embed = discord.Embed(title = f"**{topTitle}**", description = "[**GitHub**](https://github.com/Darkempire78/DeezerDownloader-Discord-Bot)", color = 0x2f9622)
                embed.set_thumbnail(url = f"{topImage}")
                embed.add_field(name = "**TOP INFORMATIONS :**", value = f"**Description :** This top is updated every day\n**Fans :** {topFans}", inline=False)
                embed.add_field(name = "**MUSIC TOP :**", value = f"{musicTop}", inline=False)
                embed.set_footer(text = "Bot Created by Darkempire#8245")
                topMessage = await ctx.channel.send(embed = embed)

                # Add reaction
                await topMessage.add_reaction("⬅️")
                await topMessage.add_reaction("➡️") 

                async def editTopMessage(page):
                    if page < 0:
                        page = 4
                    elif page > 4:
                        page = 0

                    requestTopTracks = requests.get(f'https://api.deezer.com//playlist/{top}?index={page*20}&limit=20')
                    dataTop = requestTopTracks.json()

                    musicTop = ""
                    numberOfMusicInList = page*20
                    for x in dataTop['tracks']['data']:
                        numberOfMusicInList +=1
                        musicTop = f"{musicTop}**{numberOfMusicInList})** {x['title']} - {x['artist']['name']}\n"

                    new_embed = discord.Embed(title = f"**{topTitle}**", description = "[**GitHub**](https://github.com/Darkempire78/DeezerDownloader-Discord-Bot)", color = 0x2f9622)
                    new_embed.set_thumbnail(url = f"{topImage}")
                    new_embed.add_field(name = "**TOP INFORMATIONS :**", value = f"**Description :** This top is updated every day\n**Fans :** {topFans}", inline=False)
                    new_embed.add_field(name = "**MUSIC TOP :**", value = f"{musicTop}", inline=False)
                    new_embed.set_footer(text = "Bot Created by Darkempire#8245")
                    await topMessage.edit(embed = new_embed)

                    # Call the function waitReaction
                    await waitReaction(ctx, page, topMessage)

                async def waitReaction(ctx, page, topMessage):
                    
                    def check2(reaction, user):
                        if user == ctx.author:
                            if str(reaction.emoji) == '➡️':
                                return reaction.emoji, user
                            elif str(reaction.emoji) == '⬅️':
                                return reaction.emoji, user

                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=45.0, check=check2)
                        if str(reaction.emoji) == '➡️':
                            pass
                            await topMessage.remove_reaction('➡️', user)
                            page += 1
                            await editTopMessage(page)
                        elif str(reaction.emoji) == '⬅️':
                            await topMessage.remove_reaction('⬅️', user)
                            page -= 1
                            await editTopMessage(page)
                    except asyncio.TimeoutError:
                        await topMessage.clear_reactions()

                # call the waitReaction
                page = 0
                await waitReaction(ctx, page, topMessage)
        
        except (asyncio.TimeoutError):
            embed = discord.Embed(title = f"**TIME IS OUT**", description = "You exceeded the response time (15s)", color = 0xff0000)
            embed.set_footer(text = "Bot Created by Darkempire#8245")
            await ctx.channel.send(embed = embed)
            ctx.command.reset_cooldown(ctx) # Reset the cooldown

# ------------------------ BOT ------------------------ #  

def setup(bot):
    bot.add_cog(TopCog(bot))
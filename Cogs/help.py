import discord

from discord.ext import commands

# ------------------------ COGS ------------------------ #  

class HelpCog(commands.Cog, name="help commandes"):
    def __init__(self, bot):
        self.bot = bot

# ------------------------------------------------------ #  

    @commands.command(name = 'help')
    async def help (self, ctx):
        embed = discord.Embed(title=f"__**Help page of {self.bot.user.name}**__", description="[**GitHub**](https://github.com/Darkempire78/DeezerDownloader-Discord-Bot)", color=0xdeaa0c)
        embed.set_thumbnail(url=f'{self.bot.user.avatar_url}')
        embed.add_field(name="__COMMANDS :__", value=f"**{self.bot.command_prefix}download <MusicName> :** Search the music on Deezer and download it.\n**{self.bot.command_prefix}track <MusicName> :** Find informations about a track and send preview.\n**{self.bot.command_prefix}artist <ArtistName> :** Find informations about an artist.\n**{self.bot.command_prefix}album <AlbumName> :** Find informations about an album.", inline=False)
        embed.set_footer(text="Bot Created by Darkempire#8245")
        await ctx.channel.send(embed=embed)
            

# ------------------------ BOT ------------------------ #  

def setup(bot):
    bot.remove_command("help")
    bot.add_cog(HelpCog(bot))
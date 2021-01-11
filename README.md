![](https://img.shields.io/github/languages/code-size/Darkempire78/DeezerDownloader-Discord-Bot?style=for-the-badge) 
![](https://img.shields.io/badge/SOURCERY-ENABLED-green?style=for-the-badge)

# Deezer Downloader Discord Bot

Deezer Downloader is a Discord Bot that allows you to download music from Discord. This bot downloads all its music from Deezer.

Download track            |  Infos about artist
:-------------------------:|:-------------------------:
![](https://github.com/Darkempire78/DeezerDownloader-Discord-Bot/blob/master/Capture1.PNG)  |  ![](https://github.com/Darkempire78/DeezerDownloader-Discord-Bot/blob/master/Capture2.PNG)


## Installation

Install all dependencies:

```bash
pip install -r requirements.txt
```
Then put your ARL Token from Deezer (See below) and your Discord token that can be found in
the Discord's developers portal inside `configuration.py`.

Finally, host the bot and invite it to your own server.

### Get your Deezer Arl

- login to https://www.deezer.com/
- go on cookie manager and search for "arl" (F12 -> Application -> Cookies -> "https://www.deezer.com/" -> arl)
- copy the value and paste in configuration.py

## Features

* Download MP3 and album from Deezer
* Select the best quality (320kbps) if the file doesn't reach Discord's file size limit (8mb).
* Download lyrics if available.
* Get infos about artists, albums...

## Commands

```
?download <MusicName> : Search the music on Deezer and download it.
?downloadalbum <AlbumName> : Search the album on Deezer and download it.
?track <MusicName> : Find informations about a track and send preview.
?artist <ArtistName> : Find informations about an artist.
?album <AlbumName> : Find informations about an album.
?top : Send worldwide top and top by countries.

?help : display help.
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Why this bot is not hosted ?

This bot allows you to download copyrighted work. That is why the developer decided to not host this bot.

## License

This project is under [GPLv3](https://github.com/Darkempire78/DeezerDownloader-Discord-Bot/blob/master/LICENSE).

## Disclaimer

**This project is for educational use only. Sharing copyrighted content can be against Discord TOS and your country laws. Use this tool at your own risk ! 
The developers are not responsible for the damages that can be caused by this program.**

# Advice :

You should use [Discord Tools](https://marketplace.visualstudio.com/items?itemName=Darkempire78.discord-tools) to code your Discord bots on Visual Studio Code easier.
Works for Python (Discord.py), Javascript (Discord.js) and Java (JDA). Generate template bot and code (snippets).
- **Download :** https://marketplace.visualstudio.com/items?itemName=Darkempire78.discord-tools
- **Repository :** https://github.com/Darkempire78/Discord-Tools

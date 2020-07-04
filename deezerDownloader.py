#!/usr/bin/env python3

import configuration

# standard libraries:
import argparse
import configparser
import hashlib
import os
import re
import platform

# third party libraries:
import discord
import mutagen
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, USLT, APIC
from mutagen.mp3 import MP3
from requests.packages.urllib3.util.retry import Retry
from pathvalidate import sanitize_filepath

async def deezerDownloaderCommand(ctx2, link2, musicName2, trackQuality2):
    global ctx 
    ctx = ctx2
    global link
    link = link2
    global musicName
    musicName = musicName2
    global trackQuality
    trackQuality = trackQuality2

    session = requests.Session()
    userAgent = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/68.0.3440.106 Safari/537.36'
        )
    httpHeaders = {
            'User-Agent'      : userAgent,
            'Content-Language': 'en-US',
            'Cache-Control'   : 'max-age=0',
            'Accept'          : '*/*',
            'Accept-Charset'  : 'utf-8,ISO-8859-1;q=0.7,*;q=0.3',
            'Accept-Language' : 'en-US;q=0.6,en;q=0.4',
            'Connection'      : 'keep-alive',
            }
    session.headers.update(httpHeaders)

    def apiCall(method, json_req=False):
        ''' Requests info from the hidden api: gw-light.php.
        '''
        unofficialApiQueries = {
            'api_version': '1.0',
            'api_token'  : 'null' if method == 'deezer.getUserData' else CSRFToken,
            'input'      : '3',
            'method'     : method
            }
        req = requests_retry_session().post(
            url='https://www.deezer.com/ajax/gw-light.php',
            params=unofficialApiQueries,
            json=json_req
            ).json()
        return req['results']


    def loginUserToken(token):
        ''' Handles userToken for settings file, for initial setup.
            If no USER_ID is found, False is returned and thus the
            cookie arl is wrong. Instructions for obtaining your arl
            string are in the README.md
        '''
        cookies = {'arl': token}
        session.cookies.update(cookies)
        req = apiCall('deezer.getUserData')
        if not req['USER']['USER_ID']:
            return False
        else:
            return True


    def getTokens():
        req = apiCall('deezer.getUserData')
        global CSRFToken
        CSRFToken = req['checkForm']
        global sidToken
        sidToken = req['SESSION_ID']

    # https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    def requests_retry_session(retries=3, backoff_factor=0.3,
                            status_forcelist=(500, 502, 504)):
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            method_whitelist=frozenset(['GET', 'POST'])
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session


    def getJSON(mediaType, mediaId, subtype=""):
        ''' Official API. This function is used to download the ID3 tags.
            Subtype can be 'albums' or 'tracks'.
        '''
        url = f'https://api.deezer.com/{mediaType}/{mediaId}/{subtype}?limit=-1'
        return requests_retry_session().get(url).json()


    def getCoverArt(coverArtId, size, ext):
        ''' Retrieves the coverart/playlist image from the official API, and
            returns it.
        '''
        url = f'https://e-cdns-images.dzcdn.net/images/cover/{coverArtId}/{size}x{size}.{ext}'
        r = requests_retry_session().get(url)
        return r.content

    def getLyrics(trackId):
        ''' Recieves (timestamped) lyrics from the unofficial api
            and returns them
        '''
        req = apiCall('song.getLyrics', {'sng_id': trackId})
        lyrics = {}
        if 'LYRICS_SYNC_JSON' in req: # synced lyrics
            rawLyrics = req['LYRICS_SYNC_JSON']
            syncedLyrics = ''
            for lyricLine in rawLyrics:
                try:
                    time = lyricLine['lrc_timestamp']
                except KeyError:
                    lyricLine = ''
                else:
                    line = lyricLine['line']
                    lyricLine = f'{time}{" "}{line}'
                finally:
                    syncedLyrics += lyricLine + '\n' # TODO add duration?
            lyrics['sylt'] = syncedLyrics
        if 'LYRICS_TEXT' in req: # unsynced lyrics
            lyrics['uslt'] = req['LYRICS_TEXT'].replace('\r', '')
        return lyrics


    def saveLyrics(lyrics, filename):
        ''' Writes synced or unsynced lyrics to file
        '''
        if not (lyrics and filename):
            return False

        lyricsType = 'uslt'
        if 'sylt' in lyrics:
            ext = 'lrc'
            lyricsType = 'sylt'
        elif 'uslt' in lyrics:
            ext = 'txt'
        else:
            raise ValueError('Unknown lyrics type')

        with open(f'{filename}.{ext}', 'a') as f:
            for line in lyrics[lyricsType]:
                f.write(line)
        return True


    def getTags(trackInfo, albInfo, playlist):
        ''' Combines tag info in one dict. '''
        # retrieve tags
        try:
            genre = albInfo['genres']['data'][0]['name']
        except:
            genre = ''
        tags = {
            'title'       : trackInfo['title'],
            'discnumber'  : trackInfo['disk_number'],
            'tracknumber' : trackInfo['track_position'],
            'album'       : trackInfo['album']['title'],
            'date'        : trackInfo['album']['release_date'],
            'artist'      : getAllContributors(trackInfo),
            'bpm'         : trackInfo['bpm'],
            'albumartist' : albInfo['artist']['name'],
            'totaltracks' : albInfo['nb_tracks'],
            'label'       : albInfo['label'],
            'genre'       : genre
            }
        return tags


    def getAllContributors(trackInfo):
        artists = []
        for artist in trackInfo['contributors']:
            artists.append(artist['name'])
        return artists

    def writeMP3Tags(filename, tags, coverArtId):
        handle = MP3(filename, ID3=EasyID3)
        handle.delete()
        # label is not supported by easyID3, so we add it
        EasyID3.RegisterTextKey("label", "TPUB")
        # tracknumber and total tracks is one tag for ID3
        tags['tracknumber'] = f'{str(tags["tracknumber"])}/{str(tags["totaltracks"])}'
        del tags['totaltracks']
        for key, val in tags.items():
            if key == 'artist':
                # Concatenate artists
                artists = val[0] # Main artist
                for artist in val[1:]:
                    artists += ";" + artist
                handle[key] = artists
            elif key == 'lyrics':
                if 'uslt' in val: # unsynced lyrics
                    handle.save()
                    id3Handle = ID3(filename)
                    id3Handle['USLT'] = USLT(encoding=3, text=val['uslt'])
                    id3Handle.save(filename)
                    handle.load(filename) # Reload tags
            else:
                handle[key] = str(val)
        handle.save()
        return True

    def getTrackDownloadUrl(MD5, MEDIA_VERSION, SNGID, quality):
        ''' Calculates the deezer download URL from
            a given MD5_ORIGIN (MD5 hash), SNG_ID and MEDIA_VERSION.
        '''
        # this specific unicode char is needed
        char = b'\xa4'.decode('unicode_escape')
        step1 = char.join((MD5,
                        quality, SNGID,
                        MEDIA_VERSION))
        m = hashlib.md5()
        m.update(bytes([ord(x) for x in step1]))
        step2 = f'{m.hexdigest()}{char}{step1}{char}'
        step2 = step2.ljust(80, ' ')
        cipher = Cipher(algorithms.AES(bytes('jo6aey6haid2Teih', 'ascii')),
                        modes.ECB(), default_backend())
        encryptor = cipher.encryptor()
        step3 = encryptor.update(bytes([ord(x) for x in step2])).hex()
        cdn = MD5[0]
        decryptedUrl = f'https://e-cdns-proxy-{cdn}.dzcdn.net/mobile/1/{step3}'
        return decryptedUrl


    def resumeDownload(url, filesize):
        resume_header = {'Range': 'bytes=%d-' % filesize}
        req = requests_retry_session().get(url,
                                        headers=resume_header,
                                        stream=True)
        return req


    def getBlowfishKey(trackId):
        ''' Calculates the Blowfish decrypt key for a given SNG_ID.'''
        secret = 'g4el58wc0zvf9na1'
        m = hashlib.md5()
        m.update(bytes([ord(x) for x in trackId]))
        idMd5 = m.hexdigest()
        bfKey = bytes(([(ord(idMd5[i]) ^ ord(idMd5[i+16]) ^ ord(secret[i]))
                    for i in range(16)]))
        return bfKey


    def printPercentage(text, sizeOnDisk, totalFileSize):
        percentage = round((sizeOnDisk / totalFileSize)*100)
        print("\r{} [{:d}%]".format(text, percentage), end='')


    def decryptChunk(chunk, bfKey):
        ''' Decrypt a given encrypted chunk with a blowfish key. '''
        cipher = Cipher(algorithms.Blowfish(bfKey),
                        modes.CBC(bytes([i for i in range(8)])),
                        default_backend())
        decryptor = cipher.decryptor()
        decChunk = decryptor.update(chunk) + decryptor.finalize()
        return decChunk


    def downloadTrack(filename, ext, url, bfKey):
        ''' Download and decrypts a track. Resumes download for tmp files.'''
        tmpFile = f'{filename}.tmp'
        realFile = f'{filename}{ext}'
        if os.path.isfile(tmpFile):
            text = f"Resuming download: {realFile}"
            sizeOnDisk = os.stat(tmpFile).st_size  # size downloaded file
            # reduce sizeOnDisk to a multiple of 2048 for seamless decryption
            sizeOnDisk = sizeOnDisk - (sizeOnDisk % 2048)
            i = sizeOnDisk/2048
            req = resumeDownload(url, sizeOnDisk)
        else:
            text = f"Downloading: {realFile}"
            sizeOnDisk = 0
            i = 0
            req = requests_retry_session().get(url, stream=True)
            if req.headers['Content-length'] == '0':
                print("Empty file, skipping...\n", end='')
                return False
            # make dirs if they do not exist yet
            fileDir = os.path.dirname(realFile)
            if not os.path.isdir(fileDir):
                os.makedirs(fileDir)

        totalChunks = i + int(req.headers['Content-Length'])/2048 # we need to i + .. because resumeDownload Content-Length return content length not downloaded, not full filesize
        # Decrypt content and write to file
        with open(tmpFile, 'ab') as fd:
            fd.seek(sizeOnDisk)  # jump to end of the file in order to append to it
            # Only every third 2048 byte block is encrypted.
            for chunk in req.iter_content(2048):
                if i % 3 == 0 and len(chunk) >= 2048:
                    chunk = decryptChunk(chunk, bfKey)
                printPercentage(text, i, totalChunks)
                fd.write(chunk)
                i += 1
        os.rename(tmpFile, realFile)
        return True

    def getTrack(trackId, playlist=False):
        ''' Calls the necessary functions to download and tag the tracks.
            Playlist must be a tuple of (playlistInfo, playlistTrack).
        '''
        trackInfo = getJSON('track', trackId)
        albInfo = getJSON('album', trackInfo['album']['id'])
        privateTrackInfo = apiCall('deezer.pageTrack', {'SNG_ID': trackId})['DATA']

        trackQuality2 = trackQuality
        if trackQuality2 == "320":
            trackQuality2 = "3"
        else:
            trackQuality2 = "1"
        quality = trackQuality2
        if not quality:
            print((f"Song {trackInfo['title']} not available, skipping..."
                "\nMaybe try with a higher quality setting?"))
            return False
        ext = ".mp3"
        fullFilenamePath = f'downloads\\{musicName}'

        decryptedUrl = getTrackDownloadUrl(privateTrackInfo['MD5_ORIGIN'], privateTrackInfo['MEDIA_VERSION'], privateTrackInfo['SNG_ID'], quality)
        bfKey = getBlowfishKey(privateTrackInfo['SNG_ID'])
        if downloadTrack(fullFilenamePath, ext, decryptedUrl, bfKey): # Track downloaded successfully
            tags = getTags(trackInfo, albInfo, playlist)
            coverArtId = None

            # Get track lyrics
            if 'lyrics' in tags:
                saveLyrics(tags['lyrics'], fullFilenamePath)
            else:
                lyrics = getLyrics(trackId)
                saveLyrics(lyrics, fullFilenamePath)

            writeMP3Tags(f'{fullFilenamePath}{ext}', tags, coverArtId)

        else:
            return False
        return True

    def downloadDeezer(url):
        ''' Calls the correct download functions for downloading a track, playlist,
            album or artist.
        '''
        regexStr = r'(?:(?:https?:\/\/)?(?:www\.))?deezer\.com\/(?:.*?\/)?(playlist|artist|album|track|)\/([0-9]*)(?:\/?)(tracks|albums|related_playlist|top_track)?'
        if re.fullmatch(regexStr, url) is None:
            print(f'"{url}": not a valid link')
            return False
        p = re.compile(regexStr)
        m = p.match(url)
        mediaType = m.group(1)
        mediaId = m.group(2)
        mediaSubType = m.group(3)
        getTrack(mediaId)

    async def checkSettingsFile():
        if os.path.isfile('configuration.py'):
            return 'configuration.py'
        else:
            embed = discord.Embed(title = f"**ERROR**", description = "No settings file found !", color = 0xff0000)
            embed.set_footer(text = "Bot Created by Darkempire#8245")
            await ctx.channel.send(embed = embed)
            return

    async def init():
        if not loginUserToken(configuration.arl):
            embed = discord.Embed(title = f"**ERROR**", description = "No arl found !", color = 0xff0000)
            embed.set_footer(text = "Bot Created by Darkempire#8245")
            await ctx.channel.send(embed = embed)
            return
        getTokens()

    # START
    await checkSettingsFile()
    await init()
    downloadDeezer(link)
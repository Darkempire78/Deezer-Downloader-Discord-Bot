import deezloader
from tqdm import tqdm
from deezloader.others_settings import answers
from os.path import isfile
from deezloader import(
	utils, methods, exceptions,
	download_utils, deezer_settings
)

class Login2(deezloader.Login):

    def download(
        self, link, details,
        recursive_quality = None,
        recursive_download = None,
        not_interface = None,
        zips = False
    ):

    
        if not details['quality'] in self.qualities:
            raise exceptions.QualityNotFound("The qualities have to be FLAC or MP3_320 or MP3_256 or MP3_128")

        self.token = self.get_api(self.get_user_data)['checkForm']
        ids = utils.get_ids(link)
        datas = details['datas']
        quality = details['quality']
        output = details['output']

        def get_infos(method, json_data):
            infos = self.get_api(method, self.token, json_data)
            return infos

        def check_quality_song(infos, datas):
            ids = infos['SNG_ID']
            num_quality = self.qualities[quality]['n_quality']
            file_format = self.qualities[quality]['f_format']
            song_quality = self.qualities[quality]['s_quality']
            song_md5, version = utils.check_md5_song(infos)
            song_hash = download_utils.genurl(song_md5, num_quality, ids, version)

            try:
                crypted_audio = utils.song_exist(song_md5[0], song_hash)
            except (IndexError, exceptions.TrackNotFound):
                if not recursive_quality:
                    raise exceptions.QualityNotFound("The quality chosen can't be downloaded")

                for a in self.qualities:
                    if details['quality'] == a:
                        continue

                    num_quality = self.qualities[a]['n_quality']
                    file_format = self.qualities[a]['f_format']
                    song_quality = self.qualities[a]['s_quality']
                    song_hash = download_utils.genurl(song_md5, num_quality, ids, infos['MEDIA_VERSION'])

                    try:
                        crypted_audio = utils.song_exist(song_md5[0], song_hash)
                    except exceptions.TrackNotFound:
                        raise exceptions.TrackNotFound("Error with this song %s" % link)

            music = utils.var_excape(datas['music'])
            artist = utils.var_excape(datas['ar_album'])

            directory = (
                "%s"
                % (
                    "%s/" % output
                )
            )

            name = (
                "%s%s %s"
                % (
                    directory,
                    music,
                    artist
                )
            )

            utils.check_dir(directory)
            name += " ({}){}".format(song_quality, file_format)

            if isfile(name):
                if recursive_download:
                    return name

                ans = input("Track %s already exists, do you want to redownload it?(y or n):" % name)

                if not ans in answers:
                    return name

            decrypted_audio = open(name, "wb")

            download_utils.decryptfile(
                crypted_audio.iter_content(2048),
                download_utils.calcbfkey(ids),
                decrypted_audio
            )

            utils.write_tags(
                name, 
                add_more_tags(datas, infos, ids)
            )

            return name

        def add_more_tags(datas, infos, ids):
            json_data = {
                "sng_id": ids
            }

            try:
                datas['author'] = " & ".join(
                    infos['SNG_CONTRIBUTORS']['author']
                )
            except:
                datas['author'] = ""

            try:
                datas['composer'] = " & ".join(
                    infos['SNG_CONTRIBUTORS']['composer']
                )
            except:
                datas['composer'] = ""

            try:
                datas['lyricist'] = " & ".join(
                    infos['SNG_CONTRIBUTORS']['lyricist']
                )
            except:
                datas['lyricist'] = ""

            try:
                datas['version'] = infos['VERSION']
            except KeyError:
                datas['version'] = ""

            need = get_infos(self.get_lyric, json_data)

            try:
                datas['lyric'] = need['LYRICS_TEXT']
                datas['copyright'] = need['LYRICS_COPYRIGHTS']
                datas['lyricist'] = need['LYRICS_WRITERS']
            except KeyError:
                datas['lyric'] = ""
                datas['copyright'] = ""
                datas['lyricist'] = ""

            return datas

        def tracking2(infos, datas):
            image = utils.choose_img(infos['ALB_PICTURE'])
            datas['image'] = image
            song = "{} - {}".format(datas['music'], datas['artist'])

            if not not_interface:
                print("Downloading: %s" % song)

            try:
                nams = check_quality_song(infos, datas)
            except exceptions.TrackNotFound:
                try:
                    ids = utils.not_found(song, datas['music'])
                except IndexError:
                    raise exceptions.TrackNotFound("Track not found: %s" % song)

                json_data = {
                    "sng_id": ids
                }

                infos = get_infos(self.get_song_data, json_data)
                nams = check_quality_song(infos, datas)

            return nams

        if "track" in link:
            json_data = {
                "sng_id" : ids
            }

            infos = get_infos(self.get_song_data, json_data)
            nams = tracking2(infos, datas)
            return nams

        zip_name = ""

        if "album" in link:
            nams = []
            detas = {}
            quali = ""

            json_data = {
                "alb_id": ids,
                "nb": -1
            }

            infos = get_infos(self.get_album, json_data)['data']

            image = utils.choose_img(
                infos[0]['ALB_PICTURE']
            )

            detas['image'] = image
            detas['album'] = datas['album']
            detas['year'] = datas['year']
            detas['genre'] = datas['genre']
            detas['ar_album'] = datas['ar_album']
            detas['label'] = datas['label']
            detas['upc'] = datas['upc']

            t = tqdm(
                range(
                    len(infos)
                ),
                desc = detas['album'],
                disable = not_interface
            )

            for a in t:
                detas['music'] = datas['music'][a]
                detas['artist'] = datas['artist'][a]
                detas['tracknum'] = datas['tracknum'][a]
                detas['discnum'] = datas['discnum'][a]
                detas['bpm'] = datas['bpm'][a]
                detas['duration'] = datas['duration'][a]
                detas['isrc'] = datas['isrc'][a]
                song = "{} - {}".format(detas['music'], detas['artist'])
                t.set_description_str(song)

                try:
                    nams.append(
                        check_quality_song(infos[a], detas)
                    )
                except exceptions.TrackNotFound:
                    try:
                        ids = utils.not_found(song, detas['music'])

                        json = {
                            "sng_id": ids
                        }

                        nams.append(
                            check_quality_song(
                                get_infos(self.get_song_data, json), 
                                detas
                            )
                        )
                    except (exceptions.TrackNotFound, IndexError):
                        nams.append(song)
                        print("Track not found: %s :(" % song)
                        continue

                quali = (
                    nams[a]
                    .split("(")[-1]
                    .split(")")[0]
                )

            if zips:
                album = utils.var_excape(datas['album'])

                directory = (
                    "%s%s %s/"
                    % (
                        "%s/" % output,
                        album,
                        datas['upc']
                    )
                )

                zip_name = (
                    "%s%s (%s).zip"
                    % (
                        directory,
                        album,
                        quali
                    )
                )

                try:
                    utils.create_zip(zip_name, nams)
                except FileNotFoundError:
                    raise exceptions.QualityNotFound(
                        "Can't download album \"{}\" in {} quality".format(album, details['quality'])
                    )

        elif "playlist" in link:
            json_data = {
                "playlist_id": ids,
                "nb": -1
            }

            infos = get_infos(methods.method_get_playlist_data, json_data)['data']
            nams = []

            for a in range(
                len(infos)
            ):
                try:
                    nams.append(
                        tracking2(infos[a], datas[a])
                    )
                except TypeError:
                    c = infos[a]
                    song = "{} - {}".format(c['SNG_TITLE'], c['ART_NAME'])
                    nams.append("Track not found")

            quali = "ALL"

            if zips:
                zip_name = (
                    "%s %s (%s).zip"
                    % (
                        "%s/playlist" % output,
                        ids,
                        quali
                    )
                )

                utils.create_zip(zip_name, nams)

        return nams, zip_name
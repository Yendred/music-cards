#!/usr/bin/python3
# from __future__ import unicode_literals
import hashlib
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path

import youtube_dl
from mpd import MPDClient

from CardList import CardList
from Reader import Reader

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
MEDIA_PATH = os.path.join(Path.home(), "media")  # ~/media
TRACK_DIR_PATH = os.path.join(MEDIA_PATH, "tracks")  # ~/media/tracks
MUSIC_DIR_PATH = os.path.join(MEDIA_PATH, "music")  # ~/media/music
TMP_PATH = os.path.join(MEDIA_PATH, "tmp")  # ~/media/tmp
CACHE_PATH = os.path.join(MEDIA_PATH, "cache")  # ~/media/cache
MUSIC_DIR_MAX_MEGABYTES = 500
START_VOLUME = 30


class Box:
    def __init__(self):
        for filePath in [
            MEDIA_PATH,
            TRACK_DIR_PATH,
            MUSIC_DIR_PATH,
            TMP_PATH,
            CACHE_PATH,
        ]:
            try:
                if not Path(filePath).exists():
                    print(f"Creating {filePath}")
                    Path(filePath).mkdir(mode=0o755, parents=True)

            except:  # Exception as e:
                print(f"Failed to create {filePath}")
                pass

            finally:
                pass

    def connectMPD(self):
        try:
            client = MPDClient()  # create client object
            client.timeout = (
                200  # network timeout in seconds (floats allowed), default: None
            )
            client.idletimeout = None
            client.connect("localhost", 6600)
            return client
        except:
            print("Could not connect to MPD server")
            # sys.exit(10)
        finally:
            pass

    def GetMusicDirSizeMegabytes(self):
        output = 0
        try:
            rawOutput = subprocess.run(
                ["du", "-m", MUSIC_DIR_PATH], capture_output=True
            )

            output = rawOutput.stdout.decode("ascii").split("\t")[0].strip()
            # print(f"GetMusicDirSizeMegabytes: output: '{output}'")
            return int(output)

        except:
            print(f"Returning 0, Could not determine the folder size of '{output}'")
            return 0
        finally:
            pass

    def GetAbsoluteFilepath(self, trackNameDecoded):
        return os.path.join(MUSIC_DIR_PATH, trackNameDecoded)

    def GetOldestTrackFilePath(self):
        try:
            output = ""
            p1 = subprocess.Popen(("ls", "-t", MUSIC_DIR_PATH), stdout=subprocess.PIPE)
            p2 = subprocess.Popen(
                ("tail", "-1"),
                stdin=p1.stdout,
                stdout=subprocess.PIPE,
                encoding="utf-8",
            )

            p1.stdout.close()
            rawOutput = p2.communicate()
            p2.stdout.close()

            output = rawOutput[0].strip()
            # ..stdout.decode("ascii")  # .split("\t")[0].strip())

            if output == "":
                return ""
        except:
            print("EXCEPTION:  Could not find oldest track")
            return ""
        finally:
            pass

        return self.GetAbsoluteFilepath(output)

    def PruneOldTracks(self, maxTotalMegabytes):
        # Never delete more than this many files, even if we're still
        # not below the max megabyte limit.
        deleteCountMax = 3

        # As long as the music library is too large, delete the oldest track.
        deleteCount = 0

        try:
            while self.GetMusicDirSizeMegabytes() > maxTotalMegabytes:
                oldestFilePath = self.GetOldestTrackFilePath()
                if not os.path.exists(oldestFilePath):
                    break

                os.unlink(oldestFilePath)
                deleteCount = deleteCount + 1
                if deleteCount >= deleteCountMax:
                    break

        except Exception as e:
            print(f"PruneOldTracks: Unknown Exception: {e}")
            pass
        finally:
            pass

        return deleteCount

    def ClearAndPlay(self, client, musicData):
        try:
            # lets git rid of tracks that have been sitting around for awhile
            self.PruneOldTracks(MUSIC_DIR_MAX_MEGABYTES)

            musicName = None
            musicURI = None

            # we must have all the data or we could run into issues, so if we dont have all the data, than bail
            if len(musicData) != 3:
                print(
                    f"Data inconsistencies, we should have 3 peices of data and we seem to ony have {len(musicData)}"
                )
                return

            musicName = musicData[1]
            musicURI = musicData[2]

            # print(f"Name : {musicName}")
            # print(f"Type : {musicType}")
            # print(f"URI : {musicURI}")

            localPath = ""
            if "file://" in musicURI:
                # Use the file in our local file store
                # print(f"getting local file '{musicURI}'")

                localPath = musicURI.replace("file:///home/pi/media/", "")
                # print(f"getting relative local file '{localPath}'")

                client.stop()
                client.clear()

            elif "https://" in musicURI:
                if not "youtube.com" in musicURI:
                    localPath = musicURI

                    client.stop()
                    client.clear()

                else:

                    # TODO: Come back to this.  It is still a little fragile and may not work.

                    # Download the music from youtube
                    print(f"downloading URL '{musicURI}'")

                    # Generate a unique tmp path and ensure it exists
                    # and has the right permissions.
                    while True:
                        # Create a temp folder to download the file to
                        tempFileName = hashlib.md5(
                            str(random.random()).encode("utf-8")
                        ).hexdigest()

                        uniqueTmpPath = os.path.join(TMP_PATH, tempFileName)
                        print(f"uniqueTmpPath: '{uniqueTmpPath}'")
                        if not os.path.exists(uniqueTmpPath):
                            break

                    # ydl_opts = {
                    #     "format": "bestaudio/best",
                    #     "outtmpl": os.path.join(uniqueTmpPath, "%(title)s.%(ext)s"),
                    #     "noplaylist": True,
                    # }

                    # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    #     ydl.download([musicURI])

                    ydl_opts = {
                        "format": "bestaudio",
                        "outtmpl": os.path.join(uniqueTmpPath, "%(title)s.%(ext)s"),
                        "cachedir": CACHE_PATH,
                        "noplaylist": True,
                        "restrictfilenames": True,
                        # "extractaudio": True,
                        # "audioformat": "mp3",
                        "ignoreerrors": True,
                        "no_color": True,
                        "call_home": False,
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3",
                                "preferredquality": "192",
                            },
                            {"key": "FFmpegMetadata",},
                        ],
                    }

                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        result = ydl.download([musicURI])

                    # Get path of downloaded file
                    # TODO:  Need to figure out how to get the full path of the downloaded file.

                    # Move file to TRACK_DIR_PATH
                    # TODO:  Need to move the file downloaded to the MUSIC_DIR_PATH

                    client.update()
                    client.rescan()
                    client.stop()
                    client.clear()
                    localPath = ""

            else:
                print(f"Dont know what to do here with URI '{musicURI}'")
                return

            if localPath != None and localPath != "":
                print(f"\tAdding:\t'{musicName}'")
                client.add(localPath)
                client.play()

        except Exception as e:
            print(f"Could not play '{musicData}'")
            print(f"ClearAndPlay: Unknown Exception (Ignorring): {e}")
            pass

        finally:
            # print(f"Exiting ClearAndPlay")
            pass

    def initalizeMDP(self):
        """
        We want to make sure that the MPD server is responding

        Paremeters:
        None

        Returns:
        Instance of the MPC Client

        """
        try:
            connectTry = 1
            client = None
            while not client and connectTry <= 5:
                client = self.connectMPD()
                # print(type(client))
                # print(client.mpd_version)  # print the MPD version

                if not client:
                    time.sleep(2)
                else:
                    client.setvol(START_VOLUME)
                    client.clear()
                    # client.add("file:///home/pi/ready.mp3")

                    client.repeat(0)
                    client.random(0)

                    client.crossfade(2)
                    # client.play()
                    #  time.sleep(2)
                connectTry = connectTry + 1

            if client == None or connectTry > 5:
                sys.exit("Failed to create a connection to the MPD server, Exiting!!!")

        except Exception as e:
            print(f"initalizeMDP: Unknown Exception (Ignoring): {e}")
            raise

        return client

    def printStatus(self, client):
        localClientInstance = False
        try:
            if not client:
                client = self.connectMPD()
                localClientInstance = True

            clientStatus = client.status()
            # print(f"Status: {clientStatus}")
            for key in clientStatus:
                try:
                    print(f"status\t{key.ljust(14,' ')} --> {clientStatus[key]}")
                except:
                    pass

            currentsong = client.currentsong()
            # print(f"Status: {clientStatus}")
            for key in currentsong:
                try:
                    print(f"song\t{key.ljust(14,' ')} --> {currentsong[key]}")
                except:
                    pass
        except:  # Exception as e:
            # We should not care about this exception, continue
            # print(f"printStatus: unknown exception: {e}")
            pass

        finally:
            if localClientInstance and client:
                client.close()
                client.disconnect()

    def ProcessCard(self, client, cardData, sameAsPreviousCard):
        try:
            # print(f"Card Data found : '{cardData}'")
            # cardID = cardData[0]
            cardName = cardData[1]
            cardURI = cardData[2]

            if "system://" in cardURI:
                # print(f"System card found.\t{cardURI}")

                if "reboot" in cardURI:
                    # print(f"Rebooting Pi: {cardURI}")
                    os.system("sudo shutdown -r now")
                elif "shutdown" in cardURI:
                    # print(f"Shutting down PI: {cardURI}")
                    os.system("sudo shutdown -P now")
                else:
                    print(f"Unknown System Card: {cardURI}")

            elif "setting://" in cardURI:
                # print(f"Settings card found.\t{cardURI}")

                if "setting://volume" in cardURI:
                    try:
                        # print(f"Volume card found.\t{cardURI}")

                        volume = 0
                        direction = "down"

                        splitURI = cardURI.split("/")
                        if len(splitURI) >= 2:
                            volume = int(splitURI[len(splitURI) - 1])
                            direction = splitURI[len(splitURI) - 2]

                        currentVolume = int(client.status().get("volume"))

                        if not currentVolume:
                            currentVolume = START_VOLUME

                        # round to nearest multiple of 5
                        currentVolume = 5 * round(currentVolume / 5)

                        # print(f"Current Volume : \t{currentVolume}")
                        if currentVolume:
                            if "up" == direction:
                                newVolume = currentVolume + volume
                            else:
                                newVolume = currentVolume - volume

                            if newVolume < 0 or newVolume > 100:
                                newVolume = 0
                            if newVolume > 100:
                                newVolume = 100

                            # print(f"New Volume : \t{newVolume}")
                            client.setvol(newVolume)
                            currentVolume = client.status().get("volume")
                            # print(f"New Volume : \t{ currentVolume }")
                        else:
                            print(
                                "Could not determine the current Volume, keeping current volume"
                            )

                    except Exception as e:
                        print(f"Failed to set volume: {e}")
                        pass
                    finally:
                        pass

            elif "action://" in cardURI:
                try:
                    # print(f"Play card found.\t{cardURI}")
                    # 0002933270,Pause,action,action://action/pause
                    # 0002933269,Play,action,action://action/play
                    # 0002929617,Stop,action,action://action/stop
                    # 0002929612,Next,action,action://action/next
                    # 0002915856,Previous,action,action://action/previous

                    currentVolume = client.status().get("volume")
                    # print(f"State:'{client.status().get('state')}'")
                    if "action://action/pause" == cardURI:
                        # print("Pausing")
                        client.pause()
                    elif "action://action/play" == cardURI:
                        # print("Playing")
                        client.play()
                    elif "action://action/stop" == cardURI:
                        # print("Stopping")
                        client.stop()
                    elif "action://action/next" == cardURI:
                        # TODO: need to address playlists
                        client.Next()
                    elif "action://action/previous" == cardURI:
                        # TODO: need to address playlists
                        client.Previous()
                    # print(f"State:'{client.status().get('state')}'")

                except:
                    print(f"Failed to set playable action")
                    pass
                finally:
                    pass

            #  This must be "file://" or "https://"  TODO: We should check
            else:
                currentSong = client.currentsong()
                if (
                    currentSong
                    and currentSong.get("file") in cardURI
                    and sameAsPreviousCard
                ):
                    # internet based streams do not populate the name propert
                    # immediately, so we will shove something in here until it is popilated
                    if currentSong and currentSong.get("name") is None:
                        currentSong["name"] = cardName

                    print(f"\tSame card: '{currentSong.get('name')}'")
                    if client.status().get("state") == "play":
                        print("\tPausing the music")
                        client.pause()
                    else:
                        print("\tResuming the music")
                        client.play()
                else:
                    # print("Playing a new song")
                    self.ClearAndPlay(client, cardData)
                    return True

        except Exception as e:
            # We should not care about this exception, continue
            print(f"ProcessCard: unknown exception: {e}")
            raise

        return False

    def main(self):
        reader = Reader()
        cardList = CardList()

        before_card = None

        # make sure the MPD Server is responding
        client = self.initalizeMDP()

        cardData = "empty"
        while True:
            try:
                card = ""

                print("Ready: place a card on top of the reader")
                # print(f"\tBefore_card:'{before_card}'")

                card = reader.readCard()
                # print(f"Card read: '{card}'")

                if card == "":
                    # This probably will never happen, but lets check anyway
                    print(f"Card returned invalid data: '{card}'")
                else:
                    # find the data represented by the card
                    cardData = cardList.getPlaylist(card)
                    # if cardData:
                    #     print(f"Found Card Data: {cardData}")

                    if cardData == "":
                        print(f"Card was not found in the Database: '{card}'")
                        print(
                            f"This card '{card}' can be used for adding additional music.  Skipping..."
                        )
                    else:
                        # The card is valid and we found data in the DB for this card, awesome!
                        client = self.connectMPD()

                        # returns false if the card is not a song (System/Setting/Action), otherwise true
                        if self.ProcessCard(client, cardData, card == before_card):
                            before_card = card
                            card = ""

                            currentSong = cardData[1]
                            if client.currentsong().get("name"):
                                currentSong = client.currentsong().get("name")

                        print(
                            f"\tClient Status:\tPlaying:'{currentSong}'\tVolume:'{client.status().get('volume')}'\tState:'{client.status().get('state')}'\n"
                        )

                        client.close()
                        client.disconnect()
                        client = None
            except KeyboardInterrupt:
                sys.exit(0)

            except Exception as e:
                print(f"main: Unknown Exception: {e}")
                time.sleep(2)
                pass

            finally:
                # self.printStatus(None)
                pass


if __name__ == "__main__":
    try:
        app = Box()
        app.main()
    except Exception as ex:
        print(f"global: Unhandled Exception Exiting.... {ex}")
        sys.exit(100)

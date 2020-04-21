#!/usr/bin/env python
import re
from CardList import CardList
from mpd import MPDClient
from Reader import Reader
import sys
import subprocess
import os
import time


ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
MEDIA_PATH = os.path.join(ROOT_PATH, "media")  # /home/pi/music-cards/src/media
TRACK_DIR_PATH = os.path.join(MEDIA_PATH, "tracks")  # /home/pi/jkbox/tracks
MUSIC_DIR_PATH = os.path.join(MEDIA_PATH, "music")  # /home/pi/jkbox/tracks
TMP_PATH = os.path.join(MEDIA_PATH, "tmp")  # /home/pi/jkbox/tmp
MUSIC_DIR_MAX_MEGABYTES = 500


class Box:
    def __init__(self):
        print(f"Starting")

        # print(f"__file__: '{os.path.realpath(__file__)}'")
        # print(f"ROOT_PATH: '{ROOT_PATH}'")
        # print(f"MEDIA_PATH: '{MEDIA_PATH}'")
        # print(f"MUSIC_DIR_PATH: '{MUSIC_DIR_PATH}'")
        # print(f"TMP_PATH: '{TMP_PATH}'")

        os.makedirs(TRACK_DIR_PATH, exist_ok=True)
        os.makedirs(MUSIC_DIR_PATH, exist_ok=True)
        os.makedirs(TMP_PATH, exist_ok=True)

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

    def GetMusicDirSizeMegabytes(self):
        output = 0
        try:
            rawOutput = subprocess.run(
                ["du", "-m", MUSIC_DIR_PATH], capture_output=True
            )

            # print(f"rawOutput: {rawOutput}")
            # decoded = rawOutput.stdout.decode("ascii")
            # print(f"decoded: {decoded}")
            # asciiArray = decoded.split("\t")
            # print(f"asciiArray: {asciiArray}")

            output = rawOutput.stdout.decode("ascii").split("\t")[0].strip()
            # print(f"GetMusicDirSizeMegabytes: output: '{output}'")
            return int(output)

        except:
            print(f"Returning 0, Could not determine the folder size of '{output}'")
            return 0

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

        return self.GetAbsoluteFilepath(output)

    def PruneOldTracks(self, maxTotalMegabytes):
        # Never delete more than this many files, even if we're still
        # not below the max megabyte limit.
        deleteCountMax = 3

        # As long as the music library is too large, delete the oldest track.
        deleteCount = 0
        while self.GetMusicDirSizeMegabytes() > maxTotalMegabytes:
            oldestFilePath = self.GetOldestTrackFilePath()
            if os.path.exists(oldestFilePath) == False:
                break

            os.unlink(oldestFilePath)
            deleteCount = deleteCount + 1
            if deleteCount >= deleteCountMax:
                break

        return deleteCount

    def clear_and_play(self, client, musicData):
        try:
            # lets git rid of tracks that have been sitting around for awhile
            self.PruneOldTracks(MUSIC_DIR_MAX_MEGABYTES)

            musicName = musicData[0]
            musicType = musicData[1]
            musicURI = musicData[2]

            # print(f"Name : {musicName}")
            # print(f"Type : {musicType}")
            # print(f"URI : {musicURI}")

            localPath = ""
            if "URL" == musicType:
                # Download the music from youtube
                print(f"downloading URL '{musicURI}'")
                localPath = ""
            elif "file" == musicType:
                # Use the file in our local file store
                print(f"getting local file '{musicURI}'")
                localPath = ""
            else:
                print(
                    f"Dont know what to do here with filetype '{musicType}' and URI '{musicURI}'"
                )
                return

            print(f"Playing: '{musicName}'")
            client.stop()
            client.clear()
            client.add(musicURI)
            # client.random(1)
            # client.repeat(1)
            # client.play()
        except:
            print(f"Could not play '{musicData}'")

    def initalizeMDP(self):
        """
        We want to make sure that the MPD server is responding

        Paremeters:
        None

        Returns:
        Instance of the MPC Client

        """
        client = None
        while not client:
            client = self.connectMPD()
            if not client:
                time.sleep(2)
            else:
                client.setvol(20)
                client.clear()
                # client.add("file:///home/pi/ready.mp3")
                # client.repeat(0)
                # client.play()
                # time.sleep(2)
        return client

    def main(self):
        reader = Reader()
        cardList = CardList()

        before_card = None
        before_volume = None

        # make sure the MPD Server is responding
        client = self.initalizeMDP()

        cardData = "empty"
        while True:
            try:
                card = ""
                client = self.connectMPD()

                print("\nReady: place a card on top of the reader")
                print(
                    f"Client Status:  Volume:'{client.status().get('volume')}'\tState:'{client.status().get('state')}'"
                )
                print(f"Before_card:'{before_card}'\tbefore_volume:'{before_volume}'")

                card = reader.readCard()
                print(f"Card read: '{card}'")

                if card == "":
                    print(f"Could not find and data for card: '{card}'")
                else:
                    cardData = cardList.getPlaylist(card)

                    if cardData == "":
                        print(f"Card was not found in the Database: '{card}'")
                    else:
                        # print(f"Card Data found : '{cardData}'")

                        cardName = cardData[0]
                        cardType = cardData[1]
                        cardURI = cardData[2]

                        # print(f"Client Status '{ client.status() }'")
                        # print("Connected to MPD Server")

                        # if cardData != "":
                        #     client = self.connectMPD()
                        #     self.clear_and_play(client, cardData)
                        #     client.close()
                        if "setting" == cardType:
                            print("Setting card found.")
                        else:
                            if card == before_card:
                                print("Same card.")
                                if client.status().get("state") != "play":
                                    print("Resuming the music")
                                    client.play()
                                else:
                                    print("Pausing the music")
                                    client.pause()
                            else:
                                print("Playing a new song")
                                before_card = card
                                card = ""
                                # self.clear_and_play(client, card)

                # print(f"Client Status '{ client.status() }'")
                client.close()

            # print("Closing client")
            # client.close()

            # # reader.released_Card()

            # client = connectMPD()
            # if client.status()["state"] != "pause":
            #     client.pause()
            # client.close()

            except KeyboardInterrupt:
                sys.exit(0)

            except ValueError:
                print("this card is new")
                print("need to Set a playlist")
                # reader.released_Card()

            except OSError as e:
                print(f"Execution failed: {e}")
                range(10000)  # some payload code
                time.sleep(0.2)  # sane sleep time of 0.1 seconds

            except Exception as e:
                print(f"unknown exception: {e}")
                time.sleep(2)
                pass

    #     plist = cardList.getPlaylist(card)
    #     if plist != None and plist != "":
    #         print("Playlist", plist[0])
    #         # if plist != "":
    #         #     subprocess.check_call(["./haplaylist.sh %s" % plist], shell=True)
    #         range(10000)  # some payload code
    #         time.sleep(0.2)  # sane sleep time of 0.1 seconds
    #     else:
    #         print("Card %s is not in the card list" % card)
    # except OSError as e:
    #     print("Execution failed:")
    #     range(10000)  # some payload code
    #     time.sleep(0.2)  # sane sleep time of 0.1 seconds


def main():
    app = Box()
    app.main()


if __name__ == "__main__":
    main()

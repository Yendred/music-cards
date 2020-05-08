#!/usr/bin/python3
import os
import sys
from pathlib import Path

from CardList import CardList
from Reader import Reader

MEDIA_PATH = os.path.join(Path.home(), "media")  # ~/media
MUSIC_DIR_PATH = os.path.join(MEDIA_PATH, "music")  # ~/media/music

reader = Reader()
cardList = CardList()

continue_reading = True

print("Welcome to the Music Card Reader")
print("Press Ctrl-C to stop.")

try:
    while continue_reading:
        print("Place the card in the reader")
        card = reader.readCard()
        cardName = ""
        plist = ""

        foundCard = cardList.getPlaylist(card)
        if foundCard:
            print(
                f"This card is in use, continuing will overwrite this card: '{foundCard}'"
            )

        plist = input(
            "Path to Music file, expecting file to be in folder '"
            + MUSIC_DIR_PATH
            + "' , q to quit"
        )
        if plist == "q":
            break

        cardData = [card, cardName, plist]
        if foundCard:
            cardList.removePlaylist(card)
            cardList.addPlaylist(cardData)
            print(f"Updated: {card} : {plist}")
        else:
            cardList.addPlaylist(cardData)
            print(f"Added: {card} : {plist}")

except KeyboardInterrupt:
    sys.exit(0)
finally:
    print("Done.")

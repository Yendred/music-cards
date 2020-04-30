# from readtest import *
from CardList import CardList
from Reader import Reader

reader = Reader()
cardList = CardList()

continue_reading = True

print("Welcome to the MFRC522Music Card Reader")
print("Press Ctrl-C to stop.")

while continue_reading:
    print("Place the card in the reader")
    card = reader.readCard()
    plist = input("Specify Google Playlist Name-NoSpaces, q to quit")
    if plist == "q":
        break
    cardList.addPlaylist(card, plist)
    print(f"Added: {card} : {plist})

print("Done.")

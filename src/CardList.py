import csv
import os.path
import sys


class CardList:
    def __init__(self):
        self.cardListFileName = "cardList.csv"
        self.cardListPath = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), self.cardListFileName
        )
        self.cardList = self.readList()

    def readList(self):
        # print("starting readList()")
        with open(self.cardListPath, mode="r") as csvFile:
            reader = csv.reader(csvFile, delimiter=",")
            cardList = {rows[0]: [rows[0], rows[1], rows[2]] for rows in reader}
            csvFile.close()
            # print("ending readList()")
        return cardList

    def getPlaylist(self, card):
        try:
            if not self.cardList:
                self.cardList = self.readList()

            return self.cardList[card]
        except:
            return ""

    def addPlaylist(self, card, plist):
        try:
            if card not in self.cardList.keys():
                with open(self.cardListPath, mode="a") as csvFile:
                    # csvFile = open(self.cardListPath, "a")
                    csvFile.write(card + ",,," + plist + "\n")
                    csvFile.close()

                    # add the newly addeded card to what is currently held in memory
                    self.cardList[card] = plist
            else:
                print("Card '%s' is already used" % card)
        except:
            print("Could not write file")
            if not os.path.isfile(self.cardListPath):
                print("File '%s' does not exist" % self.cardListPath)

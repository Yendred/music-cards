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
            # print(f"TypeOf CardList : '{type(cardList)}'")
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

    def removePlaylist(self, card):
        try:

            self.cardList.pop(card, None)
            fieldnames = ["ID", "Name", "URI"]
            with open(self.cardListPath, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                # writer = csv.writer(csvfile, delimiter=",")
                writer.writerows(self.cardList)

            # with open(self.cardListPath, "w", newline="\n") as csvfile:
            #     for key, value in self.cardList.items():
            #         if key != card:
            #             print(f"{key}:{value}")
            #             for item in value:
            #                 csvfile.write(f"{item},")
            #             csvfile.writelines("\n")

            # reset the list so that it is read back in on the next access
            self.cardList = None

            # with open(self.cardListPath, mode="w") as csvFile:
            #     for item in self.cardList
            #         if item
            #     csvFile.write(card + "," + cardName + "," + cardURI + "\n")

        except IOError as e:
            print(f"I/O error: {e}")
        except Exception as ex:
            print(f"Unknown Exception: {ex}")
            # print("Could not write file")
            # if not os.path.isfile(self.cardListPath):
            #     print("File '%s' does not exist" % self.cardListPath)

    def addPlaylist(self, cardData):
        try:
            card = cardData[0]
            cardName = cardData[1]
            cardURI = cardData[2]

            if card not in self.cardList.keys():
                with open(self.cardListPath, mode="a") as csvFile:
                    # csvFile = open(self.cardListPath, "a")
                    csvFile.write(card + "," + cardName + "," + cardURI + "\n")

                # add the newly added card to version in memory
                self.cardList[card] = cardData
            else:
                print("Card '%s' is already used" % card)
        except:
            print("Could not write file")
            if not os.path.isfile(self.cardListPath):
                print("File '%s' does not exist" % self.cardListPath)

import random
import datetime
import os

class Player:
    def __init__(self, name):
        self.name = name
        self.board = Board(self.name)
        self.targetBoard = Board("Target")
        self.boats = []
        self.computerShotSet = set()
        self.shotData = []
    def getHitPoints(self):
        hitPoints = 0
        for boat in self.boats:
            hitPoints += boat.getHP()
        return hitPoints
    def shoosAt(self, otherPlayer, row, col):
        if otherPlayer.board.getTile(row, col).isOccupied:
            otherPlayer.hitShip(otherPlayer.board.getTile(row, col).getValue())
            otherPlayer.board.getTile(row, col).updateValue("X")
            self.targetBoard.getTile(row, col).updateValue("X")
            self.addHitData((row, col))
            self.shotData.append(1)
            self.scanForBadShots(otherPlayer)
        else:
            self.targetBoard.getTile(row, col).updateValue("O")
            otherPlayer.board.getTile(row, col).updateValue("O")
            self.shotData.append(0)
            self.scanForBadShots(otherPlayer)
    def hitShip(self, shipLetter):
        try:
            ships = ["P", "C", "S", "D", "A"]
            self.boats[ships.index(shipLetter)].hitPoints -= 1
        except ValueError:
            x = 1
    def addHitData(self, cords):
        adjacentTiles = self.getValidAdjacentTiles(cords)
        oppositeTiles = {'RIGHT': 'LEFT', 'LEFT': 'RIGHT', 'UP': 'DOWN', 'DOWN': 'UP'}
        foundLine = False
        for direction, tile in adjacentTiles.items():
            if ("X" in tile.getValue()) & (oppositeTiles[direction] in adjacentTiles.keys()):
                adjacentTiles[oppositeTiles[direction]].increaseProbability()
                foundLine = True
        if not foundLine:
            for tile in adjacentTiles.values():
                tile.increaseProbability()
    def getValidAdjacentTiles(self, cords):
        adjacentTiles = {}
        x = cords[0]
        y = cords[1]
        if x < 10:
            adjacentTiles["RIGHT"] = self.targetBoard.getTile((x+1), y)
        if x > 1:
            adjacentTiles["LEFT"] = self.targetBoard.getTile((x-1), y)
        if y < 10:
            adjacentTiles["UP"] = self.targetBoard.getTile(x, (y+1))
        if y > 1:
            adjacentTiles["DOWN"] = self.targetBoard.getTile(x, (y-1))
        return adjacentTiles
    def scanForBadShots(self, otherPlayer):
        adjacentDirections = {"UP": ["LEFT", "RIGHT"], "DOWN": ["LEFT", "RIGHT"], "LEFT": ["UP", "DOWN"], "RIGHT": ["UP", "DOWN"]}
        for tile in self.targetBoard.tiles:
            aBoatCanFit = False
            for boatHP in [boat.getHP() for boat in otherPlayer.boats if boat.getHP is not 0]:
                for direction in ["right", "left", "up", "down"]:
                    if self.targetBoard.shipFits(tile.row, tile.col, ("z" * boatHP), direction):
                        aBoatCanFit = True
                        break
            if not aBoatCanFit:
                tile.decreaseProbablitiy()
            for direction, adjacentTile in self.getValidAdjacentTiles((tile.row, tile.col)).items():
                if ("X" in tile.getValue()) & ("X" in adjacentTile.value):
                    for eachDirection in adjacentDirections[direction]:
                        try:
                            tile.getValidAdjacentTiles(self)[eachDirection].decreaseProbablitiy()
                        except KeyError:
                            x = 1
                        try:
                            adjacentTile.getValidAdjacentTiles(self)[eachDirection].decreaseProbablitiy()
                        except KeyError:
                            x = 1
    def getShotCords(self):
        xy = self.getRandomShotCords()
        chosenTile = self.targetBoard.getTile(xy[0], xy[1])
        for tile in self.targetBoard.tiles:
            if (tile not in self.computerShotSet) & (tile.getProbability() > chosenTile.getProbability()):
                chosenTile = tile
        self.computerShotSet.add(chosenTile)
        return chosenTile
    def getRandomShotCords(self):
        while True:
            x = random.randint(1, 10)
            y = random.randint(1, 10)
            if self.targetBoard.getTile(x, y) not in self.computerShotSet:
                return (x, y)
    #def lastNumberOfShotsWereMissed(self, shots):
    #    if self.shotData > 4:
     #       sumOfEndOfList(shots) == 0
    #    else:
      #      return False

class Ship:
    def __init__(self, name, hitPoints):
        self.letter = name[0]
        self.name = name
        self.hitPoints = hitPoints
        self.letterString = self.letter * hitPoints
    def getHP(self):
        return self.hitPoints
    def getLetterString(self):
        return self.letter * self.getHP()

class Tile:
    def __init__(self, x, y, index):
        self.row = x
        self.col = y
        self.value = '[ ] '
        self.index = index
        self.isOccupied = self.value != '[ ] '
        if (x == y) or ((x + y) == 11):
            self.probabilityIsOccupied = 1.2
        else:
            self.probabilityIsOccupied = 1.1
        self.occupyingShip = ""
        self.isANeighbor = False
    def getValidAdjacentTiles(self, player):
        adjacentTiles = {}
        x = self.row
        y = self.col
        if x < 10:
            adjacentTiles["RIGHT"] = player.targetBoard.getTile((x + 1), y)
        if x > 1:
            adjacentTiles["LEFT"] = player.targetBoard.getTile((x - 1), y)
        if y < 10:
            adjacentTiles["UP"] = player.targetBoard.getTile(x, (y + 1))
        if y > 1:
            adjacentTiles["DOWN"] = player.targetBoard.getTile(x, (y - 1))
        return adjacentTiles
    def updateValue(self, value):
        self.value = '[{value}] '.format(value=value)
        if (value is not "X") & (value is not "O"):
            self.occupyingShip = value
    def getValue(self):
        return self.value[1]
    def getProbability(self):
        return self.probabilityIsOccupied
    def increaseProbability(self):
        self.probabilityIsOccupied += 1
    def decreaseProbablitiy(self):
        self.probabilityIsOccupied = 0
    def checkIfNeighbor(self):
        return self.isANeighbor
    def becomeNeighbor(self):
        self.isANeighbor = True

class Board:
    def __init__(self, owner):
        self.tiles = []
        self.owner = owner
        i = 0
        for x in range(1, 11):
            for y in range(1, 11):
                self.tiles.append(Tile(x, y, i))
                i += 1
    def printBoard(self, printIt=True):
        fullstr = "\n\n               "+ self.owner + " Board:\n   A   B   C   D   E   F   G   H   I   J\n1 "
        i = 2
        for tile in self.tiles:
            linenum = str(i)
            if len(linenum) == 1:
                linenum = linenum + " "
            if tile.col == 10:
                fullstr += tile.value + "\n" + linenum
                i += 1
            else:
                fullstr += tile.value
        if printIt:
            print(fullstr[:len(fullstr)-3])
            return fullstr

    def getIndex(self, row, col):
        for tile in self.tiles:
            if (tile.row == row) & (tile.col == col):
                return tile.index
    def getTile(self, row, col):
        return self.tiles[self.getIndex(row, col)]
    def placePiece(self, row, col, value):
        self.getTile(row, col).updateValue(value)
        self.getTile(row, col).isOccupied = True
    def isIllegalSpot(self, row, col, ship, name):
        invalidDirection = False
        if ((self.getTile(row, col).isOccupied) & (self.getTile(row, col).getValue() is not "X")):
            invalidDirection = True
        if (self.getTile(row, col).checkIfNeighbor()) & (name is 'Player'):
            invalidDirection = True
        return invalidDirection
    def shipFits(self, row, col, ship, direction, name=""):
        validDirection = True
        try:
            if direction is "right":
                for section in ship:
                    if self.isIllegalSpot(row, col, ship, name):
                        validDirection = False
                    col += 1
                    if col == 11:
                        validDirection = False
            elif direction is "left":
                for section in ship:
                    if self.isIllegalSpot(row, col, ship, name):
                        validDirection = False
                    col -= 1
                    if col == -1:
                        validDirection = False
            elif direction is "up":
                for section in ship:
                    if self.isIllegalSpot(row, col, ship, name):
                        validDirection = False
                    row += 1
                    if row == 11:
                        validDirection = False
            elif direction is "down":
                for section in ship:
                    if self.isIllegalSpot(row, col, ship, name):
                        validDirection = False
                    row -= 1
                    if row == -1:
                        validDirection = False
        except Exception as e:
            validDirection = False
        return validDirection
    def becomeNeighborInDirection(self, row, col, direction, distanceFromTile=1):
        try:
            if direction is "up":
                self.getTile((row + distanceFromTile), col).becomeNeighbor()
            elif direction is "down":
                self.getTile((row - distanceFromTile), col).becomeNeighbor()
            elif direction is "right":
                self.getTile(row, (col + distanceFromTile)).becomeNeighbor()
            elif direction is "left":
                self.getTile(row, (col - distanceFromTile)).becomeNeighbor()
        except TypeError as e:
            x = 1
    def placeShipInDirection(self, row, col, ship, direction):
        if direction is "right":
            self.becomeNeighborInDirection(row, col, "left")
            self.becomeNeighborInDirection(row, col, "right", len(ship))
            for section in ship:
                try:
                    self.placePiece(row, col, section)
                    self.becomeNeighborInDirection(row, col, "up")
                    self.becomeNeighborInDirection(row, col, "down")
                    col += 1
                except TypeError as e:
                    x = 1
        if direction is "left":
            self.becomeNeighborInDirection(row, col, "left")
            self.becomeNeighborInDirection(row, col, "right", len(ship))
            for section in ship:
                try:
                    self.placePiece(row, col, section)
                    self.becomeNeighborInDirection(row, col, "up")
                    self.becomeNeighborInDirection(row, col, "down")
                    col -= 1
                except TypeError as e:
                    x = 1
        if direction is "up":
            self.becomeNeighborInDirection(row, col, "down")
            self.becomeNeighborInDirection(row, col, "up", len(ship))
            for section in ship:
                try:
                    self.placePiece(row, col, section)
                    self.becomeNeighborInDirection(row, col, "left")
                    self.becomeNeighborInDirection(row, col, "right")
                    row += 1
                except TypeError as e:
                    x = 1
        if direction is "down":
            self.becomeNeighborInDirection(row, col, "up")
            self.becomeNeighborInDirection(row, col, "down", len(ship))
            for section in ship:
                try:
                    self.placePiece(row, col, section)
                    self.becomeNeighborInDirection(row, col, "left")
                    self.becomeNeighborInDirection(row, col, "right")
                    row -= 1
                except TypeError as e:
                    x = 1
    def placeShip(self, row, col, word, direction, name):
        if self.shipFits(row, col, word, direction, name):
            self.placeShipInDirection(row, col, word, direction)
            return True
        else:
            return False

def fillPlayerBoardsWithRandom(players):
    directions = ["right", "left", "up", "down"]
    for player in players:
        patrol = Ship("Patrol Boat", 2)
        cruiser = Ship("Crusier", 3)
        sub = Ship("Sub", 3)
        destroyer = Ship("Destroyer", 4)
        aircraftCarrier = Ship("Aircraft Carrier", 5)
        boats = [patrol, cruiser, sub, destroyer, aircraftCarrier]
        for ship in boats:
            player.boats.append(ship)
            row = random.randint(1,10)
            col = random.randint(1,10)
            direction = random.randint(0, 3)
            while not player.board.placeShip(row, col, ship.letterString, directions[direction], player.name):
                row = random.randint(1,10)
                col = random.randint(1,10)
                direction = random.randint(0, 3)
    return players

def otherPlayer(turn):
    if turn == 0:
        return 1
    else:
        return 0

def translateLetter(letter):
    cols = ["", "A","B","C","D","E","F","G","H","I","J"]
    try:
        return cols.index(letter.capitalize())
    except ValueError:
        return translateLetter(input("Invlid Column please try again"))

def validateRow(x):
    try:
        x = int(x)
        while (x > 10) | (x < 1):
            x = int(input("Invalid Row, please try again"))
        else:
            return x
    except ValueError:
        return validateRow(input("Invalid Row, please try again"))

def logWin(winner):
    gameLogPath = os.path.dirname(__file__) + "\gameLog"
    playerWins = 0
    computerWins = 0
    with open(gameLogPath, mode='rt') as reader:
        log = reader.read()
        log += str(datetime.datetime.today())
        log += "\n" + winner.name + " is winner!"
        log += winner.targetBoard.printBoard(printIt=False)
        log += winner.board.printBoard(printIt=False)
        log += "\n||||||||||||||||||||||||||||||||||||||||||||||||||||||\n"
    with open(gameLogPath, mode='wt') as writer:
        for line in log:
            writer.write(line)
    with open(gameLogPath, mode='rt') as lineReader:
        log = lineReader.readLines()
    for line in log:
        if ("Plyaer" in line) & ("Board" not in line):
            playerWins += 1
        if ("Computer" in line) & ("Board" not in line):
            computerWins += 1
    print("{winner} is the winner!!\nPlayer has won: {playerWins}\nComputer has won: {computerWins}\nComputer/Human Win Ratio: {ratio}".format(
        winner=winner.name, playerWins=playerWins, computerWins=computerWins, ratio=round(computerWins/playerWins, 2)))

def getPlayerFireCords():
    xy = input("\nENTER FIRE COORDINATES:  ")
    if len(xy) == 0:
        return getPlayerFireCords()
    else:
        return xy

def sumOfEndOfList(lst):
    num = 0
    for x in lst[:4]:
        num += x
    return num

players = fillPlayerBoardsWithRandom([Player("Player"), Player("Computer")])
turn = 0
winner = "nobody"
while winner is "nobody":
    if players[turn].getHitPoints() == 0:
        winner = players[otherPlayer(turn)]
        logWin(winner)
    else:
        if players[turn].name is "Player":
            players[turn].targetBoard.printBoard()
            players[turn].board.printBoard()
            xy = getPlayerFireCords()
            y = translateLetter(xy[0])
            x = validateRow(xy[1:])
        else:
            target = players[turn].getShotCords()
            x = target.row
            y = target.col
        players[turn].shoosAt(players[otherPlayer(turn)], x, y)
        turn = otherPlayer(turn)

x = input("")










































from tkinter import *
import random
import itertools

import tdk.gts

DICT = 'scrabble_tr_dictionary.txt'
TIMES = 2

letterTileDict = {
            "A": 12*TIMES, 
            "E": 8*TIMES,
            "İ": 7*TIMES, "K": 7*TIMES, "L": 7*TIMES,
            "R": 6*TIMES,
            "N": 5*TIMES, "T": 5*TIMES,
            "I": 4*TIMES, "M": 4*TIMES,
            "O": 3*TIMES, "S": 3*TIMES, "U": 3*TIMES,
            "B": 2*TIMES, "D": 2*TIMES, "Ü": 2*TIMES, "Y": 2*TIMES, "C": 2*TIMES, "Ç": 2*TIMES, "Ş": 2*TIMES, "Z": 2*TIMES,
            "G": 1*TIMES, "H": 1*TIMES, "P": 1*TIMES, "F": 1*TIMES, "Ö": 1*TIMES, "V": 1*TIMES, "Ğ": 1*TIMES, "J": 1*TIMES
        }

letterPointDict = {
            "A": 1, "E": 1, "İ": 1, "K": 1, "L": 1, "R": 1, "N": 1, "T": 1,
            "I": 2, "M": 2, "O": 2, "S": 2, "U": 2,
            "B": 3, "D": 3, "Ü": 3, "Y": 3,
            "C": 4, "Ç": 4, "Ş": 4, "Z": 4,
            "G": 5, "H": 5, "P": 5,
            "F": 7, "Ö": 7, "V": 7,
            "Ğ": 8,
            "J": 10
        }

tripleWord = [0, 7, 14, 105, 119, 210, 217, 224]
doubleWord = [16, 28, 32, 42, 48, 56, 64, 70, 154, 160, 168, 176, 182, 192, 196, 208]
doubleLetter = [3, 11, 36, 38, 45, 52, 59, 92, 96, 98, 102, 108, 116, 122, 126, 128, 132, 165, 172, 179, 186, 188, 213, 221]
tripleLetter = [20, 24, 76, 80, 84, 88, 136, 140, 144, 148, 200, 204]

# make the dictionary
#doc = open(DICT, "r")
#document = doc.read().lower()
#dictionary = set(document.split('\n'))
#doc.close()

class Node:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class DAWG:
    def __init__(self):
        self.root = Node()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = Node()
            node = node.children[char]
        node.is_end_of_word = True

    def check_word_exists(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

# Create a DAWG and insert words from the dictionary
dawg = DAWG()
doc = open(DICT, "r")
document = doc.read() #.lower()
dictionary = set(document.split('\n'))
doc.close()

for word in dictionary:
    dawg.insert(word)


class boardKeeper():
    def __init__(self):
        row1  = "---------------"
        row2  = "---------------"
        row3  = "---------------"
        row4  = "---------------"
        row5  = "---------------"
        row6  = "---------------"
        row7  = "---------------"
        row8  = "---------------"
        row9  = "---------------"
        row10 = "---------------"
        row11 = "---------------"
        row12 = "---------------"
        row13 = "---------------"
        row14 = "---------------"
        row15 = "---------------"
        self.board = row1 + row2 + row3 + row4 + row5 + row6 + row7 + row8 + row9 + row10 + row11 + row12 + row13 + row14 + row15

        self.tripleWordLocations = tripleWord
        self.doubleWordLocations = doubleWord
        self.doubleLetterLocations = doubleLetter
        self.tripleLetterLocations = tripleLetter

    def changeBoard(self, letterCombo, spaceCombo):
        # Prioritize special locations heuristic
        for (letter, space) in zip(letterCombo, spaceCombo):
            if space in self.tripleWordLocations or space in self.doubleWordLocations or space in self.doubleLetterLocations or space in self.tripleLetterLocations:
                self.board = self.board[:space] + letter + self.board[space+1:]
                return
        for (letter, space) in zip(letterCombo, spaceCombo):
            self.board = self.board[:space] + letter + self.board[space+1:]

    #def changeBoard(self, letterCombo, spaceCombo):
    #    for (letter, space) in zip(letterCombo, spaceCombo):
    #        self.board = self.board[:space] + letter + self.board[space+1:]

    def printBoard(self):
        board = self.board
        for row in range( int(len(board)//15) ):
            for column in range(15):
                print(board[15*row + column], end = ' ')
            print('')

    def refreshOccupied(self):
        board = self.board
        occupied = []
        for spot in range(len(board)):
            if board[spot] not in '-23@#':
                occupied.append(spot)
        return occupied

    def refreshAttachments(self):
        board = self.board
        attachments = set([])

        for i in range(len(board)):
            if board[i] not in '-23@#':
                row = i//15
                column = i%15
                # space directions
                down = (row-1)*15 + column
                up = (row+1)*15 + column
                left = row*15 + column-1
                right = row*15 + column+1
                
                # attachments are added
                if (row != 0) and (board[down] in '-23@#') and (down not in attachments):
                    attachments.add(down)
                if (row != 14) and (board[up] in '-23@#') and (up not in attachments):
                    attachments.add(up)
                if (column != 0) and (board[left] in '-23@#') and (left not in attachments):
                    attachments.add(left)
                if (column != 14) and (board[right] in '-23@#') and (right not in attachments):
                    attachments.add(right)

        if len(attachments) == 0:
            attachments.add(112)
        
        return attachments

def areValidLetters(letters):
    for letter in letters:
        if len(letter) != 1 and (letter not in 'ERTYUIOPASDFGHJKLZCVBNMĞÜŞİÖÇ'): #'ertyuiopasdfghjklzcvbnmğüşiöç'):
            return False
    return True

def areValidLocations(spaces):
    for space in spaces:
        try:
            location = int(space)
        except ValueError:
            return False
    return True

def noSpaceAlreadyOccupied(situation, occupied):
    for spot in situation:
        if spot in occupied:
            return False
    return True

def allInRow(situation):
    row = situation[0]//15
    for spot in range(1, len(situation)):
        if row != situation[spot]//15:
            return (False, 0)
    return (True, row)

def allInColumn(situation):
    column = situation[0]%15
    for spot in range(1, len(situation)):
        if column != situation[spot]%15:
            return (False, 0)
    return (True, column)

def lineConnected(situation, occupied, attachments):
    if len(situation) == 0:
        return (False, '')
    
    rowCheck = allInRow(situation)
    columnCheck = allInColumn(situation)
    
    if rowCheck[0]:
        columns = []
        row = situation[0]//15
        for spot in situation:
            columns.append(spot%15)
        numColumn = 0
        while numColumn != len(columns)-1:
            if (((row*15 + columns[numColumn] + 1) in occupied) and (numColumn != 14)):
                columns = columns[:numColumn+1] + [columns[numColumn] + 1] + columns[numColumn+1:]
            if columns[numColumn] + 1 != columns[numColumn+1]:
                return (False, 'Sütunlar ardişik değil: ' + str(columns[numColumn]) + '/' + str(columns[numColumn+1]))
            numColumn += 1
        return (True, True)
            
    elif columnCheck[0]:
        rows = []       # checks in column
        # adds occupied squares from the correct column
        column = situation[0]%15
        for spot in situation:
            rows.append(spot//15)
        # checks if they are connected in line
        numRow = 0
        while numRow != len(rows)-1:
            # once numRow == len(rows), this loop should end
            if (((rows[numRow]*15 + column + 15) in occupied) and (numRow != 14)):
                rows = rows[:numRow+1] + [rows[numRow] + 1] + rows[numRow+1:]
            if rows[numRow] + 1 != rows[numRow+1]:
                return (False, 'Satirlar ardişik değil: ' + str(rows[numRow]) + '/' + str(rows[numRow+1]))
            numRow += 1
        return (True, False)
        
    else:
        return (False, 'Harfler bir satir ya da sütunda olmali.')

def attached(situation, occupied, attachments):
    isRow = lineConnected(situation, occupied, attachments)[1]
    for spot in situation:
        # Checks if any of the spots is an attachment location. Returns whether it attaches as a row or column.
        if spot in attachments:
            return (True, isRow)
    return (False, '')

def letterLeftRight(spot, occupied):
    column = spot%15
    if column != 0:
        if (spot-1) in occupied:
            return True
    if column != 14:
        if (spot+1) in occupied:
            return True
    return False

def letterUpDown(spot, occupied):
    row = spot//15
    if row != 0:
        if (spot-15) in occupied:
            return True
    if row != 14:
        if (spot+15) in occupied:
            return True
    return False

def getMainCombo(isRowCombo, occupied, situation):
    spot = situation[0]
    locations = [spot]
    locator = spot
    if isRowCombo:
        while (((locator + 1) in occupied) or ((locator + 1) in situation)) and (locator%15 != 14):
            locator += 1
            locations.append(locator)
        # resets the locator to the original position
        locator = spot
        while (((locator - 1) in occupied) or ((locator - 1) in situation)) and (locator%15 != 0):
            locator -= 1
            locations.append(locator)
    else:
        while ((locator + 15) in occupied) or ((locator + 15) in situation):
            locator += 15
            locations.append(locator)
        # resets the locator to the original position
        locator = spot
        while ((locator - 15) in occupied) or ((locator - 15) in situation):
            locator -= 15
            locations.append(locator)
    return sorted(locations)

def getSideCombo(isRowCombo, spot, occupied):
    locations = [spot]
    locator = spot
    if isRowCombo:
        while (locator + 15) in occupied:
            locator += 15
            locations.append(locator)
        locator = spot
        while (locator - 15) in occupied:
            locator -= 15
            locations.append(locator)
    else:
        while ((locator + 1) in occupied) and (locator%15 != 14):
            locator += 1
            locations.append(locator)
        locator = spot
        while ((locator - 1) in occupied) and (locator%15 != 0):
            locator -= 1
            locations.append(locator)
    return sorted(locations)

def getAllCombos(situation, occupied, isRowCombo):
    combosMade = []
    mainCombo = getMainCombo(isRowCombo, occupied, situation)
    if len(mainCombo) != 1:
        combosMade.append(mainCombo)
    # take note, the main combo comes first
    for spot in situation:
        if (isRowCombo) and (letterUpDown(spot, occupied)):
            # checks if it is a row combo and if there exists a side combo
            combosMade.append(getSideCombo(isRowCombo, spot, occupied))
        if (not isRowCombo) and (letterLeftRight(spot, occupied)):
            # checks if it is a row combo and if there exists a side combo
            combosMade.append(getSideCombo(isRowCombo, spot, occupied))
    # for situations where a single letter is played by itself for avoiding errors
    if len(combosMade) == 0:
        combosMade.append(mainCombo)
    # now all of these combos must be checked in the dictionary
    return combosMade

def calcWordValue(combo, letterDict, board):
    wordValue = 0
    timesDouble = 0
    timesTriple = 0

    for spot in combo:
        if spot in doubleWord:
            timesDouble += 1
        elif spot in tripleWord:
            timesTriple += 1
        if spot in doubleLetter:
            if spot in letterDict.keys():
                wordValue += 2 * letterPointDict[letterDict[spot]]
            else:
                wordValue += 2 * letterPointDict[board[spot]]
        elif spot in tripleLetter:
            if spot in letterDict.keys():
                wordValue += 3 * letterPointDict[letterDict[spot]]
            else:
                wordValue += 3 * letterPointDict[board[spot]]
        else:
            if spot in letterDict.keys():
                wordValue += letterPointDict[letterDict[spot]]
            else:
                wordValue += letterPointDict[board[spot]]

    return wordValue * (2**timesDouble) * (3**timesTriple)

def maxComboValue(workingCombos, board):
    maxCombo = [-1, [], []]
    maxLocations = []
    for workingCombo in workingCombos:
        letterDict = {}
        for (letter, space) in zip(workingCombo[0], workingCombo[1]):
            letterDict[space] = letter
        comboValue = 0
        for combo in workingCombo[2]:
            # add value of every combo to the total comboValue
            comboValue += calcWordValue(combo, letterDict, board)
        if len(workingCombo[1]) == 7:
            # add 50 to any combo that uses all seven letters in hand
            comboValue += 50
        if comboValue > maxCombo[0]:
            maxCombo = [comboValue, workingCombo[0], workingCombo[1]]
            maxLocations = workingCombo[1]
    for location in maxLocations:
        if location in tripleWord:
            tripleWord.remove(location)
        elif location in doubleWord:
            doubleWord.remove(location)
        elif location in doubleLetter:
            doubleLetter.remove(location)
        elif location in tripleLetter:
            tripleLetter.remove(location)
    return maxCombo

class letterBag():
    def __init__(self):
        self.letterBag = []
        for key in letterTileDict.keys():
            for _ in range(letterTileDict[key]):
                self.letterBag.append(key)

    def removeLetters(self, num):
        removedLetters = ''
        if num < len(self.letterBag):
            for _ in range(num):
                x = random.random()
                index = int(x*len(self.letterBag) // 1)
                removedLetters += self.letterBag[index]
                self.letterBag.pop(index)
        else:
            for letter in self.letterBag:
                removedLetters += letter
            self.letterBag = []
        return removedLetters

class player():
    def __init__(self):
        self.points = 0
        self.letterHand = ''

    def addPoints(self, addedPoints):
        self.points += addedPoints

    def addToHand(self, letters):
        self.letterHand += letters

    def playFromHand(self, letters):
        for letter in letters:
            index = self.letterHand.find(letter)
            self.letterHand = self.letterHand[:index] + self.letterHand[index+1:]

class humanChecker():
    def __init__(self):
        # make the dictionary of all possible words
        doc = open(DICT, 'r')
        document = doc.read() #.lower()
        self.dictionary = set(document.split('\n'))

    def changeLetterHand(self, letters):
        self.letters = letters

    def mkAlphabet(self, letters):      
        alphabet = {
            "A": 0, "E": 0, "İ": 0, "K": 0, "L": 0, "R": 0, "N": 0, "T": 0,
            "I": 0, "M": 0, "O": 0, "S": 0, "U": 0,
            "B": 0, "D": 0, "Ü": 0, "Y": 0,
            "C": 0, "Ç": 0, "Ş": 0, "Z": 0,
            "G": 0, "H": 0, "P": 0,
            "F": 0, "Ö": 0, "V": 0,
            "Ğ": 0,
            "J": 0
        }
        for char in letters:
            if char in """1234567890!@#$%^&*()[]{}:;"'<>,.?/|~`\\ """:
                return 'Error'      # needs more editing
            else:
                alphabet[char] += 1
        return alphabet

    def enoughLetters(self, letterCombo):
        if '$' in letterCombo:
            return False
        letterHandAlphabet = self.mkAlphabet(self.letters)
        letterComboAlphabet = self.mkAlphabet(letterCombo)
        for letter in letterHandAlphabet.keys():
            if letterComboAlphabet[letter] > letterHandAlphabet[letter]:
                return False
        return True

    def comboValid(self, letters, spaces, board, occupied, dictionary, combos):
        for combo in combos:
            # check starts
            possibleWord = ''
            for spot in combo:
                if spot in spaces:
                    possibleWord += letters[spaces.index(spot)]
                else:
                    possibleWord += board[spot]
            if not tdk.gts.search(possibleWord): #.lower()):
                message = 'Böyle bir kelime bulunamadi: ' + possibleWord
                return (False, message)
        return (True, '')

    def comboWorks(self, letters, spaces, board, occupied, attachments, dictionary):
        if self.enoughLetters(letters):
            message = ''
            if noSpaceAlreadyOccupied(spaces, occupied):
                message = ''
                lineCheck = lineConnected(spaces, occupied, attachments)
                if lineCheck[0]:
                    message = ''
                    if attached(spaces, occupied, attachments)[0]:
                        message = ''
                        combos = getAllCombos(spaces, occupied, lineCheck[1])
                        validCombo = self.comboValid(letters, spaces, board, occupied, dictionary, combos)
                        if validCombo[0]:
                            message = ''
                            return (True, combos, message)
                        else:
                            message = validCombo[1]
                    else:
                        message = ''
                else:
                    message = lineCheck[1]
            else:
                message = ''
        else:
            message = ''

        return (False, [], message)

class State:
    def __init__(self, board, hand):
        self.board = boardKeeper
        self.hand = hand

    def get_possible_moves(self):
        # Generate all possible moves from the current state.
        possible_moves = []
        for letter in self.hand:
            for position in self.board.refreshOccupied():
                if self.is_valid_move(position, letter):
                    possible_moves.append((position, letter))
        return possible_moves

    def make_move(self, move):
        # Make a move and return a new state.
        new_board = self.board
        new_hand = self.hand.copy()
        position, letter = move
        new_board.changeBoard(letter, position)
        new_hand.remove(letter)
        return State(new_board, new_hand)

    def is_valid_move(self, position, letter):
        # Check if a move is valid.
        attachments = self.board.refreshAttachments()
        return position in attachments

    def is_terminal(self):
        # Check if the game is over.
        return len(self.hand) == 0 or not self.get_possible_moves()
    
    def result(self):
        # Returns 1 if the game is won, 0 if the game is lost, and 0.5 if the game is a draw.
        if len(self.hand) == 0:
            return 1
        elif not self.get_possible_moves():
            return 0
        else:
            return 0.5

class Node:
    def __init__(self, move, parent=None, state=None):
        self.move = move
        self.parent = parent
        self.state = state
        self.children = []
        self.wins = 0
        self.visits = 0

    def add_child(self, move, state):
        node = Node(move, self, state)
        self.children.append(node)
        return node

    def update(self, result):
        self.visits += 1
        self.wins += result

    def fully_expanded(self):
        return len(self.children) == len(self.state.get_possible_moves())

    def best_child(self):
        if self.children:
            return max(self.children, key=lambda node: node.wins / node.visits)
        else:
            return None
        
    def evaluate(self):
        if self.visits > 0:
            return self.wins / self.visits
        else:
            return 0

class computerChecker():
    def monte_carlo_tree_search(self, root):
        best_child = root.best_child()
        if best_child is not None:
            return best_child.move
        else:
            return None

    def _tree_policy(self, node):
        while not node.state.is_terminal():
            if not node.fully_expanded():
                return self._expand(node)
            else:
                node = node.best_child()
        return node

    def _expand(self, node):
        move = node.state.get_possible_moves()[len(node.children)]
        return node.add_child(move, node.state.make_move(move))

    def _rollout(self, state):
        while not state.is_terminal():
            move = random.choice(state.get_possible_moves())
            state = state.make_move(move)
        return state.result()  # 1 for a win, 0 for a loss.

    def _backpropagate(self, node, result):
        while node is not None:
            node.update(result)
            node = node.parent    

    def minimax(self, node, depth, maximizingPlayer):
        if depth == 0 or node.is_terminal():
            return node.evaluate()

        if maximizingPlayer:
            maxEval = float('-inf')
            for child in node.children:
                eval = self.minimax(child, depth - 1, False)
                maxEval = max(maxEval, eval)
            return maxEval

        else:
            minEval = float('inf')
            for child in node.children:
                eval = self.minimax(child, depth - 1, True)
                minEval = min(minEval, eval)
            return minEval
        
    def changeLetterHand(self, letters):
        self.letters = letters

    def conformsBetterRules(self, situation, attachments):
        for spot in situation:
            # checks if any of the spots is an attachment location
            if spot in attachments:
                return True
        return False

    def getMainCombo(self, isRowCombo, spot, occupied, situation):
        locations = [spot]
        locator = spot
        if isRowCombo:
            while (((locator + 1) in occupied) or ((locator + 1) in situation)) and (locator%15 != 14):
                locator += 1
                locations.append(locator)
            locator = spot
            while ((locator - 1) in occupied) and (locator%15 != 0):
                locator -= 1
                locations.insert(0, locator)
        else:
            while ((locator + 15) in occupied) or ((locator + 15) in situation):
                locator += 15
                locations.append(locator)
            locator = spot
            while (locator - 15) in occupied:
                locator -= 15
                locations.insert(0, locator)
        return locations

    def getSideCombo(self, isRowCombo, spot, occupied):
        locations = [spot]
        locator = spot
        if isRowCombo:
            while (locator + 15) in occupied:
                locator += 15
                locations.append(locator)
            locator = spot
            while (locator - 15) in occupied:
                locator -= 15
                locations.insert(0, locator)
        else:
            while ((locator + 1) in occupied) and (locator%15 != 14):
                locator += 1
                locations.append(locator)
            locator = spot
            while ((locator - 1) in occupied) and (locator%15 != 0):
                locator -= 1
                locations.insert(0, locator)

        if locations == [spot]:
            return []
        return locations

    def getAllCombos(self, situation, occupied, isRowCombo):
        combosMade = []
        mainCombo = self.getMainCombo(isRowCombo, situation[0], occupied, situation)
        if len(mainCombo) != 1:
            combosMade.append(mainCombo)
        for spot in situation:
            sideCombo = self.getSideCombo(isRowCombo, spot, occupied)
            if sideCombo != []:
                combosMade.append(sideCombo)
        if len(combosMade) == 0:
            combosMade.append(mainCombo)
        return combosMade

    def getLetterCombos(self):
        letters = self.letters
        letterCombos = []
        for length in range(1, len(letters)+1):
            listTuples = list( itertools.permutations(list(letters), length) )
            letterCombos.append( set(listTuples) )
        return letterCombos

    def getSpaceCombos(self, board, occupied, attachments):
        letters = self.letters

        spaceCombos = []

        for length in range(1, len(letters)+1):
            rows = []
            columns = []

            for spot in range(len(board)):
                if spot not in occupied:
                    row = spot//15
                    column = spot%15 + 1
                    spaceCount = 1
                    spaceCombo = [spot]
                    while spaceCount != length:
                        if column != 15:
                            if (row*15 + column) not in occupied:
                                spaceCount += 1
                                spaceCombo.append(row*15 + column)
                            column += 1
                        else:
                            spaceCount = length
                    if len(spaceCombo) == length and self.conformsBetterRules(spaceCombo, attachments):
                        rows.append(spaceCombo)

            if length != 1:
                for spot in range(len(board)):
                    if spot not in occupied:
                        row = spot//15 + 1
                        column = spot%15
                        spaceCount = 1
                        spaceCombo = [spot]
                        while spaceCount != length:
                            if row != 15:
                                if (row*15 + column) not in occupied:
                                    spaceCount += 1
                                    spaceCombo.append(row*15 + column)
                                row += 1
                            else:
                                spaceCount = length
                        if len(spaceCombo) == length and self.conformsBetterRules(spaceCombo, attachments):
                            columns.append(spaceCombo)

            spaceCombos.append([rows, columns])

        return spaceCombos

    def comboWorks(self, letterCombo, spaceCombo, board, occupied, dictionary, isRowCombo):
        self.allCombos = self.getAllCombos(spaceCombo, occupied, isRowCombo)
        for combo in self.allCombos:
            possibleWord = ''
            for spot in combo:
                if spot in spaceCombo:
                    possibleWord += letterCombo[spaceCombo.index(spot)]
                else:
                    possibleWord += board[spot]

            if possibleWord not in dictionary:
            #if not dawg.check_word_exists(possibleWord): #.lower()):
            #if possibleWord.lower() not in dictionary:
            #if not tdk.gts.search(possibleWord.lower()):
                return False
        return True

    def getDirectedCombos(self, board, occupied, attachments, dictionary):
        allLetterCombos = self.getLetterCombos()
        allSpaceCombos = self.getSpaceCombos(board, occupied, attachments)

        workingCombos = []
        for (letterCombos, spaceCombos) in zip(allLetterCombos, allSpaceCombos):
            for letterCombo in letterCombos:
                for spaceCombo in spaceCombos[0]:
                    # row combos dealt with first
                    if self.comboWorks(letterCombo, spaceCombo, board, occupied, dictionary, True):
                        workingCombos.append([letterCombo, spaceCombo, self.allCombos])
                for spaceCombo in spaceCombos[1]:
                    # column combos dealt with second
                    if self.comboWorks(letterCombo, spaceCombo, board, occupied, dictionary, False):
                        workingCombos.append([letterCombo, spaceCombo, self.allCombos])

        return workingCombos

class dataStorage():
    def __init__(self, data):
        self.data = data
        self.data.dataCenter = 750
        self.data.squareLeft = 20
        self.data.squareTop = 70
        self.data.backgroundFill = "#F5CDCD"
        self.data.instructionFill = "#F5FDFD"
        self.data.emptySquareFill = "#E5FDFD"
        self.data.tripleWordFill = "red"
        self.data.doubleWordFill = "orange"
        self.data.doubleLetterFill = "yellow"
        self.data.tripleLetterFill = "green"
        self.data.occupiedSquareFill = "magenta"
        self.data.handSquareFill = "#66DDDD"
        self.data.squareSize = 32

        # for the scrabble board
        self.data.emptyBoardLocations = []
        self.data.board = ''
        for i in range(225):
            self.data.emptyBoardLocations.append(i)
            self.data.board += '-'
        self.data.occupiedBoardLocations = []
        self.data.occupiedBoardLetters = []
        self.data.temporaryBoardLocations = []
        self.data.temporaryBoardLetters = []

        # letters in hand
        self.data.computerLetterHand = 'abcdefg'

        self.data.letterHand = 'abcdefg'
        self.data.emptyHandLocations = []
        self.data.occupiedHandLocations = [0, 1, 2, 3, 4, 5, 6]
        self.data.canSwitchFromHand = False
        self.data.canSwitchFromBoard = False
        self.data.firstClickLocation = -1
        self.data.firstClickLetter = '_'

        self.data.letterBagSize = 0
        self.data.humanScore = 0
        self.data.computerScore = 0

        self.data.tripleWord = []
        self.data.doubleWord = []
        self.data.doubleLetter = []
        self.data.tripleLetter = []

        self.data.humanTurn = False
        self.data.computerTurn = False
        self.data.passTurn = False
        self.data.playTurn = False
        self.data.switchTurn = False
        self.data.invalidTurn = True
        self.data.searchOn = False

        self.data.isPaused = False
        self.data.timerDelay = 50
        self.data.message1 = ''
        self.data.message2 = "Başlamak için herhangi bir yere tiklayin."
        self.data.message3 = ''

    def changeScore(self, score, forHuman):
        if forHuman:
            self.data.humanScore = score
        else:
            self.data.computerScore = score

    def changeLetterBagSize(self, letterBagSize):
        self.data.letterBagSize = letterBagSize

    def changeLetterHand(self, letterHand):
        self.data.letterHand = letterHand

    def humanChangeBoard(self, board):
        for i in range(len(self.data.temporaryBoardLocations)):
            self.data.occupiedBoardLocations.append(self.data.temporaryBoardLocations[i])
            self.data.occupiedBoardLetters.append(self.data.temporaryBoardLetters[i])
        self.data.temporaryBoardLocations = []
        self.data.temporaryBoardLetters = []

    def computerChangeBoard(self, board, letters, spaces):
        self.data.board = board
        for (letter, space) in zip(letters, spaces):
            self.data.emptyBoardLocations.remove(space)
            self.data.occupiedBoardLocations.append(space)
            self.data.occupiedBoardLetters.append(letter)

    def returnTemporaryLetters(self):
        for letter in self.data.temporaryBoardLetters:
            self.data.letterHand += letter
        for i in range(len(self.data.letterHand)-1, 0, -1):
            if self.data.letterHand[i] == '-':
                self.data.letterHand = self.data.letterHand[:i] + self.data.letterHand[i+1:]
        self.data.emptyBoardLocations += self.data.temporaryBoardLocations
        for location in self.data.temporaryBoardLocations:
            self.data.board = self.data.board[:location] + '-' + self.data.board[location+1:]
        handSize = len(self.data.temporaryBoardLocations)+len(self.data.occupiedHandLocations)
        self.data.occupiedHandLocations = []
        for i in range(handSize):
            self.data.occupiedHandLocations.append(i)
        self.data.temporaryBoardLocations = []
        self.data.temporaryBoardLetters = []

    def resetHand(self, letterHand):
        self.data.occupiedHandLocations = []
        for i in range(len(letterHand)):
            self.data.occupiedHandLocations.append(i)
        self.data.emptyHandLocations = []

    def refreshSpecialTiles(self, tw, dw, dl, tl):
        self.data.tripleWord = tw
        self.data.doubleWord = dw
        self.data.doubleLetter = dl
        self.data.tripleLetter = tl

    def resetData(self):
        self.data.canSwitchFromHand = False
        self.data.canSwitchFromBoard = False
        self.data.firstClickLocation = -1
        self.data.firstClickLetter = '_'
        self.data.invalidTurn = True

    def firstClickHand(self, handColumn):
        self.data.message1 = ""
        self.data.message2 = ""
        self.data.canSwitchFromHand = True
        self.data.firstClickLocation = handColumn

    def firstClickBoard(self, spot):
        self.data.message1 = ""
        self.data.message2 = ""
        self.data.canSwitchFromBoard = True
        self.data.firstClickLocation = spot

    def emptyHandBoardSwitch(self, spot):
        handColumn = self.data.firstClickLocation
        # switch the letters
        letterCopy = self.data.letterHand[handColumn]
        self.data.letterHand = self.data.letterHand[:handColumn] + self.data.board[spot] + self.data.letterHand[handColumn+1:]
        self.data.board = self.data.board[:spot] + letterCopy + self.data.board[spot+1:]
        # update the data
        self.data.emptyBoardLocations.remove(spot)      # empty board location becomes temporary
        self.data.temporaryBoardLocations.append(spot)
        self.data.temporaryBoardLetters.append(self.data.board[spot])
        self.data.occupiedHandLocations.remove(handColumn)      # remove the letter
        self.data.emptyHandLocations.append(handColumn)         # add to empty hand locations
        self.data.message1 = ""
        self.data.message2 = ""

    def temporaryHandBoardSwitch(self, spot):
        handColumn = self.data.firstClickLocation
        index = self.data.temporaryBoardLocations.index(spot)
        letterCopy = self.data.letterHand[handColumn]
        self.data.temporaryBoardLetters = self.data.temporaryBoardLetters[:index] + [letterCopy] + self.data.temporaryBoardLetters[index+1:]
        self.data.letterHand = self.data.letterHand[:handColumn] + self.data.board[spot] + self.data.letterHand[handColumn+1:]
        self.data.board = self.data.board[:spot] + letterCopy + self.data.board[spot+1:]
        self.data.message1 = ""
        self.data.message2 = ""

    def occupiedHandHandSwitch(self, handColumn):
        handColumn1 = self.data.firstClickLocation
        handColumn2 = handColumn
        letter1 = self.data.letterHand[handColumn1]
        letter2 = self.data.letterHand[handColumn2]
        self.data.letterHand = self.data.letterHand[:handColumn1] + letter2 + self.data.letterHand[handColumn1+1:]
        self.data.letterHand = self.data.letterHand[:handColumn2] + letter1 + self.data.letterHand[handColumn2+1:]
        self.data.message1 = ""
        self.data.message2 = ""
        
    def emptyHandHandSwitch(self, handColumn):
        handColumn1 = self.data.firstClickLocation
        handColumn2 = handColumn
        letter1 = self.data.letterHand[handColumn1]
        letter2 = self.data.letterHand[handColumn2]
        self.data.letterHand = self.data.letterHand[:handColumn1] + letter2 + self.data.letterHand[handColumn1+1:]
        self.data.letterHand = self.data.letterHand[:handColumn2] + letter1 + self.data.letterHand[handColumn2+1:]
        self.data.occupiedHandLocations.remove(handColumn1)
        self.data.emptyHandLocations.remove(handColumn2)
        self.data.occupiedHandLocations.append(handColumn2)
        self.data.emptyHandLocations.append(handColumn1)
        self.data.message1 = ""
        self.data.message2 = ""

    def occupiedBoardHandSwitch(self, handColumn):
        spot = self.data.firstClickLocation
        index = self.data.temporaryBoardLocations.index(spot)
        letterCopy = self.data.letterHand[handColumn]
        self.data.temporaryBoardLetters = self.data.temporaryBoardLetters[:index] + [letterCopy] + self.data.temporaryBoardLetters[index+1:]
        self.data.letterHand = self.data.letterHand[:handColumn] + self.data.board[spot] + self.data.letterHand[handColumn+1:]
        self.data.board = self.data.board[:spot] + letterCopy + self.data.board[spot+1:]
        self.data.message1 = ""
        self.data.message2 = ""

    def emptyBoardHandSwitch(self, handColumn):
        spot = self.data.firstClickLocation
        index = self.data.temporaryBoardLocations.index(spot)   # index maps to both location and letter
        self.data.temporaryBoardLocations.pop(index)        # temporary board location becomes empty
        self.data.temporaryBoardLetters.pop(index)
        self.data.emptyBoardLocations.append(spot)
        self.data.occupiedHandLocations.append(handColumn)      # remove the letter
        self.data.emptyHandLocations.remove(handColumn)         # add to empty hand locations
        # switch the letters
        letterCopy = self.data.letterHand[handColumn]
        self.data.letterHand = self.data.letterHand[:handColumn] + self.data.board[spot] + self.data.letterHand[handColumn+1:]
        self.data.board = self.data.board[:spot] + letterCopy + self.data.board[spot+1:]
        self.data.message1 = ""
        self.data.message2 = ""

    def emptyBoardBoardSwitch(self, spot):
        spot1 = self.data.firstClickLocation
        spot2 = spot
        letter1 = self.data.board[spot1]
        letter2 = self.data.board[spot2]
        self.data.board = self.data.board[:spot1] + letter2 + self.data.board[spot1+1:]
        self.data.board = self.data.board[:spot2] + letter1 + self.data.board[spot2+1:]
        index1 = self.data.temporaryBoardLocations.index(spot1)
        index2 = self.data.emptyBoardLocations.index(spot2)
        self.data.temporaryBoardLocations[index1] = spot2
        self.data.emptyBoardLocations[index2] = spot1
        self.data.message1 = ""
        self.data.message2 = ""

    def temporaryBoardBoardSwitch(self, spot):
        spot1 = self.data.firstClickLocation
        spot2 = spot
        letter1 = self.data.board[spot1]
        letter2 = self.data.board[spot2]
        self.data.board = self.data.board[:spot1] + letter2 + self.data.board[spot1+1:]
        self.data.board = self.data.board[:spot2] + letter1 + self.data.board[spot2+1:]
        index1 = self.data.temporaryBoardLocations.index(spot1)
        index2 = self.data.temporaryBoardLocations.index(spot2)
        self.data.temporaryBoardLocations[index1] = spot2
        self.data.temporaryBoardLocations[index2] = spot1
        self.data.message1 = ""
        self.data.message2 = ""

    def mousePressed(self, event):
        column = ((event.x - self.data.squareLeft) // self.data.squareSize)
        if (column > 14 or column < 0):
            column = 225        # if outside of board, column is only used for the board
        row = ((event.y - self.data.squareTop) // self.data.squareSize)
        spot = row*15 + column          # spot in grid
        onTemporarySpot = spot in self.data.temporaryBoardLocations
        onEmptySpot = spot in self.data.emptyBoardLocations

        handRow = (event.y - 360)//self.data.squareSize
        handColumn = ((event.x - (self.data.dataCenter-115))//self.data.squareSize)        # column in the hand
        occupiedInHand = ((handRow == 0) and (handColumn in self.data.occupiedHandLocations))
        emptyInHand = ((handRow == 0) and (handColumn in self.data.emptyHandLocations))

        onPassButton = (event.y >= 400 and event.y < 430) and (event.x >= 650 and event.x < 700)
        onPlayButton = (event.y >= 400 and event.y < 430) and (event.x >= 700 and event.x < 750)
        onSwitchButton = (event.y >= 400 and event.y < 430) and (event.x >= 750 and event.x < 800)
        onSearchButton = (event.y >= 400 and event.y < 430) and (event.x >= 800 and event.x < 850)
        
        if self.data.canSwitchFromHand:
            if onEmptySpot: self.emptyHandBoardSwitch(spot)     # firstClick was on the hand
            elif onTemporarySpot: self.temporaryHandBoardSwitch(spot)
            elif occupiedInHand: self.occupiedHandHandSwitch(handColumn)
            elif emptyInHand: self.emptyHandHandSwitch(handColumn)
            else:
                self.data.message1 = ""
                self.data.message2 = ""
            self.data.firstClickLocation = -1       # if can switch, reset first click no matter what
            self.data.canSwitchFromHand = False     # if can switch, reset boolean no matter what
        elif self.data.canSwitchFromBoard:
            if occupiedInHand: self.occupiedBoardHandSwitch(handColumn)    # firstClick was on the board
            elif emptyInHand: self.emptyBoardHandSwitch(handColumn)
            elif onEmptySpot: self.emptyBoardBoardSwitch(spot)
            elif onTemporarySpot: self.temporaryBoardBoardSwitch(spot)
            else:
                self.data.message1 = ""
                self.data.message2 = ""
            self.data.firstClickLocation = -1       # if can switch, reset first click no matter what
            self.data.canSwitchFromBoard = False    # if can switch, reset boolean no matter what
        else:
            if occupiedInHand: self.firstClickHand(handColumn)
            elif onTemporarySpot: self.firstClickBoard(spot)
            elif onEmptySpot:
                self.data.message1 = ""
                self.data.message2 = ""
            elif onPassButton:
                self.data.passTurn = True
                self.data.message1 = "Pas geçildi."
                self.data.message2 = "Herhangi bir yere tikla."
            elif onPlayButton:
                self.data.playTurn = True
                self.data.message1 = "Oynandi."
                self.data.message2 = ""
            elif onSwitchButton:
                self.data.switchTurn = True
                self.data.message1 = "Harfleri geri al."
                self.data.message2 = ""
            elif onSearchButton:
                self.data.searchOn = True
            else:
                self.data.message1 = ""
                self.data.message2 = ""

    def keyPressed(self, event):
        if (event.char == "p"):
            self.data.isPaused = not self.data.isPaused

    def drawBoardSquare(self, canvas, row, column, letter, fillColor):
        data = self.data
        canvas.create_rectangle(data.squareLeft + column*data.squareSize,
                    data.squareTop + row*data.squareSize,
                    data.squareLeft + column*data.squareSize + data.squareSize,
                    data.squareTop + row*data.squareSize + data.squareSize,
                    fill=fillColor)
        canvas.create_text(data.squareLeft + (column+0.5)*data.squareSize,
                    data.squareTop + (row+0.5)*data.squareSize,
                    text=letter, font="Arial 10")
        if letter in letterPointDict:
            canvas.create_text(data.squareLeft+8 + (column+0.5)*data.squareSize,
                   data.squareTop + (row+0.5)*data.squareSize + 8,
                   text=str(letterPointDict[letter]),
                   font="Arial 8")

    def redrawAll(self, canvas):
        data = self.data
        
        spotList = []
        for i in range(225):
            spotList.append(i)

        # instruction background
        canvas.create_rectangle(0, 0, 1000, 600, fill=data.backgroundFill)
        canvas.create_rectangle(data.dataCenter-190, 35, data.dataCenter+190, 460, fill=data.instructionFill)
            
        for (letter, spot) in zip(data.board, spotList):
            row = spot//15
            column = spot%15
            letter = data.board[spot]
            if spot in data.emptyBoardLocations:
                if spot in data.tripleWord:
                    self.drawBoardSquare(canvas, row, column, "3xK", data.tripleWordFill)
                elif spot in data.doubleWord:
                    self.drawBoardSquare(canvas, row, column, "2xK", data.doubleWordFill)
                elif spot in data.doubleLetter:
                    self.drawBoardSquare(canvas, row, column, "2xH", data.doubleLetterFill)
                elif spot in data.tripleLetter:
                    self.drawBoardSquare(canvas, row, column, "3xH", data.tripleLetterFill)
                else:
                    self.drawBoardSquare(canvas, row, column, letter, data.emptySquareFill)
            elif spot in data.temporaryBoardLocations:
                self.drawBoardSquare(canvas, row, column, letter, data.handSquareFill)
            else:
                # for occupied squares
                self.drawBoardSquare(canvas, row, column, letter, data.occupiedSquareFill)

        # draw the letter hand
        canvas.create_text(data.dataCenter+2, 345, text="", font="Arial 10")

        indexList = []
        for i in range(len(data.letterHand)):
            indexList.append(i)
        
        for (letter, column) in zip(data.letterHand, indexList):
            if letter == '-':
                canvas.create_rectangle(data.dataCenter-115 + data.squareSize*column,
                                360,
                                data.dataCenter-115 + data.squareSize*column + data.squareSize,
                                360 + data.squareSize,
                                fill=data.emptySquareFill)
            else:
                canvas.create_rectangle(data.dataCenter-115 + data.squareSize*column,
                                360,
                                data.dataCenter-115 + data.squareSize*column + data.squareSize,
                                360 + data.squareSize,
                                fill=data.handSquareFill)
            canvas.create_text(data.dataCenter-115 + data.squareSize*(column+0.5),
                               360 + data.squareSize/2,
                               text=letter,
                               font="Arial 10")
            if letter in letterPointDict:
                canvas.create_text(data.dataCenter-115+8 + data.squareSize*(column+0.5),
                       360 + data.squareSize/2 + 8,
                       text=str(letterPointDict[letter]),
                       font="Arial 8")

        # draw the buttons
        canvas.create_rectangle(650, 400, 700, 430, fill="orange")
        canvas.create_rectangle(700, 400, 750, 430, fill="orange")
        canvas.create_rectangle(750, 400, 800, 430, fill="orange")
        #canvas.create_rectangle(800, 400, 850, 430, fill="orange")
        canvas.create_text(675, 415, text="Pas", font="Arial 10")
        canvas.create_text(725, 415, text="Oyna", font="Arial 10")
        canvas.create_text(775, 415, text="Geri Al", font="Arial 10")
        #canvas.create_text(825, 415, text="Search", font="Arial 10")

        # draw the score
        canvas.create_rectangle(data.dataCenter-140, 250, data.dataCenter+140, 290, fill="#66FF66")

        # draw the text
        canvas.create_text(265, 50, text="Scrabble", font="Arial 20")
        canvas.create_text(data.dataCenter, 60, text="", font="Arial 15")
        #canvas.create_text(data.dataCenter, 100, text="Pressing 'p' pauses/unpauses timer")
        canvas.create_text(data.dataCenter, 120, text="")

        canvas.create_text(data.dataCenter, 160, text=(" "), font="Arial 15")
        canvas.create_text(data.dataCenter, 190, text=(data.message1), font="Arial 10")
        canvas.create_text(data.dataCenter, 210, text=(data.message2), font="Arial 10")
        canvas.create_text(data.dataCenter, 230, text=(data.message3), font="Arial 10")

        canvas.create_text(data.dataCenter, 260, text=("Skor:"), font="Arial 10")
        canvas.create_text(data.dataCenter, 280, text=("İnsan: " + str(data.humanScore) + "      AI: " + str(data.computerScore)), font="Arial 10")
        
        if data.letterBagSize == 0:
            canvas.create_text(data.dataCenter, 300, text=("HARF KALMADI!!!"), font="Arial 10")
        else:
            canvas.create_text(data.dataCenter, 300, text=("Torbada Kalan Harf Sayısı: " + str(data.letterBagSize)), font="Arial 10")

        canvas.create_text(data.dataCenter, 320, text="AI harfleri: " + computerPlayer.letterHand, font="Arial 10")
        #canvas.create_text(data.dataCenter, 320, text="Computer Letters: " + ' '.join(get_close_matches(''.join(data.letterHand), tdk.gts.index())), font="Arial 10")

boardKeeper = boardKeeper()
humanPlayer = player()
computerPlayer = player()
humanCheck = humanChecker()
computerCheck = computerChecker()
letterBag = letterBag()

def run(width=1000, height=600):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height, fill='white', width=0)
        x.redrawAll(canvas)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        if x.data.endOfGame:
            x.data.message1 = "Oyun Bitti!!!"
            if humanPlayer.points > computerPlayer.points:
                x.data.message2 = 'İnsan kazandi!'
            elif humanPlayer.points < computerPlayer.points:
                x.data.message2 = 'AI kazandi!'
            else:
                x.data.message2 = "Berabere!"

        elif x.data.computerTurn:
            # case of computer turn
            x.data.message1 = "Sira bilgisayarda..."
            x.data.message2 = ''
            x.data.message3 = ''
            redrawAllWrapper(canvas, data)

            occupied = set(boardKeeper.refreshOccupied())
            attachments = set(boardKeeper.refreshAttachments())

            # bestMove = computerCheck.minimax(boardKeeper.board, computerPlayer.letterHand, dictionary, True)
            # state = State(boardKeeper.board, computerPlayer.letterHand)
            # best_move = computerCheck.monte_carlo_tree_search(state)            
            # maxCombo = maxComboValue(bestMove, boardKeeper.board)

            computerCheck.changeLetterHand(computerPlayer.letterHand)
            computerCheck.getLetterCombos()
            workingCombos = computerCheck.getDirectedCombos(boardKeeper.board, occupied, attachments, dictionary)
            maxCombo = maxComboValue(workingCombos, boardKeeper.board)
            if maxCombo[0] != -1:
                x.refreshSpecialTiles(tripleWord, doubleWord, doubleLetter, tripleLetter)
                boardKeeper.changeBoard(maxCombo[1], maxCombo[2])
                x.computerChangeBoard(boardKeeper.board, maxCombo[1], maxCombo[2])
                computerPlayer.addPoints(maxCombo[0])
                x.changeScore(computerPlayer.points, False)
                computerPlayer.playFromHand(maxCombo[1])
                removedLetters = letterBag.removeLetters(len(maxCombo[1]))
                x.changeLetterBagSize(len(letterBag.letterBag))
                computerPlayer.addToHand(removedLetters)
                data.message1 = "Skor: " + str(maxCombo[0]) + ", Kullanilan Harfler: " + str(maxCombo[1])
            else:
                x.data.message1 = 'AI pas geçti.'
            x.data.message2 = "Herhangi bir yere tikla."
            x.data.computerTurn = False
            x.data.humanTurn = False

            if len(computerPlayer.letterHand) == 0:
                x.data.endOfGame == True

        elif x.data.humanTurn:
            occupied = set(boardKeeper.refreshOccupied())
            attachments = set(boardKeeper.refreshAttachments())

            x.mousePressed(event)

            if x.data.searchOn:
                x.data.searchOn = False
                e = Entry()
                e.pack()
                e.delete(0, END)
                e.insert(0, "a default value")

            elif x.data.switchTurn:
                x.data.switchTurn = False
                x.returnTemporaryLetters()

            elif x.data.passTurn:
                x.data.passTurn = False
                x.returnTemporaryLetters()
                x.data.humanTurn = False
                x.data.computerTurn = True

            elif x.data.playTurn:
                x.data.playTurn = False
                humanCheck.changeLetterHand(humanPlayer.letterHand)
                spaces = sorted(x.data.temporaryBoardLocations)
                letters = []
                newDict = {}
                for (location, character) in zip(x.data.temporaryBoardLocations, x.data.temporaryBoardLetters):
                    newDict[location] = character
                for space in spaces:
                    letters.append(newDict[space])

                if len(letters) != len(spaces):
                    x.data.message1 = ''
                    spaces = []
                    letters = []
                elif not areValidLetters(letters):
                    x.data.message1 = ''
                    letters = ['$']
                elif not areValidLocations(spaces):
                    x.data.message1 = ''
                    spaces = []
                else:
                    locations = []
                    for space in spaces:
                        locations.append(int(space))
                    spaces = locations
                    x.data.message1 = 'Yerler ve harfler doğru. '

                # human check, enters word check
                returnedCombos = humanCheck.comboWorks(letters, spaces, boardKeeper.board, occupied, attachments, dictionary)
                x.data.message1 += returnedCombos[2]
                if returnedCombos[0]:
                    # check
                    workingCombos = [[letters, spaces, returnedCombos[1]]]
                    maxCombo = maxComboValue(workingCombos, boardKeeper.board)
                    x.refreshSpecialTiles(tripleWord, doubleWord, doubleLetter, tripleLetter)
                    score = maxCombo[0]
                    lettersPlayed = maxCombo[1]
                    combos = maxCombo[2]
                    x.data.message2 = '' #'Combo score: ' + str(score) + ', Letters played: ' + str(lettersPlayed)
                    x.data.message3 = 'Herhangi bir yere tikla.'
                    boardKeeper.changeBoard(lettersPlayed, combos)
                    humanPlayer.addPoints(score)
                    x.changeScore(humanPlayer.points, True)
                    humanPlayer.playFromHand(lettersPlayed)
                    removedLetters = letterBag.removeLetters(len(lettersPlayed))
                    humanPlayer.addToHand(removedLetters)
                    x.changeLetterHand(humanPlayer.letterHand)
                    x.changeLetterBagSize(len(letterBag.letterBag))
                    x.resetHand(humanPlayer.letterHand)
                    x.humanChangeBoard(boardKeeper.board)
                    x.resetData()
                    x.data.humanTurn = False
                    x.data.computerTurn = True

                    if len(humanPlayer.letterHand) == 0:
                        x.data.endOfGame == True
                else:
                    x.data.message2 = "Yanlis hamle. Tekrar deneyin."

        else:
            x.data.message1 = "Sira sizde..."
            x.data.message2 = ''
            x.data.humanTurn = True
            x.data.computerTurn = False

        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        x.keyPressed(event)
        redrawAllWrapper(canvas, data)

    # Initialize data
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.endOfGame = False
    x = dataStorage(data)
    x.refreshSpecialTiles(tripleWord, doubleWord, doubleLetter, tripleLetter)
    # creates hands for both players
    removedLetters = letterBag.removeLetters(7)
    humanPlayer.addToHand(removedLetters)
    x.data.letterHand = humanPlayer.letterHand

    x.data.computerLetterHand = computerPlayer.letterHand

    removedLetters = letterBag.removeLetters(7)
    computerPlayer.addToHand(removedLetters)
    # initialize size of letterbag in datastorage
    x.changeLetterBagSize(len(letterBag.letterBag))
    # create the root and the canvas
    root = Tk()
    frame = Frame(root)
    canvas = Canvas(root, width=x.data.width, height=x.data.height)
    canvas.pack()
    # set up events
    redrawAllWrapper(canvas, x.data)
    root.bind("<Button-1>", lambda event: mousePressedWrapper(event, canvas, x.data))
    root.bind("<Key>", lambda event: keyPressedWrapper(event, canvas, x.data))
    # and launch the app
    while not x.data.endOfGame:
        root.mainloop()

run(1000, 600)

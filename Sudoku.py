
"""
****************************************************************************************************

                            ----Sudoku Board Creation Algorithm----

****************************************************************************************************

Purpose:
    An algorithm for generating a valid Sudoku board but doing so in such a way that seeks to 
    create a "new" board every time by invoking many random calls along the process of the algorithm.
    This is done for gameplay purposes, as the final applications will allow the users to play Sudoku,
    but also give them procedurally generated boards each time they start a new game. The goal was to 
    never have the same board twice. 

    I wrote this algrorithm for use in portfolio projects after finding inerest in the challenge while
    self-teaching concepts of recursion and backtracking, hoping to make a mobile game and a website 
    where players can play different levels of Sudoku. Code for the algorithm was completed in July 2020, 
    and my last relevant CS course was Programming Fundamentals II in spring 2020

Sudoku terms used in documentaion:
    Squares - The individual tiles which contain the numbers
    Boxes - The 9 'larger squares' in the Sudoku game, wherein only numbers 1 through 9 can exist with no
    repeats
    Rows/Columns - Only numbers 1 throguh 9 can exist in each row and column, with no repeats

The Algorithm:

    Step 1.) - Create an Empty Board
    A 9 by 9 numpy is created of all zeroes. A successful placement of numbers will overide all of the zeroes
    however, if the semi-random placement of values fails, some methods will place zeroes if the logic of the 
    board is 'corrupt' (overlapping values in rows/columns/boxes) and will indicate to other methods that the 
    program must backtrack. A valid board will have no zeroes, and all values will be placed so that a game of
    Sudoku can be played. 

    Step 2.) Place the First Box
    The method first_box() randomly chooses values 1 - 9 and places them in the top left box of the board

    Step 3.) Try to fill the rest of the boxes with valid numbers, except for the last box
        The alogrithm will step through the boxes of the board from left to right and then top to bottom. 
        self.corners describes the top left square in each box. Steps 4 and 5 describe the process of determining
        a valid box. The method make_puzzle() handles this process and will recurse on the first 8 boxes if one of
        them fails to be valid after 50 attempts at scrambling the box. However, once it approaches the final, bottom
        right box, for the board to be valid there can only be one possible placement of values in the box. If this is not
        the case, the first box must be reset/reseeded as handled in sudoku_array()

    Step 4.) (For boxes 2-8) Validate each square in the box
        The method validate_square() will check the possible numbers that can be placed in the given box by comparing the 
        existing numbers in the square's row and column, as well as popping a value from a stack with integers 1- 9 for each
        box. This way, it determines which values are possible for a square to have and if there are no possible numbers to be
        placed, the box is invalid. Once each square is validated, the algrorithm will choose a random number from the remaining
        stack of valid numbers for each square.

    Step 5.) (For boxes 2-8) Place valid boxes
        There is the possibility that the random number from a square's valid numbers will corrupt the box before a valid 9 numbers
        can be placed. Since this is the case, the place_box() method will place zeroes if a square is invalid and will return false
        upon the method's completion if this is the case. This method's caller, make_puzzle() will allow place_box() to be attempted
        50 times in the hope of achieving a valid box, after this many attempts however, the board is corrupt and make_puzzle() will
        recursively call itself and re-seed the entire board since a new first box will be generated and each consecutive box will be
        placed according to steps 4 and 5

    Step 6.) The final box
        If boxes 2 - 8 are placed, the nature of the Sudoku game then dictates that each square in the final bottom-right box
        can have only 1 unique valid number. Even if the previous boxes were valid, there is still the possibility that this last box
        will reveal a corrupt board. Depending on the randomness of the board, this can overstack if recursion is implemented. (Python
        documentation does not recommend recursive stacks above 1000) So the method sudoku_array() will loop infinitely calling 
        make_puzzle() until it achieves a valid final box (and thus a valid board). Again, the algroithm will place zeroes to indicate
        to other methods that the board is corrupt.

    Step 7.) Hide the numbers
        Based on the player's difficulty, the algorithm will hide numbers so a game can be played. It is not entirely random though,
        as it will definitely reveal squares in each box, row, and column so that the board is playable on harder difficulties. Note:
        Once the board is hidden, it is possible to achieve a valid board that does not match the board that the algorithm generated.
        As long as the player follows the "one rule" of Sudoku, they still win.

"""

import numpy as np
import random as rand
from Puzzle import Puzzle


class Sudoku(Puzzle):

    def __init__(self, diff = None, name = None, creator = None, subject = None):

        super().__init__(name, creator, subject)
        self.difficulty = diff
        self.puzzle = np.zeros((9,9), dtype=np.int)
        self.corners = [
            (0, 3), (0, 6), (3, 0), (3, 3), (3, 6), (6, 0), (6, 3)
        ]

        #logic in constructor allows the creation of a new board upon instantiation of a new object 
        # (if difficulty parameter is provided)
        if self.difficulty != None:
            self.puzzle = self.sudoku_array()
            self.hide_numbers()

    def first_box(self):

        nums = [i for i in range(1,10)]     #stack of numbers 1 - 9
        for i in range(0, 3):
            for j in range(0, 3):
                #sets a square to a randomly popped value from the stack
                self.puzzle[i, j] = nums.pop(rand.randint(0, len(nums)-1))

    def place_box(self, corner):

        nums = [i for i in range(1,10)]
        placed = []
        for i in range(0, 3):
            for j in range(0, 3):

                row = i + corner[0]
                col = j + corner[1]

                #makes the list of valid numbers for each square, then chooses a number at random from this list
                valid_nums = self.validate_square(row, col)
                num = self.place_square(valid_nums, nums)

                #sets the number, it may be overwritten if place_box() is called again
                self.puzzle[row, col] = num

                #checks if the number has already been placed due to bad randomness or a corrupt board
                #pops the stack if it has a place, adds a 0 otherwise to show corruption
                if num in nums:
                    placed.append(num)
                    nums.remove(num)
                else:
                    placed.append(0)

        #checks for zeroes to determine corruption
        if 0 in placed:
            return False
        else:
            return True

    def validate_square(self, row, col):

        #starts with a full stack
        valid_nums = [i for i in range(1,10)]
        taken_row = []
        taken_col = []

        #removes numbers from the stack that already exist in the row
        for r in range(0, col):
            taken_row.append(self.puzzle[row, r])
        for tr in taken_row:
            if tr in valid_nums:
                valid_nums.remove(tr)

        #removes numbers from the stack that already exist in the column
        for c in range(0, row):
            taken_col.append(self.puzzle[c, col])
        for tc in taken_col:
            if tc in valid_nums:
                valid_nums.remove(tc)

        #returns a list that contains numbers remaining in the stack
        return valid_nums

    #place_square() receives two parameters, all valid numbers that are not contain in that square's row or column
    # and a list of remaining numbers in the individual box
    def place_square(self, valid, nbank):

        rand.shuffle(valid)
        bank = nbank

        #finds a number that is valid in rows/columns/boxes by comparing lists. Otherwise returns a 0 to show corruption
        for vn in valid:
            for itm in bank:
                if vn == itm:
                    return vn
        return 0

    #internal function to make the board, NTE recursive
    def make_puzzle(self):

        self.first_box()    #places the first box

        #attempts to place boxes 2-8 
        for cor in self.corners:
            count = 0
            while True:

                #place_box() returns a boolean while also altering the puzzle instance variable
                #it will return false if there is a 0, meaning that box is not necessarily corrupt,
                #but will need to be randomly generated again in an attempt to be valid 
                box = self.place_box(cor)
                if box:
                    break
                count += 1

                #however, make_puzzle() will only allow fifty possible retries before it determines that the box
                # is corrupt and cannot be valid. The recursive call happens at this point.
                if count > 50:
                    self.make_puzzle()

        #The last box is the hardest to get right, and only one possible combination will be possible if the previous
        # boxes were placed validly, because of that, no stack is used here as validate_square should only return a single
        # number in its list, if this is not the case a 0 will be placed revealing corruption and will be handled in the 
        # sudoku_array() function 
        for i in range(6, 9):
            for j in range(6, 9):
                square = self.validate_square(i, j)
                if len(square) == 1:
                    self.puzzle[i, j] = square[0]
                else:
                    self.puzzle[i, j] = 0
        return self.puzzle

    # used in sudoku_array() as a way to provide a final check that there are no zeroes on the board (a valid sudoku game)
    def validate_puzzle(self, puzzle):

        for i in range(0, 9):
            for j in range(0, 9):
                if puzzle[i, j] == 0:
                    return False
        return True

    #wrapper function for make_puzzle(), it usually takes 5 - 15 attempts of make_puzzle() before a valid board is generated
    def sudoku_array(self):

        puz = self.make_puzzle()
        while True:

            #checks if the board is valid and returns the board if so
            if self.validate_puzzle(puz):
                return puz

            #otherwise calls make_puzzle() infinitely until a board is found
            else:
                puz = self.make_puzzle()

    #After a valid board is generated, numbers will be hidden based on the player's chosen difficulty
    def hide_numbers(self):

        # revealed is a list of tuples containing coordinates for numbers that will be shown
        revealed = []

        #reveals at least one number per box so that the game is playable even if there is a bad random seed
        revealed.append((rand.randint(0, 2), rand.randint(0, 2)))
        revealed.append((rand.randint(6, 8), rand.randint(6, 8)))
        for cor in self.corners:
            row = cor[0] + rand.randint(0, 2)
            col = cor[1] + rand.randint(0, 2)
            revealed.append((row, col))

        #now reveals at least one additional number per row for the same reason
        count = 0
        while count < 9:
            square = (count, rand.randint(0, 8))
            if square not in revealed:
                revealed.append(square)
                count += 1

        difficulty = 0
        count = 0

        #determines how many more squares will be revealed based on the difficulty
        if self.difficulty == 1:
            difficulty = 7
        if self.difficulty == 2:
            difficulty = 14
        if self.difficulty == 3:
            difficulty = 23
        if self.difficulty == 4:
            difficulty = 42
        if self.difficulty == 5:
            difficulty = 60

        #chooses new coordinates randomly, but always unique ones
        while count < difficulty:
            square = (rand.randint(0, 8), rand.randint(0, 8))
            if square not in revealed:
                revealed.append(square)
                count += 1

        #sets all revealed coordinates on the board to 0, so that GUIs can use zeroes as empty squares
        for i in range(0, 9):
            for j in range(0, 9):
                idx = (i, j)
                if idx not in revealed:
                    self.puzzle[i, j] = 0

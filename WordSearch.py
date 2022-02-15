"""
************************************************************************************************************************************
*
*                                           -- Word Search Creation Algorithm --
*
************************************************************************************************************************************
*
*  Purpose: Create a solvable word-search puzzle with the given list of words. Meant to be part of a backend puzzle API for a 
*           Portfolio Project. Completed 6/15/20
*
*  The Algorithm:
*       Step 1: Setup the puzzle
*       Determines the longest word of the word-set and assigns the width and height of the puzzle based on this value (so that the
*       longest word could fit vertically or horizontally) along with a size multiplier based on the difficulty of the puzzle. Then,
*       assign random ascii values for the entire puzzle so that the words are 'hidden' once they're placed.
*
*       Step 2: Determine the next word's placement. 
*       Words can be placed vertically, horizontally, diagonally up, or diagonally down and either in standard left-to-right order
*       or reversed. The place_word() function will randomly choose one of these orientations and ensure that the word is placement
*       is in bounds
*
*       Step 3: Validate the placement
*       After the placement of a word is chosen, validate_word() will check for collisions with already placed words. The only valid
*       collision is when the character at the collision point is the same for both words (crossing words). hide_word() runs a finite
*       loop of randomly choosing a placement and checking if it is valid. If a word cannot be placed after the iterations, the puzzle
*       will return a failure, otherwise the parent scramble() function will alter the character matrix to display the hidden word
*
*       Step 4: Attempt new scambles if a placement failed
*       Depending on the random nature of the placements, one failed word does not mean that the entire word set cannot be scrambled.
*       The scramble() function will recurse until a valid word-search is created.
*
************************************************************************************************************************************
"""

import numpy as np
import random as r

from Puzzle import Puzzle

class WordSearch(Puzzle):

    def __init__(self, word_bank = None, diff = None,
        name = None, creator = None, subject = None):

        super().__init__(name, creator, subject)

        self.difficulty = diff
        self.word_bank = word_bank
        self.word_bank.sort(key=len)
        self.word_bank.reverse()
        self.reserved = []
        self.puz_size = 20
        self.long = 0
        self.puzzle = np.random.randint(ord('A'), ord('Z'),
            size = (self.puz_size, self.puz_size))

        if self.word_bank != None:
            self.long = self.longest_string(self.word_bank)
            if self.difficulty != None:
                self.puz_size = int(len(word_bank)*(1.25+(self.difficulty/4)))
                if self.puz_size < self.long:
                    self.puz_size = self.long
                self.puzzle = self.scramble()

    #chooses a starting position and orientation for a word,
    #then simulates its indeces for validation, returns list of tuples
    """
    *********************************************************************************************
    *
    *                               -- place_word() --
    *
    *   Purpose: Determine the starting position, orientation and coordinates of a placed-word attempt
    *   Parameters: warr -> list of ascii values based on a given word
    *   Return Values: List of coordinates on the puzzle where the attempt will be placed and the
    *   ascii value of that position (the letter)
    *
    *   Operation: Randomly chooses an orientation and in-bounds starting position, then maps
    *   the coordinates of where the word will be placed into the returned list
    *
    *********************************************************************************************
    """
    def place_word(self, warr):

        ori = r.randint(1, 8)

        # horizontal, left to right
        if ori == 1:
            row = r.randint(0, self.puz_size-1)
            col = r.randint(0, self.puz_size-len(warr))
            check = []
            for i, v in enumerate(warr):
                check.append((row, col+i, v))
            return check

        #horizontal, right to left
        if ori == 2:
            row = r.randint(0, self.puz_size-1)
            col = r.randint(len(warr)-1, self.puz_size-1)
            check = []
            for i, v in enumerate(warr):
                check.append((row, col-i, v))
            return check

        #vertical, top to bottom
        if ori == 3:
            row = r.randint(0, self.puz_size-len(warr))
            col = r.randint(0, self.puz_size-1)
            check = []
            for i, v in enumerate(warr):
                check.append((row+i, col, v))
            return check

        #vertical, bottom to top
        if ori == 4:
            row = r.randint(len(warr)-1, self.puz_size-1)
            col = r.randint(0, self.puz_size-1)
            check = []
            for i, v in enumerate(warr):
                check.append((row-i, col, v))
            return check

        #diagonal down(\), left to right
        if ori == 5:
            row = r.randint(0, self.puz_size-len(warr))
            col = r.randint(0, self.puz_size-len(warr))
            check = []
            for i, v in enumerate(warr):
                check.append((row+i, col+i, v))
            return check

        #diagonal down(\), right to left
        if ori == 6:
            row = r.randint(len(warr)-1, self.puz_size-1)
            col = r.randint(len(warr)-1, self.puz_size-1)
            check = []
            for i, v in enumerate(warr):
                check.append((row-i, col-i, v))
            return check

        #diagonal up(/), left to right
        if ori == 7:
            row = r.randint(len(warr)-1, self.puz_size-1)
            col = r.randint(0, self.puz_size-len(warr))
            check = []
            for i, v in enumerate(warr):
                check.append((row-i, col+i, v))
            return check

        #diagonal up(/), right to left
        if ori == 8:
            row = r.randint(0, self.puz_size-len(warr))
            col = r.randint(len(warr)-1, self.puz_size-1)
            check = []
            for i, v in enumerate(warr):
                check.append((row+i, col-i, v))
            return check

    """
    *********************************************************************************************
    *
    *                               -- validate() --
    *
    *   Purpose: Determines if a chosen word placement will collide with existing placements
    *   Parameters: check -> List of coordinates and ascii values to check 
    *   Return Values: False for failed collision, True otherwise
    *
    *   Operation: Loops through check list and determines if any coordinate collides with an
    *   already placed position stored in the reserved class var. If there is a collision, determines
    *   if it is valid (same character in that coordinate)
    *
    *********************************************************************************************
    """
    def validate(self, check):

        #compares the check vs all placed values
        for i, v in enumerate(check):
            for j, r in enumerate(self.reserved):

                #coordinates match, but characters/ascii values do not
                if v[0]==r[0] and v[1]==r[1]:
                    if v[2] != r[2]:
                        return False
        return True

    """
    *********************************************************************************************
    *
    *                               -- hide_word() --
    *
    *   Purpose: Makes all the attempts for a word to be hidden in wrapper function
    *   Parameters: warr -> Pass the word array list of ascii values
    *   Return Values: actual positions of valid coordinates and the ascii values
    *
    *   Operation: Loops 300 times in an attempt for a random word placement to be successful
    *
    *********************************************************************************************
    """
    def hide_word(self, warr):

        for n in range(0, 300):
            check = self.place_word(warr)
            if self.validate(check):
                return check
        return []

    """
    *********************************************************************************************
    *
    *                               -- scramble() --
    *
    *   Purpose: Core algorithm/driver function. 
    *   Parameters: None
    *   Return Values: Completed Puzzle
    *
    *   Operation: Sets up the puzzle, then loops through the word bank and attempts to place each
    *   word. If there is a valid placement, adds the coordinates to the reserved list for comparison.
    *   If the placement fails, function recurses. After successfull placement of all of the word
    *   bank, alters the actual puzzle with reserved list coordinates and values.
    *
    *********************************************************************************************
    """
    def scramble(self):

        #randomizes the puzzle with random values
        puzzle = np.random.randint(ord('A'), ord('Z'),
            size = (self.puz_size, self.puz_size))

        for word in self.word_bank:

            #checks if the word can be hidden
            check = self.hide_word(self.word_array(word))
            if check:

                #adds the word to the reserved list
                for i in check:
                    self.reserved.append(i)
            else:
                #resets the algortithm and recurses
                self.reserved.clear()
                self.scramble()

        #set puzzle values
        for j, v in enumerate(self.reserved):
            puzzle[v[0], v[1]] = v[2]

        return puzzle

    #String method
    def __str__(self, puzzle = None):
        output = ""
        if puzzle == None:
            puzzle = self.puzzle
        for i in range(0, self.puz_size):
            output += "\n"
            for j in range(0, self.puz_size):
                output += chr(puzzle[i, j]) + "  "
        return output

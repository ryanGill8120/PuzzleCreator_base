"""
**************************************************************************************************************************************
*
*                                           -- Simple Crossword Creation Algorithm --
*
**************************************************************************************************************************************
*
*  Purpose: Creates a simple crossword (one where words do not directly border) to allow a user of the puzzle API to create a 
*  crossword using an equally sized bank of words and questions. Completed 8/15/20
*
*  The Algorithm:
*  Step 1: Setup the puzzle
*  The main setup involves determining the size of the puzzle, which will be a square. It will always be at least 1.5 times the
*  size of the largest word in the word bank, or 1.8 times the size of the word bank itself. This keeps the time to create the 
*  puzzle manageable
* 
*  Step 2: Place the first word
*  The algorithm orders the word bank in descending order of word lengths to give the greatest chance of another word having an 
*  intersection.
*  
*  Step 3: Find valid intersections of possible next word positions
*  Being a crossword puzzle, all words must match a character of a crossing. The algorithm will find all possible intersections of
*  already placed words and check if the placements of these intersections are in bounds
*
*  Step 4: Check for collision or border failures
*  Before an attempted placement can be written, it must check for collisions with other words. And, if a collision occurs, it is
*  only a valid placement if the character at the collisions are the same. Also, since this is not a true crossword puzzle where 
*  nearly every square is filled, non-colliding words can never touch each other, or border, the algorithm must check this in the
*  placement too and only mark it as valid if it does not touch.
* 
*  Step 5: Repeat and recurse as necessary
*  The algorithm will try the above steps until the word bank is empty and every word is placed. It will skip words if they do not
*  have a placement and try the next if one is available. However, the algorithm will fail if no more words can be placed. Due to 
*  the randomicity of the algorithm, this does not mean that the word bank is invalid, and it will recurse up to a set number of 
*  trys attempting to make a valid puzzle.
*
**************************************************************************************************************************************
"""
import numpy as np
import random as r
from Puzzle import Puzzle

class Crossword(Puzzle):

    def __init__(self, word_bank = None, questions = None,
        name = None, creator = None, subject = None):

        super().__init__(name, creator, subject)
        self.questions = questions
        self.word_bank = word_bank
        self.word_bank.sort(key=len)
        self.word_bank.reverse()
        self.reserved = []
        self.skipped = []
        self.trys = 0
        if self.word_bank:
            self.puz_size = int(len(self.word_bank) * 1.8)
            ls = self.longest_string(self.word_bank)
            if self.puz_size < ls:
                self.puz_size = int(ls * 1.5)
            self.puzzle = np.zeros(
                (self.puz_size, self.puz_size), dtype=np.int
            )
            self.make_puzzle()


    #places the first word horizontally and near the middle
    def first_word(self, word):

        warr = self.word_array(word)
        row = r.randint((self.puz_size//4), self.puz_size-(self.puz_size//4))
        col = r.randint(0, self.puz_size-len(warr))
        check = []
        for i, v in enumerate(warr):
            check.append((row, col+i, v))
        self.reserved.append(check)
        for i in check:
            self.puzzle[i[0], i[1]] = i[2]

    #checks if the word is horizontal
    def is_horizontal(self, check):
        if check[0][0] == check[1][0]:
            return True
        else:
            return False

    #finds the intersections of a word compared to those already
    #placed on the puzzle, returns a list of tuples containing starting
    #coordinates and orientation of possible word placements
    #(row, col, orientation)
    """
    *********************************************************************************************
    *
    *                               -- find_intersections() --
    *
    *   Purpose: Determine if a given word has intersections with already placed words. Additionally,
    *   checks if the word at the intersection is in bounds
    *   Parameters: word - the word to check
    *   Return Values: List of tuples containing the coordinates and orientation of the intersection
    *
    *   Operation: Loops through all characters in the words that have been placed and compares them
    *   to the characters of the parameter word. Also checks the placement of the word against the
    *   boundaries of the puzzle
    *
    *********************************************************************************************
    """
    def find_intersections(self, word):

        intersections = []
        word1 = self.word_array(word)
        for check in self.reserved:
            for i, v in enumerate(check):
                for j, val in enumerate(word1):
                    if v[2]==val:

                        #horizontal 
                        if self.is_horizontal(check):
                            row = v[0]-j
                            if row >=0 and row <= self.puz_size:

                                #boundary checking
                                if v[1]>0:
                                    left = self.puzzle[row, v[1]-1]
                                    if left == 0:
                                        intersections.append((row, v[1], 1))
                                if v[1]+len(word1) < self.puz_size-1:
                                    right = self.puzzle[row, v[1]+len(word1)]
                                    if right == 0:
                                        intersections.append((row, v[1], 1))

                        #vertical
                        else:
                            col = v[1]-j
                            if col >=0 and col <= self.puz_size:
                                if v[0]>0:
                                    top = self.puzzle[v[0]-1, col]
                                    if top == 0:
                                        intersections.append((v[0], col, 0))
                                if v[0]+len(word1) < self.puz_size-1:
                                    bot = self.puzzle[v[0]+len(word1), col]
                                    if bot == 0:
                                        intersections.append((v[0], col, 0))

        return intersections

    """
    *********************************************************************************************
    *
    *                               -- catch_overlap() --
    *
    *   Purpose: Determine if a given word borders another in-line, that is they would form a 
    *   seemingly too long word on the puzzle without whitespace
    *   Parameters: word - word to be checked
    *   Return Values: Boolean of whether the word placement is valid
    *
    *   Operation: Compares the first and last characters of a word against already placed words
    *   The only collision allowed is when one is if they are not the same orientation, otherwise
    *   the placement is invalid
    *
    *********************************************************************************************
    """
    def catch_overlap(self, check):
        for t in check:
            for word in self.reserved:
                for tup in word:
                    if t[0] == tup[0] and t[1] == tup[1]:
                        if t[2] != tup[2]:
                            return False
        for word in self.reserved:
            first = word[0]
            last = word[-1]

            #horizontal
            if self.is_horizontal(check):
                for tp in check:
                    if tp[0] > 0:
                        top = tp[0]-1
                        if top == first[0] and tp[1]==first[1]:
                            return False
                        if top == last[0] and tp[1] == last[1]:
                            return False
                    if tp[0] < (self.puz_size-1):
                        bot = tp[0]+1
                        if bot == first[0] and tp[1]==first[1]:
                            return False
                        if bot == last[0] and tp[1] == last[1]:
                            return False
            
            #vertical
            else:
                for tp in check:
                    if tp[1] > 0:
                        left = tp[1]-1
                        if left == first[1] and tp[0]==first[0]:
                            return False
                        if left == last[1] and tp[0]==last[0]:
                            return False
                    if tp[1] < (self.puz_size-1):
                        right = tp[1]+1
                        if right == first[1] and tp[0]==first[0]:
                            return False
                        if right == last[1] and tp[0]==last[0]:
                            return False
        return True

    """
    *********************************************************************************************
    *
    *                               -- check_surroundings() --
    *
    *   Purpose: Catches bordering of words, they cannot be touching unless there is a valid 
    *   collision
    *   Parameters: word - word to be checked
    *   Return Values: Boolean of whether the word placement is valid
    *
    *   Operation: Loops through the check word and compares neighboring rows/columns and checks
    *   if a word exists in that space
    *
    *********************************************************************************************
    """
    def check_surroundings(self, check):

        if self.is_horizontal(check):
            row = check[0][0]
            leftS = check[0][1]-1
            rightS = check[-1][1]+1
            if leftS < 0 or rightS > self.puz_size-1:
                return False
            if self.puzzle[row, leftS] != 0 or self.puzzle[row, rightS] != 0:
                return False
            for i in range(1, len(check)):
                if row > 0:
                    above = row-1
                    tl_square = self.puzzle[above, check[i-1][1]]
                    tr_square = self.puzzle[above, check[i][1]]
                    if tl_square != 0 and tr_square != 0:
                        return False
                if row < self.puz_size-1:
                    below = row + 1
                    bl_square = self.puzzle[below, check[i-1][1]]
                    br_square = self.puzzle[below, check[i][1]]
                    if bl_square != 0  and br_square != 0:
                        return False
        else:
            col = check[0][1]
            topS = check[0][0]-1
            botS = check[-1][0]+1
            if topS < 0 or botS > self.puz_size-1:
                return False
            if self.puzzle[topS, col] != 0 or self.puzzle[botS, col] != 0:
                return False
            for j in range(1, len(check)):
                if col>0:
                    left = col - 1
                    lt_square = self.puzzle[check[j-1][0], left]
                    lb_square = self.puzzle[check[j][0], left]
                    if lt_square != 0 and lb_square != 0:
                        return False

                if col < self.puz_size-1:
                    right = col + 1
                    rt_square = self.puzzle[check[j-1][0], right]
                    rb_square = self.puzzle[check[j][0], right]
                    if rt_square != 0 and rb_square != 0:
                        return False
        return True

    """
    *********************************************************************************************
    *
    *                               -- validate_word() --
    *
    *   Purpose: Parent function for checking a word that handles the randomization of inputs for
    *   different puzzle creations as well as calling all the validity functions
    *   Parameters: word - word to be checked
    *   Return Values: list of ascii characters to be placed if the placement is valid, otherwise
    *   an empty list (false)
    *
    *   Operation: Checks if intersections exist, then randomizes them. Then calls the validity 
    *   functions to see if the placement is valid. Once one is found, returns the placement
    *
    *********************************************************************************************
    """
    def validate_word(self, word):

        intersections = self.find_intersections(word)
        if not intersections:
            return []
        warr = self.word_array(word)
        r.shuffle(intersections)
        for i in intersections:
            if i[2] == 0:
                check = [(i[0], i[1]+j, warr[j]) for j in range(0, len(warr))]
            else:
                check = [(i[0]+k, i[1], warr[k]) for k in range(0, len(warr))]
            if self.catch_overlap(check):
                if self.check_surroundings(check):
                    return check
        return []

    """
    *********************************************************************************************
    *
    *                               -- make_puzzle() --
    *
    *   Purpose: Core function that creates the puzzle using the other helper functions
    *   Parameters: none
    *   Return Values: Boolean of whether the puzzle creation was successful
    *
    *   Operation: Sets up the puzzle and word bank, then loops through attempting to validate words,
    *   any that cannot be placed are appended to the skipped list, where they will get another
    *   chance to be placed. If word placements fail, the algorithm recurses up to a set number
    *   of times and returns true if a puzzle is created within these trys, returns false otherwise 
    *
    *********************************************************************************************
    """
    def make_puzzle(self):

        self.puzzle = np.zeros((self.puz_size, self.puz_size), dtype=np.int)
        self.first_word(self.word_bank[0])
        for i in range(1, len(self.word_bank)):
            word = self.word_bank[i]
            check = self.validate_word(word)
            if check:
                self.reserved.append(check)
                for c in check:
                    self.puzzle[c[0], c[1]] = c[2]
            else:
                self.skipped.append(word)
        for word in self.skipped:
            check = self.validate_word(word)
            if check:
                self.reserved.append(check)
                for c in check:
                    self.puzzle[c[0], c[1]] = c[2]
            else:
                self.trys += 1
                if self.trys > 200:
                    return False
                else:
                    self.reserved.clear()
                    self.skipped.clear()
                    self.make_puzzle()
        return True

    def __str__(self):
        output = ""
        for i in range(0, self.puz_size):
            output += "\n"
            for j in range(0, self.puz_size):
                square = self.puzzle[j, i]
                if square > 0:
                    output += chr(square) + "  "
                else:
                    output += "   "
        return output

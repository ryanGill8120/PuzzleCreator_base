


"""
    *********************************************************************************************
    *
    *                               -- Puzzle() --
    *
    *   Purpose: Parent class for all puzzles
    *
    *   Operation: Contains functions used by multiple puzzles
    *
    *********************************************************************************************
    """


import numpy as np
class Puzzle:

    def __init__(self, name = None, creator = None, subject = None):

        self.name = name
        self.creator = creator
        self.subject = subject

    #takes a string and converts into a numpy array of ASCII values
    def word_array(self, word):
        return np.array([ord(c) for c in word.upper()])

    def longest_string(self, list):
        long = 0
        for w in list:
            if len(w) > long:
                long = len(w)
        return long

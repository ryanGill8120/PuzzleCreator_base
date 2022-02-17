
"""
*************************************************************************************************************************************
*
*                                                   -- Maze Creation Algrorithm --
*
*************************************************************************************************************************************
*
*  Purpose: Create a playable maze that will always have a solvable path, but be challenging in that there will be many
*           branches that will mislead the solver while also not allowing overlapping or alternate paths
*
*  Completed on 1/22/22 for the purpose of adding to a full puzzle API and as a resume project
*
*  The Algorithm:
*
*      Step 1: Initialize the maze
*      The maze will always be an odd number in height by an odd number in width, with the borders at the edges closed. 
*      This is represented on a 2d matrix with various number representing different parts of the maze, 1s being for walls
*      To allow space and generate a maze where any path is always 1 cell wide, specific cells will always be chosen as walls
*      in a specific patern that allow later pathing functions to follow the rules above.
*
*      Step 2: Create the actual starting path
*      Letting the algorithm branch on its own might result in a maze-like structure with no way for the player to traverse the
*      maze successfully, so a true path must be made. Using the max-steps specified, the starting_path() function will randomly
*      select a starting point and then attempt to make the path. Since the directions of the 'steps' are determined randomly 
*      each iteration, there is a possibility that the path could get stuck by coiling in on itelf or navigating to a corner,
*      so each iteartion checks if there is a step available using check_steps(). The maze and path will reset if no steps are 
*      available and then attempt the path again. Once a successful path has been made, a entry point and exit point will be visible
*      on the outer walls of the maze
*
*      Step 3: Create the branches of the maze
*      The branches are the misleading paths of the maze that do not lead to the exit point. They are created much in the same way
*      as the starting path, using check_steps() to determine if a path is available and trying to step at the size of the max-step
*      each iteration, decrementing the step size in hopes of finding a path. However, the branches try to go as far as they can until
*      no further paths are available in order to make a complicated maze. Two sets of points are used to achieve a full maze, one of 
*      source points where a new step can be taken from, and another of all remaining possible points a path could reach in the maze
*      matrix. The goal of the branching method is to run until the set of remaining set of points is empty, but each time a succesful
*      step is taken, one more source point will be added to the respective set wherefrom a new step can be taken. Steps will prefer
*      using the last step of a successful branch as a source.
*       
**************************************************************************************************************************************
"""

import numpy as np
import random as rand
import json
from Puzzle import Puzzle

class Maze(Puzzle):

    def __init__(self, name=None, creator=None, subject=None, height=None, width=None, steps=None):
        super().__init__(name, creator, subject)

        #initialized values are defaults
        self.width = 25
        self.height = 25
        self.MAX_STEPS = 2
        self.starting_pos
        self.last_pos
        self.remaining = set()
        self.sources = set()
        self.maze
        self.maze_json = None

        # constructor logic that will handle instantiation errors
        #height and width must always be odd integers
        if width:
            if width % 2 == 0:
                width += 1
            self.width = width

        if height:
            if height % 2 ==0:
                height += 1
            self.height = height

        if steps:
            if steps > 4:
                steps = 4
            self.MAX_STEPS = steps

        #makes a maze on instantiation
        self.create_maze()
        self.maze_json = json.dumps(self.maze.tolist())
        
    #setup function that makes a clear maze for further alteration
    def init_maze(self):

        #numpy setup of 2d array
        puz = np.zeros((self.height, self.width), dtype=np.int)

        #makes the outer walls
        for i in range(self.width):
            puz[0, i] = 1
            puz[self.height-1, i] = 1

        for i in range(1, self.height-1):
            puz[i, 0] = 1
            puz[i, self.width-1] = 1

        #makes the internal unreachable points, these will never be accessible by a branch or path
        for i in range(1, self.height//2):
            for j in range(1, self.width//2):
                puz[i*2, j*2] = 1

        return puz

    """
    *********************************************************************************************
    *
    *                               -- starting_path() --
    *
    *   Purpose: Create a definite path that will allow for a solvable maze
    *   Parameters: None
    *   Return Values: None
    *
    *   Operation: First selects a random starting point on the left side of the maze, then tries
    *   to 'step' in a random direction based on the MAX_STEP value. Uses check_step() to determine
    *   if this step is valid. If it is, sets value on the maze array to indicate the starting path.
    *   If it is not valid, attempts a lower step size. If a lower step size fails, the path is stuck
    *   and must be restarted, at which point the method resets the maze with init_maze() and tries 
    *   again. Continues until a step reaches the right-most non-wall column of the maze.
    *
    *********************************************************************************************
    """
    def starting_path(self):

        #initialize an empty maze array
        self.maze = self.init_maze()
        step_size = self.MAX_STEPS      #first initialization of step_size var

        #chooses a random starting position on the left side of the maze and alters maze array accordingly
        start = rand.randint(0, (self.height//2 - 1))*2 + 1    
        self.maze[start, 0] = 2
        self.maze[start, 1] = 2
        self.starting_pos = (start, 0)
        current_pos = (start, 1)    #this variable is essentially the LCV

        #continue until coordinate tuple is on the rightmost non-wall position
        while current_pos[1] != self.width - 2:

            #reset of vars on each iteration
            path_available = False
            step_size = self.MAX_STEPS

            #tries every stepsize
            while step_size > 0:

                valid_dirs, dir_names = self.check_steps(current_pos, step_size)

                #check_steps was successful, a step is possible
                if valid_dirs:
                    path_available = True
                    break

                #check_steps not successful, try a lower step size
                step_size -= 1

            #at least the smallest step exists
            if path_available:

                #choose a random direction for step
                rand_index = rand.randint(0, len(valid_dirs) - 1)
                rand_place = valid_dirs[rand_index]
                rand_dir = dir_names[rand_index]

                #alters the maze based on the chosen direction
                if rand_dir == "above":
                    for n in range(step_size * 2):
                        self.maze[rand_place[-1][0] + n, rand_place[-1][1]] = 2
                elif rand_dir == "right":
                    for n in range(step_size * 2):
                        self.maze[rand_place[-1][0], rand_place[-1][1] - n] = 2
                elif rand_dir == "below":
                    for n in range(step_size * 2):
                        self.maze[rand_place[-1][0] - n, rand_place[-1][1]] = 2
                elif rand_dir == "left":
                    for n in range(step_size * 2):
                        self.maze[rand_place[-1][0], rand_place[-1][1] + n] = 2

                #saves last point filled
                current_pos = rand_place[-1]

            #no paths available, reset the maze
            else:
                current_pos = (start, 1)
                self.maze = self.init_maze()
                self.maze[start, 0] = 2
                self.maze[start, 1] = 2

        #saves last position to class and makes the exit
        self.last_pos = current_pos
        self.maze[current_pos[0], current_pos[1] + 1] = 2

    """
    *********************************************************************************************
    *
    *                               -- make_branches() --
    *
    *   Purpose: Create the misleading paths off of the actual path
    *   Parameters: None
    *   Return Values: None
    *
    *   Operation: Similar to the function of the starting_path() function, but fills all remaining
    *   points of the maze with paths that begin from the actual path or from an existing branch, 
    *   will typically prefer sourcing from the end of the last step made in a branch, if possible.
    *   Maintains two sets of points, remaining and sources, sources will grow as new branches are 
    *   added (begins with the sources from the main path) and remaining will shrink as spaces are
    *   filled in. The function's loop ends when all spaces are filled, and it will try smaller and
    *   smaller step sizes on all possible sources until a valid position is found
    *
    *********************************************************************************************
    """
    def make_branches(self):

        step_size = self.MAX_STEPS
        # pass through the matrix and determine if a position is open (remaining) or already filled (a source)
        i, j = 1, 1
        while i < self.height:
            while j < self.width:
                if self.maze[i, j] == 0:
                    self.remaining.add((i, j))
                else:
                    self.sources.add((i,j))
                j += 2
            j = 1
            i += 2
       
        prefer = None   #var to hold the prefered source (the last coordinate place in a branch, makes a more difficult maze)
        removals = []   #cannot remove items of a set during iteration, they will be stored here when found and removed later   

        while self.remaining:
            
            path_available = False
            prefer_available = False

            #flow for continiuing a branch because the prefer var is set
            if prefer:

                #tries lower and lower step sizes to find a possible step
                while step_size > 0:

                    #call to check_steps to see if a step is possible or if the source is 'stuck'
                    valid_dirs, dir_names = self.check_steps(prefer, step_size)
                    if valid_dirs:
                        prefer_available = True
                        break
                    else:
                        step_size -= 1

            # the above code failed, there was not a step from the prefered point
            if not prefer_available:

                #remove that prefered point from sources for efficiency and reset step size for new try
                if prefer:
                    self.sources.remove(prefer)
                step_size = self.MAX_STEPS
                while step_size > 0:

                    removals.clear()
                    #now loop through sources set to find a new valid step source
                    for s in self.sources:
                        valid_dirs, dir_names = self.check_steps(s, step_size)

                        #exit loop if a valid step is found
                        if valid_dirs:
                            path_available = True
                            break

                        #otherwise mark that point for removal if smallest step size is tried
                        elif step_size == 1:
                            removals.append(s)
                    
                    #remove dead sources
                    for rem in removals:
                        self.sources.remove(rem)

                    #exit loop if a step exists
                    if path_available:
                        break

                    #otherwise try a smaller step size
                    else:
                        step_size -= 1
                
            #one kind of path exists
            if path_available or prefer_available:

                #randomly choose one of the valid directions to travel
                rand_index = rand.randint(0, len(valid_dirs) - 1)
                rand_place = valid_dirs[rand_index]
                rand_dir = dir_names[rand_index]

                #alter the maze based on the direction
                if rand_dir == "above":
                    for n in range(step_size * 2):
                        self.maze[rand_place[-1][0] + n, rand_place[-1][1]] = 3
                elif rand_dir == "right":
                    for n in range(step_size * 2):
                        self.maze[rand_place[-1][0], rand_place[-1][1] - n] = 3
                elif rand_dir == "below":
                    for n in range(step_size * 2):
                        self.maze[rand_place[-1][0] - n, rand_place[-1][1]] = 3
                elif rand_dir == "left":
                    for n in range(step_size * 2):
                        self.maze[rand_place[-1][0], rand_place[-1][1] + n] = 3

                #set the prefer point to the last point filled
                prefer = rand_place[-1]

                #add new branch points to sources and remove the points from remaining
                for r in rand_place:
                    self.remaining.remove(r)
                    self.sources.add(r)
                #reset step size
                step_size = self.MAX_STEPS

            #error condition (loop should end when condition checks for empty remaining, this check prevents infinite loop in error)
            else:
                break
    """
    *********************************************************************************************
    *
    *                               -- check_steps() --
    *
    *   Purpose: Determine if a given coordinate has a valid step from its position
    *   Parameters: coord (Tuple representing the coordinate (i, j))
    *               step_size (the size of the step to check)
    *   Return Values: If successful --> valid_dirs, dir_names 
    *                                   (list of ending coordinates, list of those direction's names)
    *                  If failed --> False, False
    *
    *   Operation: Determines all possible directions' coordinates mathematically, then checks
    *   these coordinates against the maze to determine if they are out of bounds or collide with a
    *   wall or an existing path. Then returns lists of valid coordinate endings and the directions
    *
    *********************************************************************************************
    """
    def check_steps(self, coord, step_size):

        valid_dirs = []
        dir_names = []
        above = []
        right = []
        below = []
        left = []

        #create mathematical coordinates for all directions
        for i in range(1, step_size + 1):
            above.append((coord[0] - (2 * i), coord[1]))
            right.append((coord[0], coord[1] + (2 * i)))
            below.append((coord[0] + (2 * i), coord[1]))
            left.append((coord[0], coord[1] - (2 * i)))

        above_valid = True
        right_valid = True
        below_valid = True
        left_valid = True

        # check for out of bounds and collisions for all coordinates
        for tup in above:
            if tup[0] < 1 or self.maze[tup[0], tup[1]] != 0:
                above_valid = False
                break

        for tup in right:
            if tup[1] >= self.width or self.maze[tup[0], tup[1]] != 0:
                right_valid = False
                break

        for tup in below:
            if tup[0] >= self.height or self.maze[tup[0], tup[1]] != 0:
                below_valid = False
                break

        for tup in left:
            if tup[1] < 1 or self.maze[tup[0], tup[1]] != 0:
                left_valid = False
                break

        #add valid direction data to their respective list
        if above_valid:
            valid_dirs.append(above)
            dir_names.append("above")
        if right_valid:
            valid_dirs.append(right)
            dir_names.append("right")
        if below_valid:
            valid_dirs.append(below)
            dir_names.append("below")
        if left_valid:
            valid_dirs.append(left)
            dir_names.append("left")

        #return lists if they exist
        if valid_dirs:
            return valid_dirs, dir_names

        #otherwise return 2 Falses
        return False, False

    #simplifies creation of the maze into one call
    def create_maze(self):
        self.starting_path()
        self.make_branches()
    
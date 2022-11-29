#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 11:22:03 2022

@author: ignasi
"""
import copy

import time
import chess
import numpy as np
import sys
import queue
from typing import List

RawStateType = List[List[List[int]]]

from itertools import permutations


class Aichess():
    """
    A class to represent the game of chess.

    ...

    Attributes:
    -----------
    chess : Chess
        represents the chess game

    Methods:
    --------
    startGame(pos:stup) -> None
        Promotes a pawn that has reached the other side to another, or the same, piece

    """

    def __init__(self, TA, myinit=True):

        if myinit:
            self.chess = chess.Chess(TA, True)
        else:
            self.chess = chess.Chess([], False)

        self.listNextStates = []
        self.listVisitedStates = []
        self.pathToTarget = []
        self.currentStateW = self.chess.boardSim.currentStateW;
        self.depthMax = 8;
        self.checkMate = False

    def getCurrentState(self):

        return self.myCurrentStateW

    def getListNextStatesW(self, myState):

        self.chess.boardSim.getListNextStatesW(myState)
        self.listNextStates = self.chess.boardSim.listNextStates.copy()

        return self.listNextStates

    def isSameState(self, a, b):

        isSameState1 = True
        # a and b are lists
        for k in range(len(a)):

            if a[k] not in b:
                isSameState1 = False

        isSameState2 = True
        # a and b are lists
        for k in range(len(b)):

            if b[k] not in a:
                isSameState2 = False

        isSameState = isSameState1 and isSameState2
        return isSameState

    def isVisited(self, mystate):

        if (len(self.listVisitedStates) > 0):
            perm_state = list(permutations(mystate))

            isVisited = False
            for j in range(len(perm_state)):

                for k in range(len(self.listVisitedStates)):

                    if self.isSameState(list(perm_state[j]), self.listVisitedStates[k]):
                        isVisited = True

            return isVisited
        else:
            return False

    def isCheckMate(self, mystate):

        if (mystate[0][0] == 0) and (mystate[1][1] == 4) and (mystate[1][0] == 2):
            return True
                    
        return False
    
    # Cast a tuple of two tuples into a list of two lists
    def tupleToList(self, tuple):
        return [list(tuple[0]), list(tuple[1])]

    # Specific check to sort the state pair and ensure that the rook is before the king
    def orderComprovation(self, state):
        if state[0][2]==6:
            state2 = []
            state2.append(state[1])
            state2.append(state[0])
            state = state2
        return state

    # Returns the heuristic used in the Best First Search, which is the manhattan distance between both nodes
    def BFSHeuristic(self, actual):
        distanceR = 0
        R = actual[0]
        K = actual[1]
        if R[0] != 0 and R[1] == 4:
            distanceR = 2
        elif R[0] != 0 and R[1] != 4:
            distanceR = 1
        distanceK = abs(2-K[1]) + abs(4-K[0])        
        return distanceR + distanceK

    # Returns the heuristic used in the A*
    def AStarHeuristic(self, actual, depth):
        return self.BFSHeuristic(actual) + depth


    def DepthFirstSearch(self, currentState, depth):
        # 'startState' is the initial state of the boxes
        startState = currentState

        """
        Initialize the data structures needed to perform the scan
        1. 'border' is the list of borders where we can expand the route
        2. Two dictionaries that will help to recover the work on the frontiers.
           2.1 'boards' saves the tables (value) in the form of value in each border (key)
           2.2 'current' stores a tuple with two elements (value), this tuple has the previous state and its respective depth (key)
        3. 'visited' saves states that have already been visited
        4. 'path' is the list where will save the path to the target (pathToTarget)

        Note: All lists used in dictionaries will be cast to tuples because a tuple is a 'hasheable' element and can be stored in a dictionary
        """
        frontera = [currentState]
        boards = {}
        current = {}
        path = []
        visited = []
        currentTuple = (tuple(currentState[0]), tuple(currentState[1]))

        # Save a deepcopy of the table as a value in the current state used as a key in 'boards'
        boards[currentTuple] = copy.deepcopy(aichess.chess.boardSim)
        j=0

        while frontera:
            # Extract the last element from the frontiers list, as done in a LIFO stack
            currentState = frontera.pop()
            currentTuple = (tuple(currentState[0]), tuple(currentState[1]))

            # Assign to the current table the value of the current state of the table dictionary
            aichess.chess.boardSim = boards[currentTuple]

            if j>0: # It's not the first iteration
                # Save the previous state and the depth of the current state used as key
                aux = current[currentTuple]
                previousState = aux[0]
                actual_depth = aux[1]
            else:
                # Set the depth to 0 and the previous state as the current because it's the first iteration
                actual_depth = 0
                previousState = currentState
            j = j+1

            # Move the table to advance the search
            aichess.chess.moveSim(previousState[0],currentState[0])
            aichess.chess.moveSim(previousState[1], currentState[1])

            # Check if it's in a checkmate position
            if(self.isCheckMate(currentState)):
                # If it's affirmative, perform a loop to build the path by performing 'backtracking' and building it with the help of the 'previous' dictionary
               path.append(self.tupleToList(currentTuple))
               while self.tupleToList(currentTuple) != startState:
                  aux = current[currentTuple]
                  currentState = aux[0]
                  currentTuple = (tuple(currentState[0]), tuple(currentState[1]))
                  path.append(self.tupleToList(currentTuple))

               # Finally save the path in the attribute of the 'pathToTarget' class and exit the algorithm, the algorithm has found the solution
               aichess.pathToTarget = path[len(path):0:-1]
               aichess.listVisitedStates = visited
               return False

           # If we are not in a checkmate position, we loop to visit all the next states of the current one
            for i in aichess.getListNextStatesW(currentState):
                i = self.orderComprovation(i)
                # We check if the state has not been visited yet, the rook or king is not repeated (possible code errors) and we have not reached the maximum allowed depth
                if (i not in visited) and i[0][2]!=i[1][2] and (i[0][0]!=i[1][0] or i[0][1]!=i[1][1]) and actual_depth < depth:
                    # Add the current state of the iteration in the visited and frontier list, now it's another frontier
                    visited.append(i), frontera.append(i)
                    # Save the state as a tuple
                    currentTuple = (tuple(i[0]), tuple(i[1]))
                    # Save a copy of the current table (value) with the current state of the iteration (key) in the 'boards' dictionary for later use
                    boards[currentTuple] = copy.deepcopy(aichess.chess.boardSim)
                    # Assign to an auxiliary variable a tuple with the current state of the iteration and the current depth incremented by 1
                    aux = (currentState, actual_depth + 1)
                    # Save the auxiliary variable (value) with the current state in the form of a tuple (key) in the dictionary 'current'
                    current[currentTuple] = aux
        return False
 
    def BreadthFirstSearch(self, currentState):
        # 'startState' is the initial state of the boxes
        startState = currentState

        """
        Initialize the data structures needed to perform the scan
        1. 'border' is the list of borders where we can expand the route
        2. Two dictionaries that will help to recover the work on the frontiers.
           2.1 'boards' saves the tables (value) in the form of value in each border (key)
           2.2 'current' stores the previous state
        3. 'visited' saves states that have already been visited
        4. 'path' is the list where will save the path to the target (pathToTarget)

        Note: All lists used in dictionaries will be cast to tuples because a tuple is a 'hasheable' element and can be stored in a dictionary
        """
        frontera = [currentState]
        boards = {}
        current = {}
        visited = []
        path = []
        currentTuple = (tuple(currentState[0]), tuple(currentState[1]))

        # Save a deepcopy of the table as a value in the current state used as a key in 'boards'
        boards[currentTuple] = copy.deepcopy(aichess.chess.boardSim)
        j=0

        while frontera:
            # Extract the first element from the frontiers list, as done in a FIFO queue
            currentState = frontera[0]
            frontera.remove(currentState)
            currentTuple = (tuple(currentState[0]), tuple(currentState[1]))

            # Assign to the current table the value of the current state of the table dictionary
            aichess.chess.boardSim = boards[currentTuple]

            if j>0: # It's not the first iteration
                # Save the previous state and the depth of the current state used as key
                aux = current[currentTuple]
                previousState = aux[0]
                actual_depth = aux[1]
            else:
                # Set the previous state as the current because it's the first iteration
                previousState = currentState
                actual_depth = 0
            j = j+1

            # Move the table to advance the search
            aichess.chess.moveSim(previousState[0],currentState[0])
            aichess.chess.moveSim(previousState[1], currentState[1])

            # Check if it's in a checkmate position
            if(self.isCheckMate(currentState)):
                # If it's affirmative, perform a loop to build the path by performing 'backtracking' and building it with the help of the 'previous' dictionary
               path.append(self.tupleToList(currentTuple))
               while self.tupleToList(currentTuple) != startState:
                  aux = current[currentTuple]
                  currentState = aux[0]
                  currentTuple = (tuple(currentState[0]), tuple(currentState[1]))
                  path.append(self.tupleToList(currentTuple))

               # Finally save the path in the attribute of the 'pathToTarget' class and exit the algorithm, the algorithm has found the solution
               aichess.pathToTarget = path[len(path):0:-1]
               aichess.listVisitedStates = visited
               return False

           # If we are not in a checkmate position, we loop to visit all the next states of the current one
            for i in aichess.getListNextStatesW(currentState):
                i = self.orderComprovation(i)
                # We check if the state has not been visited yet, the rook or king is not repeated (possible code errors) and we have not reached the maximum allowed depth
                if (i not in visited) and i[0][2]!=i[1][2] and (i[0][0]!=i[1][0] or i[0][1]!=i[1][1]):
                    # Add the current state of the iteration in the visited and frontier list, now it's another frontier
                    visited.append(i), frontera.append(i)
                    # Save the state as a tuple
                    currentTuple = (tuple(i[0]), tuple(i[1]))
                    # Save a copy of the current table (value) with the current state of the iteration (key) in the 'boards' dictionary for later use
                    boards[currentTuple] = copy.deepcopy(aichess.chess.boardSim)
                    # Assign to an auxiliary variable a tuple with the current state of the iteration and the current depth incremented by 1
                    aux = (currentState, actual_depth + 1)
                    # Save the auxiliary variable (value) with the current state in the form of a tuple (key) in the dictionary 'current'
                    current[currentTuple] = aux
        return False

    def BestFirstSearch(self, currentState):
            
        # 'startState' is the initial state of the boxes
        startState = currentState

        """
        Initialize the data structures needed to perform the scan
        1. 'frontera' is a priority queue of frontiers where we can expand the route according to the implemented heuristics
        2. Two dictionaries that will help to recover the work on the frontiers.
           2.1 'boards' saves the tables (value) in the form of value in each border (key)
           2.2 'current' stores the previous state
        3. 'visited' saves states that have already been visited
        4. 'path' is the list where will save the path to the target (pathToTarget)

        Note: All lists used in dictionaries will be cast to tuples because a tuple is a 'hasheable' element and can be stored in a dictionary
        """
        frontera = queue.PriorityQueue()
        frontera.put((self.BFSHeuristic(currentState), currentState))
        boards = {}
        current = {}
        visited = []
        path = []
        currentTuple = (tuple(currentState[0]), tuple(currentState[1]))

        # Save a deepcopy of the table as a value in the current state used as a key in 'boards'
        boards[currentTuple] = copy.deepcopy(aichess.chess.boardSim)
        j=0

        while frontera:
            # Extract the element with a minor heuristic
            auxTuple = frontera.get()
            currentState = auxTuple[1]
            currentTuple = (tuple(currentState[0]), tuple(currentState[1]))

            # Assign to the current table the value of the current state of the table dictionary
            aichess.chess.boardSim = boards[currentTuple]

            if j>0: # It's not the first iteration
                # Save the previous state and the depth of the current state used as key
                aux = current[currentTuple]
                previousState = aux[0]
                actual_depth = aux[1]
            else:
                # Set the previous state as the current because it's the first iteration
                previousState = currentState
                actual_depth = 0
            j = j+1

            # Move the table to advance the search
            aichess.chess.moveSim(previousState[0],currentState[0])
            aichess.chess.moveSim(previousState[1], currentState[1])

            # Check if it's in a checkmate position
            if(self.isCheckMate(currentState)):
                # If it's affirmative, perform a loop to build the path by performing 'backtracking' and building it with the help of the 'previous' dictionary
               path.append(self.tupleToList(currentTuple))
               while self.tupleToList(currentTuple) != startState:
                  aux = current[currentTuple]
                  currentState = aux[0]
                  currentTuple = (tuple(currentState[0]), tuple(currentState[1]))
                  path.append(self.tupleToList(currentTuple))

               # Finally save the path in the attribute of the 'pathToTarget' class and exit the algorithm, the algorithm has found the solution
               aichess.pathToTarget = path[len(path):0:-1]
               aichess.listVisitedStates = visited
               return False

           # If we are not in a checkmate position, we loop to visit all the next states of the current one
            for i in aichess.getListNextStatesW(currentState):
                i = self.orderComprovation(i)
                # We check if the state has not been visited yet, the rook or king is not repeated (possible code errors) and we have not reached the maximum allowed depth
                if (i not in visited) and i[0][2]!=i[1][2] and (i[0][0]!=i[1][0] or i[0][1]!=i[1][1]):
                    # Add the current state of the iteration in the visited and frontier list, now it's another frontier
                    visited.append(i), frontera.put((self.BFSHeuristic(i), i))
                    # Save the state as a tuple
                    currentTuple = (tuple(i[0]), tuple(i[1]))
                    # Save a copy of the current table (value) with the current state of the iteration (key) in the 'boards' dictionary for later use
                    boards[currentTuple] = copy.deepcopy(aichess.chess.boardSim)
                    # Assign to an auxiliary variable a tuple with the current state of the iteration and the current depth incremented by 1
                    aux = (currentState, actual_depth + 1)
                    # Save the auxiliary variable (value) with the current state in the form of a tuple (key) in the dictionary 'current'
                    current[currentTuple] = aux
        return False
              
    def AStarSearch(self, currentState):
            
        # 'startState' is the initial state of the boxes
        startState = currentState

        """
        Initialize the data structures needed to perform the scan
        1. 'frontera' is a priority queue of frontiers where we can expand the route according to the implemented heuristics
        2. Two dictionaries that will help to recover the work on the frontiers.
           2.1 'boards' saves the tables (value) in the form of value in each border (key)
           2.2 'current' stores the previous state
        3. 'visited' saves states that have already been visited
        4. 'path' is the list where will save the path to the target (pathToTarget)

        Note: All lists used in dictionaries will be cast to tuples because a tuple is a 'hasheable' element and can be stored in a dictionary
        """
        frontera = queue.PriorityQueue()
        frontera.put((self.BFSHeuristic(currentState), currentState))
        boards = {}
        current = {}
        visited = []
        path = []
        currentTuple = (tuple(currentState[0]), tuple(currentState[1]))

        # Save a deepcopy of the table as a value in the current state used as a key in 'boards'
        boards[currentTuple] = copy.deepcopy(aichess.chess.boardSim)
        j=0

        while frontera:
            # Extract the element with a minor heuristic
            auxTuple = frontera.get()
            currentState = auxTuple[1]
            currentTuple = (tuple(currentState[0]), tuple(currentState[1]))

            # Assign to the current table the value of the current state of the table dictionary
            aichess.chess.boardSim = boards[currentTuple]

            if j>0: # It's not the first iteration
                # Save the previous state and the depth of the current state used as key
                aux = current[currentTuple]
                previousState = aux[0]
                actual_depth = aux[1]
            else:
                # Set the depth to 0 and the previous state as the current because it's the first iteration
                actual_depth = 0
                previousState = currentState
            j = j+1

            # Move the table to advance the search
            aichess.chess.moveSim(previousState[0],currentState[0])
            aichess.chess.moveSim(previousState[1], currentState[1])

            # Check if it's in a checkmate position
            if(self.isCheckMate(currentState)):
                # If it's affirmative, perform a loop to build the path by performing 'backtracking' and building it with the help of the 'previous' dictionary
               path.append(self.tupleToList(currentTuple))
               while self.tupleToList(currentTuple) != startState:
                  aux = current[currentTuple]
                  currentState = aux[0]
                  currentTuple = (tuple(currentState[0]), tuple(currentState[1]))
                  path.append(self.tupleToList(currentTuple))

               # Finally save the path in the attribute of the 'pathToTarget' class and exit the algorithm, the algorithm has found the solution
               aichess.pathToTarget = path[len(path):0:-1]
               aichess.listVisitedStates = visited
               return False

           # If we are not in a checkmate position, we loop to visit all the next states of the current one
            for i in aichess.getListNextStatesW(currentState):
                i = self.orderComprovation(i)
                # We check if the state has not been visited yet, the rook or king is not repeated (possible code errors) and we have not reached the maximum allowed depth
                if (i not in visited) and i[0][2]!=i[1][2] and (i[0][0]!=i[1][0] or i[0][1]!=i[1][1]):
                    # Add the current state of the iteration in the visited and frontier list, now it's another frontier
                    visited.append(i), frontera.put((self.AStarHeuristic(i, actual_depth), i))
                    # Save the state as a tuple
                    currentTuple = (tuple(i[0]), tuple(i[1]))
                    # Save a copy of the current table (value) with the current state of the iteration (key) in the 'boards' dictionary for later use
                    boards[currentTuple] = copy.deepcopy(aichess.chess.boardSim)
                    # Assign to an auxiliary variable a tuple with the current state of the iteration and the current depth incremented by 1
                    aux = (currentState, actual_depth + 1)
                    # Save the auxiliary variable (value) with the current state in the form of a tuple (key) in the dictionary 'current'
                    current[currentTuple] = aux
        return False

    def heuristics():
        return False        

def translate(s):
    """
    Translates traditional board coordinates of chess into list indices
    """

    try:
        row = int(s[0])
        col = s[1]
        if row < 1 or row > 8:
            print(s[0] + "is not in the range from 1 - 8")
            return None
        if col < 'a' or col > 'h':
            print(s[1] + "is not in the range from a - h")
            return None
        dict = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        return (8 - row, dict[col])
    except:
        print(s + "is not in the format '[number][letter]'")
        return None


if __name__ == "__main__":
    start = time.time()
    #   if len(sys.argv) < 2:
    #       sys.exit(usage())

    # intiialize board
    TA = np.zeros((8, 8))
    # white pieces
    # TA[0][0] = 2
    # TA[2][4] = 6
    # # black pieces
    # TA[0][4] = 12

    TA[7][0] = 2
    TA[7][7] = 6
    TA[0][4] = 12

    # initialise board
    print("stating AI chess... ")
    aichess = Aichess(TA, True)
    currentState = aichess.chess.board.currentStateW.copy()
    print("printing board")
    aichess.chess.boardSim.print_board()

    # get list of next states for current state
    print("current State", currentState)

    # it uses board to get them... careful 
    aichess.getListNextStatesW(currentState)
    #   aichess.getListNextStatesW([[7,4,2],[7,4,6]])
    print("list next states ", aichess.listNextStates)

    # starting from current state find the end state (check mate) - recursive function
    # aichess.chess.boardSim.listVisitedStates = []
    # find the shortest path, initial depth 0
    depth = 10
    #aichess.BreadthFirstSearch(currentState)
    #aichess.DepthFirstSearch(currentState, depth)
    #aichess.BestFirstSearch(currentState)
    aichess.AStarSearch(currentState)

#    MovesToMake = ['1e','2e','2e','3e','3e','4d','4d','3c']

#    for k in range(int(len(MovesToMake)/2)):

#         print("k: ",k)

#         print("start: ",MovesToMake[2*k])
#         print("to: ",MovesToMake[2*k+1])

#         start = translate(MovesToMake[2*k])
#         to = translate(MovesToMake[2*k+1])
#
#         print("start: ",start)
#         print("to: ",to)
         
#         aichess.chess.moveSim(start, to)

    end  = time.time()
    ExecTime = end-start
    aichess.chess.boardSim.print_board()
    print("#Move sequence...  ", aichess.pathToTarget)
    print("#Visited sequence...  ", aichess.listVisitedStates)
    print("#Current State...  ", aichess.chess.board.currentStateW)
    print("#Execution time... ", ExecTime, "seconds")

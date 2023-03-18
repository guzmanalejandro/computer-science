#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 11:22:03 2022

@author: ignasi
"""

import random
from typing import List

import numpy as np

import chess

import json
import os

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
        self.currentStateW = self.chess.boardSim.currentStateW
        self.qTable = {}
        self.qTableWhites = {}
        self.qTableBlacks = {}
        self.numVisitedWhites = {}
        self.numVisitedBlacks = {}
        self.errorValue = 0.5
        self.kValue = 0     


    def stateToString(self, whiteState):
        wkState = self.getPieceState(whiteState,6)
        wrState = self.getPieceState(whiteState,2)
        stringState = str(wkState[0])+","+str(wkState[1])+","
        if wrState != None:
            stringState += str(wrState[0])+","+str(wrState[1])

        return stringState

    def stringToState(self, stringWhiteState):
        whiteState = []
        whiteState.append([int(stringWhiteState[0]),int(stringWhiteState[2]),6])
        if len(stringWhiteState) > 4:
            whiteState.append([int(stringWhiteState[4]),int(stringWhiteState[6]),2])

        return whiteState

    def getCurrentStateW(self):

        return self.chess.boardSim.currentStateW

    def getListnextStatesX(self, mypieces):

        if mypieces[0][2] > 6:
            return self.getListNextStatesB(mypieces)
        else:
            return self.getListNextStatesW(mypieces)

    def getListNextStatesW(self, myState):

        self.chess.boardSim.getListNextStatesW(myState)
        self.listNextStates = self.chess.boardSim.listNextStates.copy()

        return self.listNextStates

    def getListNextStatesB(self, myState):
        self.chess.boardSim.getListNextStatesB(myState)
        self.listNextStates = self.chess.boardSim.listNextStates.copy()

        return self.listNextStates

    def newBoardSim(self, listStates):
        # We create a new boardSim
        TA = np.zeros((8, 8))
        for state in listStates:
            TA[state[0]][state[1]] = state[2]

        self.chess.newBoardSim(TA)

    def getPieceState(self, state, piece):
        pieceState = None
        for i in state:
            if i[2] == piece:
                pieceState = i
                break
        return pieceState

    def getCurrentState(self):
        listStates = []
        for i in self.chess.board.currentStateW:
            listStates.append(i)
        for j in self.chess.board.currentStateB:
            listStates.append(j)
        return listStates

    def getNextPositions(self, state):
        # Given a state, we look at the following possible states
        # From these we return a list with the positions, that is, [row, column]
        if state == None:
            return None
        if state[2] > 6:
            nextStates = self.getListNextStatesB([state])
        else:
            nextStates = self.getListNextStatesW([state])
        nextPositions = []
        for i in nextStates:
            nextPositions.append(i[0][0:2])
        return nextPositions

    def getWhiteState(self, currentState):
        whiteState = []
        wkState = self.getPieceState(currentState, 6)
        whiteState.append(wkState)
        wrState = self.getPieceState(currentState, 2)
        if wrState != None:
            whiteState.append(wrState)
        return whiteState

    def getBlackState(self, currentState):
        blackState = []
        bkState = self.getPieceState(currentState, 12)
        blackState.append(bkState)
        brState = self.getPieceState(currentState, 8)
        if brState != None:
            blackState.append(brState)
        return blackState

    def getMovement(self, state, nextState):
        # Given a state and a successor state, we return the position of the moved piece in both states
        pieceState = None
        pieceNextState = None
        for piece in state:
            if piece not in nextState:
                movedPiece = piece[2]
                pieceNext = self.getPieceState(nextState, movedPiece)
                if pieceNext != None:
                    pieceState = piece
                    pieceNextState = pieceNext
                    break

        return [pieceState, pieceNextState]
    
    def makeMovement(self, standard_current_state, standard_next_state):
        start = [e for e in standard_current_state if e not in standard_next_state]
        to = [e for e in standard_next_state if e not in standard_current_state]
        start, to = start[0][0:2], to[0][0:2]
        aichess.chess.moveSim(start, to)
        
    def isCheckMate(self, mystate):
        # Check mate for exercise 1 (the black king is fixed at position [0,4]
        # we put the possible states where check mate occurs
        listCheckMateStates = [[[0,0,2],[2,4,6]],[[0,1,2],[2,4,6]],[[0,2,2],[2,4,6]],[[0,6,2],[2,4,6]],[[0,7,2],[2,4,6]]]

        # We look at all state permutations and see if they match the CheckMates list
        for permState in list(permutations(mystate)):
            if list(permState) in listCheckMateStates:
                return True

        return False

    def isCheckMate_2(self, currentState_Player, currentState_Rival,color):
        # Return 1 checkmate in favor of white pieces
        # Return 2 checkmate in favor of black pieces

        if color:
            if len(currentState_Rival) == 0:
                return 1
            if len(currentState_Rival) == 1 and currentState_Rival[0][2] == 8:
                return 1
        else:
            if len(currentState_Rival) == 0:
                return 2
            if len(currentState_Rival) == 1 and currentState_Rival[0][2] == 2:
                return 2
        return False
    
    def create_position(self,currentState,qlearn,list_moves):
        """
        Args:
            currentState: New state that's not in the Q-Learn table.
            qlearn: Table with Q-Learn values.
        Returns: We seek to create a dictionary for the qlearn of exercise 2 where each state will have a dictionary of the states
        future to which you can reach your score, the reward of the state itself, and the key, which will be the same
        CurrentState.
        """
        sta = str(currentState)
        qlearn[sta] = dict()
        qlearn[sta]['value'] = 0
        qlearn[sta]['bestMove'] = None
        qlearn[sta]['moves'] = dict()
        for move in list_moves:
            if qlearn[sta]['moves'].get(str(move)) == None:  # si la key de move no existe qlearn[sta]['moves'][str(move)] = 0
                qlearn[sta]['moves'][str(move)] = 0

        return qlearn[sta]

    def reward(self, mystate):
        # Reward first exercise
        if self.isCheckMate(mystate):
            return 100
        return -1

    def maxQValue(self, stringState, dictQValues):
        if stringState not in dictQValues.keys():
            return 0
        maxQ = -999999
        dictState = dictQValues[stringState]
        for nextString in dictState.keys():
            maxQ = max(maxQ, dictState[nextString])
        return maxQ

    def epsilonGreedy(self, epsilon, listStates, currentState):
        x = random.uniform(0,1)
        # Exploration with epsilon probability
        if x < epsilon:
            # A random number between zero and the length of the list of states
            n = random.randint(0, len(listStates) - 1)
            nextState = listStates[n]
            nextString = self.stateToString(nextState)
            # State has been visited?
            currentDict = self.qTable[self.stateToString(currentState)]
            if nextString not in currentDict.keys():
                currentDict[nextString] = 0
            return nextState, nextString
        # Exploration with 1-epsilon probabilty
        else:
            listBestStates = []
            maxValue = float('-inf')
            currentDict = self.qTable[self.stateToString(currentState)]
            visitedStatesString = currentDict.keys()
            errorRange = 0.1

            # First loop to find the maximum value
            for state in listStates:
                stateString = self.stateToString(state)
                # If the state has not been visited, we initialize it
                if stateString not in visitedStatesString:
                    currentDict[stateString] = 0
                qValue = currentDict[stateString]

                if qValue > maxValue:
                    maxValue = qValue
            # Second loop to find the best states
            for state in listStates:
                stateString = self.stateToString(state)
                qValue = currentDict[stateString]
                # We evaluate whether the value is within an error margin of the largest value found
                # If yes, we add it to the best possible states
                if qValue >= maxValue - errorRange:
                    listBestStates.append(state)

            n = random.randint(0,len(listBestStates)-1)
            selectedState = listBestStates[n]
            selectedString = self.stateToString(selectedState)
            return selectedState, selectedString

    def Qlearning(self, epsilon, gamma, alpha):
        currentState = self.getCurrentStateW()
        # We transform the state into a string
        currentString = self.stateToString(currentState)
        # Save the initial state of the table
        initialState, initialString = currentState, currentString
        self.qTable[currentString] = {}
        # We fix the range of the error, to see when the Q-table converges
        errorRange = 0.75
        numConvergingPaths = 0
        numIterations = 0

        # When the number of iterations is exceeded, the algorithm will stop.
        while numConvergingPaths < 10:
            numIterations += 1
            checkMate = False
            movementsCheckMate = 0
            error = 0
            while not checkMate:
                # If we haven't visited the state, we add it to the Q-table
                if currentString not in self.qTable.keys():
                    self.qTable[currentString] = {}
                listNextStates = []
                # We save all child states in listNextStates
                for state in self.getListNextStatesW(currentState):
                    if state[0][0:2] != [0,4] and state[1][0:2] != [0,4]:
                        listNextStates.append(state)

                # We choose one of the states through exploration or exploitation
                nextState, nextString = self.epsilonGreedy(epsilon, listNextStates, currentState)
                qValue = self.qTable[currentString][nextString]
                # We get the reward associated with the state nextState
                reward = self.reward(nextState)
                # If we have some checkmate, the Q-Value will already be the reward itself
                if reward != -1:
                    qValue = reward
                else:
                    # We get the value of the sample and the Q-value
                    sample = reward + gamma*self.maxQValue(nextString, self.qTable)
                    # We add up the difference between the real reward and the predicted one
                    error += sample - qValue
                    qValue = (1-alpha)*qValue + alpha*sample
                    movementsCheckMate += 1
                self.qTable[currentString][nextString] = qValue
                if reward == -1:
                    # To the actual position
                    self.newBoardSim(nextState+[[0,4,12]])
                    currentState, currentString = nextState, nextString
                # In case it's checkmate, we finish this iteration of Q-learning.
                else:
                    checkMate = True
            # We calculate the average of the error in order to normalize it and avoid having a large error if there are a large number of moves
            if movementsCheckMate != 0:
                meanError = error/movementsCheckMate
                # If error is in the range (-error, error) this path has converged.
                if meanError < errorRange and meanError > -errorRange:
                    numConvergingPaths += 1
                # If not, reset the counter because there's no convergence in this iteration
                else:
                    numConvergingPaths = 0
            self.newBoardSim(initialState+[[0,4,12]])
            currentState, currentString = initialState, initialString
            # we show the current iteration every 500 iterations, taking into account that it will converge with a large number of iterations
            if numIterations%500 == 0:
                print("Iteration ",numIterations,"with error", error)
        # When the execution is finished, we recover the path that leads us to a greater reward
        self.reconstructPath(initialState)
        print("Total of iterations: ",numIterations)
    
    def QlearningMultiplayer(self, iterations, epsilon, gamma, alpha):

        # Variable that indicates if it's whites or blacks turn
        white = True

        # Initialize the two qLearn tables, one for each piece (black or white)
        qlearnW = {}
        qlearnB = {}

        listW = self.getListnextStatesX(currentStateW)
        listW = self.normalize_list(listW,currentStateW)

        listB = self.getListnextStatesX(currentStateB)
        listB = self.normalize_list(listB, currentStateB)

        # Create the first position of our Q-Learn table
        qlearnW[str(currentStateW + currentStateB )] = self.create_position(currentStateW,qlearnW,listW)
        qlearnB[str(currentStateB + currentStateW)] = self.create_position(currentStateB, qlearnB, listB)
        
        for iteration in range(iterations):
            # Initialize the states of each black and white pieces
            stateW = self.chess.boardSim.currentStateW.copy()
            stateB = self.chess.boardSim.currentStateB.copy()
            chess_temp = copy.deepcopy(self.chess)
            for t in itertools.count():
                if white:
                    listW = self.getListnextStatesX(stateW)
                    next_stateW = self.epsilonGreedy(stateW,listW,qlearnW,epsilon)
                    self.chess.boardSim.print_board()
                    previousW = copy.copy(stateW)
                    # Make the movement
                    self.makeMovement(stateW, next_stateW)
                    self.elimina_piece(next_stateW, stateB)
                    stateW = previousW.copy()
                    # If the state is new in the qLearn table
                    if qlearnW.get(str(next_stateW)) == None:
                        listW = self.getListnextStatesX(next_stateW)
                        qlearnW[str(next_stateW)] = self.create_position(next_stateW,qlearnW,listW)
                    reward = self.reward(next_stateW)
                    qlearnW[str(stateW)]['moves'][str(next_stateW)] = qlearnW[str(next_stateW)]['value']
                    best_next_action = max(qlearnW[str(next_stateW)]['moves'], key=qlearnW[str(next_stateW)]['moves'].get)
                    td_target = reward + discount_factor*(qlearnW[str(next_stateW)]['value']) - qlearnW[str(stateW)]['value']
                    qlearnW[str(stateW)]['value'] = alpha*td_target
                    stateW = next_stateW.copy()
                    stateB = self.chess.boardSim.currentStateB.copy()
                    white = False

                else:
                    listB = self.getListnextStatesX(stateB)
                    next_stateB = self.epsilonGreedy(stateB, listB, qlearnB, epsilon)
                    self.chess.boardSim.print_board()
                    previousB = copy.copy(stateB)
                    # Make the movement
                    self.makeMovement(stateB, next_stateB)
                    self.elimina_piece(next_stateB, stateW)
                    stateB = previousB.copy()
                    # If the state is new in the qLearn table
                    if qlearnB.get(str(next_stateB)) == None:
                        listB = self.getListnextStatesX(next_stateB)
                        qlearnB[str(next_stateB)] = self.create_position(next_stateB, qlearnB, listB)
                    reward = self.reward(next_stateB)
                    qlearnB[str(stateB)]['moves'][str(next_stateB)] = qlearnB[str(next_stateB)]['value']
                    best_next_action = max(qlearnB[str(next_stateB)]['moves'], key=qlearnB[str(next_stateB)]['moves'].get)
                    td_target = reward + discount_factor * (qlearnB[str(next_stateB)]['value']) - qlearnB[str(stateB)]['value']
                    qlearnB[str(stateB)]['value'] = alpha * td_target
                    stateB = next_stateB.copy()
                    stateW = self.chess.boardSim.currentStateW.copy()
                    white = True
            self.chess = copy.deepcopy(chess_temp)
        return qlearnW, qlearnB

    def reconstructPath(self, initialState):
        currentState = initialState
        currentString = self.stateToString(initialState)
        checkMate = False
        self.chess.board.print_board()

        path = [initialState]
        while not checkMate:
            maxQ = -999999
            # Let's initialize the maxState to none and try to find the state that maximize the q-value on the table
            maxState = None
            # Dictionary of the states of the actual state on the Q-Values table
            currentDict = self.qTable[currentString]
            # Let's see which state has the next highest Q-value
            for stateString in currentDict.keys():
                qValue = currentDict[stateString]
                if maxQ < qValue:
                    maxState = stateString
                    maxQ = qValue
            state = self.stringToState(maxState)
            # When we get it we add it to the path
            path.append(state)
            movement = self.getMovement(currentState,state)
            # We make the corresponding move
            self.chess.move(movement[0],movement[1])
            self.chess.board.print_board()
            currentString = maxState
            currentState = state
            # When check mate is achieved, the execution ends
            if self.isCheckMate(state):
                checkMate = True

        print("Path sequence: ",path)


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
    #   if len(sys.argv) < 2:
    #       sys.exit(usage())

    # intiialize board
    TA = np.zeros((8, 8))

    # Initial configuration
    TA[7][0] = 2
    TA[7][4] = 6
    TA[0][7] = 8
    TA[0][4] = 12


    # initialise board
    print("stating AI chess... ")
    aichess = Aichess(TA, True)
    exercise = 1

    if exercise == 1:
        aichess.Qlearning(0.3, 0.9, 0.1)

    if exercise == 2:
        aichess.QlearningMultiplayer(1000, 0.1, 0.9, 0.3)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 11:22:03 2022

@author: ignasi
"""
import copy
import math

import chess
import board
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
        self.listVisitedSituations = []
        self.pathToTarget = []
        self.currentStateW = self.chess.boardSim.currentStateW;
        self.depthMax = 8;
        self.checkMate = False

    def copyState(self, state):
        copyState = []
        for piece in state:
            copyState.append(piece.copy())
        return copyState
    def isVisitedSituation(self, color, mystate):
        if (len(self.listVisitedSituations) > 0):
            perm_state = list(permutations(mystate))

            isVisited = False
            for j in range(len(perm_state)):

                for k in range(len(self.listVisitedSituations)):
                    if self.isSameState(list(perm_state[j]), self.listVisitedSituations.__getitem__(k)[1]) and color == \
                            self.listVisitedSituations.__getitem__(k)[0]:
                        isVisited = True

            return isVisited
        else:
            return False


    def getCurrentStateW(self):

        return self.myCurrentStateW

    # Returns the next state of whites 
    def getListNextStatesW(self, myState):

        self.chess.boardSim.getListNextStatesW(myState)
        self.listNextStates = self.chess.boardSim.listNextStates.copy()

        return self.listNextStates
    
    # Returns the next state of blacks 
    def getListNextStatesB(self, myState):
        self.chess.boardSim.getListNextStatesB(myState)
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

    def black_king_threatened(self, currentState):
        self.newBoardSim(currentState)
        
        black_king_state = None
        white_king_state = None
        black_rook_state = None
        white_rook_state = None

        # Obtain the position of each separate piece
        for i in currentState:
            if i[2] == 12:
                black_king_state = i
                black_king_pos = black_king_state[0:2]
            if i[2] == 6:
                white_king_state = i
            if i[2] == 2:
                white_rook_state = i
            if i[2] == 8:
                black_rook_state = i

        # The black pieces cannot kill the white king
        if white_king_state == None:
            return False
        # Can the white king kill the black king?
        for white_king_pos in self.getNextPositions(white_king_state):
            if black_king_pos == white_king_pos:
                # Checkmate!
                return True
        if white_rook_state != None:
            # Can the white rook kill the black king?
            for wrPosition in self.getNextPositions(white_rook_state):
                if black_king_pos == wrPosition:
                    return True

        return False

    def black_king_movements_threatened(self, currentState):
        # The future states of the black king are threatened by the whites?
        self.newBoardSim(currentState)
        
        black_king_state = None
        white_king_state = None
        black_rook_state = None
        white_rook_state = None
        
        # Pick the black king state
        for i in currentState:
            if i[2] == 12:
                black_king_state = i
        allWatched = False
        # It's important to check if the king is located on a wall, a situation that determines its state of threat
        if black_king_state[0] == 0 or black_king_state[0] == 7 or black_king_state[1] == 0 or black_king_state[1] == 7:
            for i in currentState:
                if i[2] == 2:
                    white_rook_state = i
            whiteState = self.getWhiteState(currentState)
            allWatched = True
            nextBStates = self.getListNextStatesB(self.getBlackState(currentState))

            for state in nextBStates:
                newWhiteState = whiteState.copy()
                # Check if white rook has been eliminated, in case of it remove it from the state
                if white_rook_state != None and white_rook_state[0:2] == state[0][0:2]:
                    newWhiteState.remove(white_rook_state)
                state = state + newWhiteState
                # Move black pieces to the new state
                self.newBoardSim(state)

                # Is the black king threatened or not?
                if not self.black_king_threatened(state):
                    allWatched = False
                    break
        self.newBoardSim(currentState)
        return allWatched

    def black_check_mate(self, currentState):
        # If the black king is threatened and for all of his movements is threatened too, the black king is in check mate!
        if self.black_king_threatened(currentState) and self.black_king_movements_threatened(currentState):
            return True

        return False

    def white_king_threatened(self, currentState):
        # This method check if the white king is threatened by the black pieces
        self.newBoardSim(currentState)

        black_king_state = None
        white_king_state = None
        black_rook_state = None
        white_rook_state = None
        # Obtain the position of each separate piece
        for i in currentState:
            if i[2] == 12:
                black_king_state = i
            if i[2] == 6:
                white_king_state = i
                white_king_pos = white_king_state[0:2]
            if i[2] == 2:
                white_rook_state = i
            if i[2] == 8:
                black_rook_state = i

        # The white pieces cannot kill the black king
        if black_king_state == None:
            return False
        # Can the black king kill the white king?
        for black_king_pos in self.getNextPositions(black_king_state):
            if white_king_pos == black_king_pos:
                # Tindríem un checkMate
                return True
        if black_rook_state != None:
            # Can the black rook kill the white king?
            for black_rook_pos in self.getNextPositions(black_rook_state):
                if white_king_pos == black_rook_pos:
                    return True

        return False

    def white_king_movements_threatened(self, currentState):
        self.newBoardSim(currentState)
        # The future states of the white king are threatened by the blacks?
        # Pick the white king state
        
        black_king_state = None
        white_king_state = None
        black_rook_state = None
        white_rook_state = None
        
        for i in currentState:
            if i[2] == 6:
                white_king_state = i
        allWatched = False
        # It's important to check if the king is located on a wall, a situation that determines its state of threat
        if white_king_state[0] == 0 or white_king_state[0] == 7 or white_king_state[1] == 0 or white_king_state[1] == 7:
            for i in currentState:
                if i[2] == 8:
                    black_rook_state = i
            blackState = self.getBlackState(currentState)
            allWatched = True
            nextWStates = self.getListNextStatesW(self.getWhiteState(currentState))
            for state in nextWStates:
                newBlackState = blackState.copy()
                # Check if black rook has been eliminated, in case of it remove it from the state
                if black_rook_state != None and black_rook_state[0:2] == state[0][0:2]:
                    newBlackState.remove(black_rook_state)
                state = state + newBlackState
                # Move white pieces to the new state
                self.newBoardSim(state)
                # Is the white king threatened or not?
                if not self.white_king_threatened(state):
                    allWatched = False
                    break
        self.newBoardSim(currentState)
        return allWatched

    def white_check_mate(self, currentState):
        # If the white king is threatened and for all of his movements is threatened too, the white king is in check mate!
        if self.white_king_threatened(currentState) and self.white_king_movements_threatened(currentState):
            return True
        return False

    def newBoardSim(self, listStates):
        # Create a new boardSim
        TA = np.zeros((8, 8))
        for state in listStates:
            TA[state[0]][state[1]] = state[2]

        self.chess.newBoardSim(TA)

    def getCurrentState(self):
        # Return the current state of the pieces of the board
        listStates = []
        for i in self.chess.board.currentStateW:
            listStates.append(i)
        for j in self.chess.board.currentStateB:
            listStates.append(j)
        return listStates

    def getNextPositions(self, state):
        # Return the next positions of a determinated state of the pieces of the board
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
        white_king_state = None
        white_rook_state = None
        for i in currentState:
            if i[2] == 6:
                white_king_state = i
        whiteState.append(white_king_state)
        for i in currentState:
            if i[2] == 2:
                white_rook_state = i
        if white_rook_state != None:
            whiteState.append(white_rook_state)
        return whiteState

    def getBlackState(self, currentState):
        blackState = []
        black_king_state = None
        black_rook_state = None
        
        for i in currentState:
            if i[2] == 12:
                black_king_state = i
        blackState.append(black_king_state)
        for i in currentState:
            if i[2] == 8:
                black_rook_state = i
        if black_rook_state != None:
            blackState.append(black_rook_state)
        return blackState

    def getMovement(self, state, nextState):
        # Given a state and a successor state, return the position of the moved piece in both states
        pieceState = None
        pieceNextState = None
        for piece in state:
            if piece not in nextState:
                movedPiece = piece[2]
                for i in nextState:
                    if i[2] == movedPiece:
                        pieceNext = i
                
                if pieceNext != None:
                    pieceState = piece
                    pieceNextState = pieceNext
                    break

        return [pieceState, pieceNextState]

    def evaluate(self, currentState, color):
        # Return the image of the evaluation function implemented on the minimax algorithm
        value = 0
        
        black_king_state = None
        white_king_state = None
        black_rook_state = None
        white_rook_state = None

        for i in currentState:
            if i[2] == 12:
                black_king_state = i
            if i[2] == 6:
                white_king_state = i
            if i[2] == 2:
                white_rook_state = i
            if i[2] == 8:
                black_rook_state = i

        # Get the separated rows and columns of each piece state
        row_black_king = black_king_state[0]
        column_black_king = black_king_state[1]
        row_white_king = white_king_state[0]
        column_white_king = white_king_state[1]

        if white_rook_state != None:
            row_white_wook = white_rook_state[0]
            column_white_rook = white_rook_state[1]
        if black_rook_state != None:
            row_black_rook = black_rook_state[0]
            column_black_rook = black_rook_state[1]

        # Black rook has been eliminated?
        if black_rook_state == None:
            value += 50
            row = abs(row_black_king - row_white_king)
            column = abs(column_white_king - column_black_king)
            kings_distance = min(row, column) + abs(row - column)
            # The kings are separated are not threatened each other and the white rook is not eliminated
            if kings_distance >= 3 and white_rook_state != None:
                # Assign the distance between the rooks as a plus to the value of the evaluation function
                rowR = abs(row_black_king - row_white_wook)
                columnR = abs(column_white_rook - column_black_king)
                value += (min(rowR, columnR) + abs(rowR - columnR))/10
            value += (7 - kings_distance)

        # White rook has been eliminated?
        if white_rook_state == None:
            value += -50
            row = abs(row_black_king - row_white_king)
            column = abs(column_white_king - column_black_king)
            kings_distance = min(row, column) + abs(row - column)

            # The kings are separated are not threatened each other and the black rook is not eliminated
            if kings_distance >= 3 and black_rook_state != None:
                # Assign the distance between the rooks as a plus to the value of the evaluation function
                rowR = abs(row_white_king - row_black_rook)
                columnR = abs(column_black_rook - column_white_king)
                value -= (min(rowR, columnR) + abs(rowR - columnR)) / 10
            value += (-7 + kings_distance)

        # White king is threatened!
        if self.white_king_threatened(currentState):
            value += -20
            
        # Black king is threatened!
        if self.black_king_threatened(currentState):
            value += 20

        # If the evaluation function is for black pieces, the positive values are negative
        if not color:
            value = (-1) * value

        return value

    def minimaxAlgorithm(self, depthWhite,depthBlack):
        currentState = self.getCurrentState()
        # White pieces are in a check mate position?
        if self.white_check_mate(currentState):
            return False
        # Black king is threatened?
        if self.black_king_threatened(currentState):
            return True
        # Copy the current state
        copyState = self.copyState(currentState)
        self.listVisitedSituations.append((False, copyState))
        # We assign to a variable the color of the pieces that will win, but in no one wins, the tie is represented by 'none'
        colorWin = None
        for i in range(50):
            currentState = self.getCurrentState()
            # White pieces turn!
            if i % 2 == 0:
                if not self.minimaxWhite(currentState, depthWhite):
                    break
                if self.black_check_mate(currentState):
                    colorWin = True
                    break
            # Black pieces turn!
            else:
                if not self.minimaxBlack(currentState, depthBlack):
                    break
                if self.white_check_mate(currentState):
                    colorWin = False
                    break

            # Print the board
            self.chess.board.print_board()

        # Print the final board
        self.chess.board.print_board()
        return colorWin

    def minimaxWhite(self, state, depthMax):
        nextState = self.maximumWhites(state, 0, depthMax)
        copyState = self.copyState(nextState)
        if self.isVisitedSituation(True, copyState):
            return False
        self.listVisitedSituations.append((True, copyState))
        # Get the movement of the piece
        movement = self.getMovement(state, nextState)
        # Move the piece with this movement in the board of the match
        self.chess.move(movement[0], movement[1])
        return True

    def maximumWhites(self, currentState, depth, depthMax):
        # Últim moviment ha estat de les negres.
        # Is the white king threatened in all of his movements?
        if self.white_king_movements_threatened(currentState):
            # If white king is threatened now, it's in a check mate position!
            if self.white_king_threatened(currentState):
                return -1000
            # If not, the pieces are in a tie position
            return 0

        if depth == depthMax:
            return self.evaluate(currentState, True)

        # Assign the maximun value as a very negative number
        maximumValue = -99999
        maximumState = None
        whiteState = self.getWhiteState(currentState)
        blackState = self.getBlackState(currentState)
        black_rook_state = None
        for i in currentState:
            if i[2] == 8:
                black_rook_state = i
        for state in self.getListNextStatesW(whiteState):
            newBlackState = blackState.copy()
            # It has removed the black rook? Remove it!
            if black_rook_state != None and black_rook_state[0:2] == state[0][0:2]:
                newBlackState.remove(black_rook_state)
            # Update the state
            state = state + newBlackState
            # Don't analize the movements in which the white king is threatened
            if not self.white_king_threatened(state):
                valueSate = self.minimumWhites(state, depth + 1, depthMax)
                # It's a good state? Update the maximum value and state
                if valueSate > maximumValue:
                    maximumValue = valueSate
                    maximumState = state
        # If it reach the maximum depth, return the state that represents the next white's movement
        if depth == 0:
            return maximumState
        return maximumValue

    def minimumWhites(self, currentState, depth, depthMax):
        # Últim moviment ha estat de les blanques
        # Is the black king threatened in all of his movements?
        if self.black_king_movements_threatened(currentState):
            if self.black_king_threatened(currentState):
                # It's important to arribe to the checkmate position in the less number of possible movements
                return 99999 / depth
            return 0

        if depth == depthMax:
            return self.evaluate(currentState, True)
        blackState = self.getBlackState(currentState)
        whiteState = self.getWhiteState(currentState)
        for i in currentState:
            if i[2] == 2:
                white_rook_state = i

        # Assign the minimum value as a very positive number
        minimumValue = 99999
        for state in self.getListNextStatesB(blackState):
            newWhiteState = whiteState.copy()
            # It has removed the black rook? Remove it!
            if white_rook_state != None and white_rook_state[0:2] == state[0][0:2]:
                newWhiteState.remove(white_rook_state)
            state = state + newWhiteState
            # Don't analize the movements in which the white king is threatened
            if not self.black_king_threatened(state):
                # Update minimum value
                minimumValue = min(minimumValue, self.maximumWhites(state, depth + 1, depthMax))

        return minimumValue

    def minimaxBlack(self, state, depthMax):
        nextState = self.maximumBlacks(state, 0, depthMax)
        copyState = self.copyState(nextState)
        if self.isVisitedSituation(True, copyState):
            return False
        self.listVisitedSituations.append((True, copyState))
        # Get the movement of the piece
        movement = self.getMovement(state, nextState)
        # # Move the piece with this movement in the board of the match
        self.chess.move(movement[0], movement[1])
        return True

    def maximumBlacks(self, currentState, depth, depthMax):
        # Is the black king threatened in all of his movements?
        if self.black_king_movements_threatened(currentState):
            # If black king is threatened now, it's in a check mate position!
            if self.black_king_threatened(currentState):
                return -1000
            return 0

        if depth == depthMax:
            return self.evaluate(currentState, False)

        # Assign the maximun value as a very negative number
        maximumValue = -99999
        maximumState = None
        blackState = self.getBlackState(currentState)
        whiteState = self.getWhiteState(currentState)
        for i in currentState:
            if i[2] == 2:
                white_rook_state = i
        for state in self.getListNextStatesB(blackState):
            newWhiteState = whiteState.copy()
            # It has removed the black rook? Remove it!
            if white_rook_state != None and white_rook_state[0:2] == state[0][0:2]:
                newWhiteState.remove(white_rook_state)
             # Update the state
            state = state + newWhiteState
            # Don't analize the movements in which the white king is threatened
            if not self.black_king_threatened(state):
                valueSate = self.minimumBlacks(state, depth + 1, depthMax)
                # It's a good state? Update the maximum value and state
                if valueSate > maximumValue:
                    maximumValue = valueSate
                    maximumState = state
        # If it reach the maximum depth, return the state that represents the next black's movement
        if depth == 0:
            return maximumState
        return maximumValue

    def minimumBlacks(self, currentState, depth, depthMax):
        # Is the white king threatened in all of his movements?
        if self.white_king_movements_threatened(currentState):
            if self.white_king_threatened(currentState):
                 # It's important to arribe to the checkmate position in the less number of possible movements
                return 99999 / depth
            return 0

        if depth == depthMax:
            return self.evaluate(currentState, False)
        whiteState = self.getWhiteState(currentState)
        blackState = self.getBlackState(currentState)
        black_rook_state = None
        for i in currentState:
            if i[2] == 8:
                black_rook_state = i
        # Assign the minimum value as a very positive number
        minimumValue = 99999
        for state in self.getListNextStatesW(whiteState):
            newBlackState = blackState.copy()
            # It has removed the white rook? Remove it!
            if black_rook_state != None and black_rook_state[0:2] == state[0][0:2]:
                newBlackState.remove(black_rook_state)
            state = state + newBlackState
            # Don't analize the movements in which the white king is threatened
            if not self.white_king_threatened(state):
                # Update minimum value
                minimumValue = min(minimumValue, self.maximumBlacks(state, depth + 1, depthMax))

        return minimumValue

    def alphaBetaPoda(self, depthWhite,depthBlack):
        currentState = self.getCurrentState()
        # White pieces are in a check mate position?
        if self.white_check_mate(currentState):
            # The black pieces won!
            return False
        # Black king is threatened?
        if self.black_king_threatened(currentState):
            # Thw white pieces won!
            return True
        # Copy the current state
        copyState = self.copyState(currentState)
        self.listVisitedSituations.append((False, copyState))
        # We assign to a variable the color of the pieces that will win, but in no one wins, the tie is represented by 'none'
        colorWin = None
        for i in range(50):
            currentState = self.getCurrentState()
            # White pieces turn!
            if i % 2 == 0:
                if not self.podaWhite(currentState, depthWhite):
                    break
                if self.black_check_mate(currentState):
                    colorWin = True
                    break
            # Black pieces turn!
            else:
                if not self.podaBlack(currentState, depthBlack):
                    break
                if self.white_check_mate(currentState):
                    colorWin = False
                    break
            
            # Print the board
            self.chess.board.print_board()
        # Print the final board
        self.chess.board.print_board()
        return colorWin

    def podaWhite(self, state, depthMax):
        # We assign the variable alpha as a very negative number and beta as a very negative number
        alpha = -99999
        beta = 99999
        nextState = self.podaMaxValueWhite(state, 0, depthMax, alpha, beta)
        copyState = self.copyState(nextState)
        if self.isVisitedSituation(True, copyState):
            return False
        self.listVisitedSituations.append((True, copyState))
        # Get the movement of the piece
        movement = self.getMovement(state, nextState)
        # Move the piece with this movement in the board of the match
        self.chess.move(movement[0], movement[1])
        return True

    def podaMaxValueWhite(self, currentState, depth, depthMax, alpha, beta):
        # Últim moviment ha estat de les negres.
        # Is the white king threatened in all of his movements?
        if self.white_king_movements_threatened(currentState):
            # If white king is threatened now, it's in a check mate position!
            if self.white_king_threatened(currentState):
                return -1000
            # If not, the pieces are in a tie position
            return 0
        #If arrive to the maximum depth, calculate the image of the evaluation function for that state
        if depth == depthMax:
            return self.evaluate(currentState, True)

        # Assign the maximun value as a very negative number
        maximumValue = -99999
        maximumState = None
        whiteState = self.getWhiteState(currentState)
        blackState = self.getBlackState(currentState)
        black_rook_state = None
        for i in currentState:
            if i[2] == 8:
                black_rook_state = i
        for state in self.getListNextStatesW(whiteState):
            newBlackState = blackState.copy()
            # It has removed the black rook? Remove it!
            if black_rook_state != None and black_rook_state[0:2] == state[0][0:2]:
                newBlackState.remove(black_rook_state)
            # Update the state
            state = state + newBlackState
            # Don't analize the movements in which the white king is threatened
            if not self.white_king_threatened(state):
                valueSate = self.podaMinValueWhite(state, depth + 1, depthMax, alpha, beta)
                 # It's a good state? Update the maximum value and state
                if valueSate > maximumValue:
                    maximumValue = valueSate
                    maximumState = state
                # Make a prunning in case of fulfill the beta's condition
                if maximumValue >= beta:
                    break
                # Update the alpha's value
                alpha = max(alpha, maximumValue)

        # If it reach the maximum depth, return the state that represents the next white's movement
        if depth == 0:
            return maximumState
        return maximumValue

    def podaMinValueWhite(self, currentState, depth, depthMax, alpha, beta):
        # Últim moviment ha estat de les blanques
        # Is the black king threatened in all of his movements?
        if self.black_king_movements_threatened(currentState):
            if self.black_king_threatened(currentState):
                # It's important to arribe to the checkmate position in the less number of possible movements
                return 99999 / depth
            return 0

        if depth == depthMax:
            return self.evaluate(currentState, True)
        blackState = self.getBlackState(currentState)
        whiteState = self.getWhiteState(currentState)
        white_rook_state = None
        for i in currentState:
            if i[2] == 2:
                white_rook_state = i
        # Assign the minimum value as a very positive number
        minimumValue = 99999
        for state in self.getListNextStatesB(blackState):
            newWhiteState = whiteState.copy()
            # It has removed the black rook? Remove it!
            if white_rook_state != None and white_rook_state[0:2] == state[0][0:2]:
                newWhiteState.remove(white_rook_state)
            state = state + newWhiteState
            # Don't analize the movements in which the white king is threatened
            if not self.black_king_threatened(state):
                minimumValue = min(minimumValue, self.podaMaxValueWhite(state, depth + 1, depthMax, alpha, beta))
                # Make a prunning in case of fulfill the alpha's condition
                if minimumValue <= alpha:
                    break
                # Update the beta's value
                beta = min(beta, minimumValue)

        return minimumValue

    def podaBlack(self, state, depthMax):
        alpha = -99999
        beta = 99999
        nextState = self.podaMaxValueBlack(state, 0, depthMax, alpha, beta).copy()
        copyState = self.copyState(nextState)
        if self.isVisitedSituation(False, copyState):
            return False
        self.listVisitedSituations.append((False, copyState))
        # Get the movement of the piece
        movement = self.getMovement(state, nextState)
        # Move the piece with this movement in the board of the match
        self.chess.move(movement[0], movement[1])
        return True

    def podaMaxValueBlack(self, currentState, depth, depthMax, alpha, beta):
        # Is the black king threatened in all of his movements?
        if self.black_king_movements_threatened(currentState):
            # If black king is threatened now, it's in a check mate position!
            if self.black_king_threatened(currentState):
                return -9999
            return 0

        if depth == depthMax:
            return self.evaluate(currentState, False)

        # Assign the maximun value as a very negative number
        maximumValue = -99999
        maximumState = None
        whiteState = self.getWhiteState(currentState)
        blackState = self.getBlackState(currentState)
        white_rook_state = None
        for i in currentState:
            if i[2] == 2:
                white_rook_state = i
        for state in self.getListNextStatesB(blackState):
            newWhiteState = whiteState.copy()
            # It has removed the black rook? Remove it!
            if white_rook_state != None and white_rook_state[0:2] == state[0][0:2]:
                newWhiteState.remove(white_rook_state)
            # Update the state
            state = state + newWhiteState
            # Don't analize the movements in which the white king is threatened
            if not self.black_king_threatened(state):
                valueSate = self.podaMinValueBlack(state, depth + 1, depthMax, alpha, beta)

                # It's a good state? Update the maximum value and state
                if valueSate > maximumValue:
                    maximumValue = valueSate
                    maximumState = state

                # Make a prunning in case of fulfill the beta's condition
                if maximumValue >= beta:
                    break
                # Update the alpha's value
                alpha = max(alpha, maximumValue)

        # If it reach the maximum depth, return the state that represents the next black's movement
        if depth == 0:
            return maximumState
        return maximumValue

    def podaMinValueBlack(self, currentState, depth, depthMax, alpha, beta):
        # Is the white king threatened in all of his movements?
        if self.white_king_movements_threatened(currentState):
            if self.white_king_threatened(currentState):
                # It's important to arribe to the checkmate position in the less number of possible movements
                return 99999 / depth
            return 0

        if depth == depthMax:
            return self.evaluate(currentState, False)
        blackState = self.getBlackState(currentState)
        whiteState = self.getWhiteState(currentState)
        black_rook_state = None
        for i in currentState:
            if i[2] == 8:
                black_rook_state = i
        # Assign the minimum value as a very positive number
        minimumValue = 99999
        for state in self.getListNextStatesW(whiteState):
            newBlackState = blackState.copy()
            # It has removed the white rook? Remove it!
            if black_rook_state != None and black_rook_state[0:2] == state[0][0:2]:
                newBlackState.remove(black_rook_state)
            state = state + newBlackState
            # Don't analize the movements in which the white king is threatened
            if not self.white_king_threatened(state):
                # Update minimum value
                minimumValue = min(minimumValue, self.podaMaxValueBlack(state, depth + 1, depthMax, alpha, beta))

                # Make a prunning in case of fulfill the alpha's condition
                if minimumValue <= alpha:
                    break
                # Update the beta's value
                beta = min(beta, minimumValue)

        return minimumValue


    def mean(self, values):
        sum = 0
        N = len(values)
        for i in range(N):
            sum += values[i]

        return sum / N
  
    def calculateExp(self, values):
        # Method that returns the expectation value
        if len(values) == 0:
            return 0
        mean = self.mean(values)
        
        sum = 0
        N = len(values)
        for i in range(N):
            sum += pow(values[i] - mean, 2)

        deviation = pow(sum / N, 1 / 2)
        
        # Don't standarized the values if deviation is 0
        if deviation == 0:
            return values[0]

        expectation = 0
        sum = 0
        N = len(values)
        for i in range(N):
            # Normalize the value, with the mean and deviation
            normalizedValues = (values[i] - mean) / deviation
            # Pass the values to positive with the function e^(-x), where x is the standardized value.
            positiveValue = pow(1 / math.e, normalizedValues)
            # Calculate the expectation
            expectation += positiveValue * values[i]
            sum += positiveValue

        return expectation / sum

    def expectimax(self, depthWhite, depthBlack):
        currentState = self.getCurrentState()
        # White pieces are in a check mate position?
        if self.white_check_mate(currentState):
            # The black pieces won!
            return False
        if self.black_king_threatened(currentState):
            # The white pieces won!
            return True
        # Copy the current state
        copyState = self.copyState(currentState)
        self.listVisitedSituations.append((False, copyState))
        # We assign to a variable the color of the pieces that will win, but in no one wins, the tie is represented by 'none'
        colorWin = None
        for i in range(50):
            currentState = self.getCurrentState()
            # White pieces turn!
            if i % 2 == 0:
                if not self.expectimaxWhite(currentState, depthWhite):
                    break
                if self.black_check_mate(currentState):
                    colorWin = True
                    break
            # Black pieces turn!
            else:
                if not self.expectimaxBlack(currentState, depthBlack):
                    break
                if self.white_check_mate(currentState):
                    colorWin = False
                    break

            # Print the board
            self.chess.board.print_board()
        # Print the final board
        self.chess.board.print_board()
        return colorWin

    def expectimaxWhite(self, state, depthMax):
        nextState = self.expMaxValueWhite(state, 0, depthMax)
        copyState = self.copyState(nextState)
        if self.isVisitedSituation(True, copyState):
            return False
        self.listVisitedSituations.append((True, copyState))
        # Get the movement of the piece
        movement = self.getMovement(state, nextState)
        # Move the piece with this movement in the board of the match
        self.chess.move(movement[0], movement[1])
        return True

    def expMaxValueWhite(self, currentState, depth, depthMax):
        # Is the white king threatened in all of his movements?
        if self.white_king_movements_threatened(currentState):
            if self.white_king_threatened(currentState):
                return -9999
            # If not, the pieces are in a tie position
            return 0
        # If arrive to the maximum depth, calculate the image of the evaluation function for that state
        if depth == depthMax:
            return self.evaluate(currentState, True)

        # Assign the maximun value as a very negative number
        maximumValue = -99999
        maximumState = None
        whiteState = self.getWhiteState(currentState)
        blackState = self.getBlackState(currentState)
        black_rook_state = None
        for i in currentState:
            if i[2] == 8:
                black_rook_state = i
        for state in self.getListNextStatesW(whiteState):
            newBlackState = blackState.copy()
            # # It has removed the black rook? Remove it!
            if black_rook_state != None and black_rook_state[0:2] == state[0][0:2]:
                newBlackState.remove(black_rook_state)
            # Update the state
            state = state + newBlackState
            # Don't analize the movements in which the white king is threatened
            if not self.white_king_threatened(state):
                valueSate = self.expValueWhite(state, depth + 1, depthMax)

                 # It's a good state? Update the maximum value and state
                if valueSate > maximumValue:
                    maximumValue = valueSate
                    maximumState = state

        # If it reach the maximum depth, return the state that represents the next white's movement
        if depth == 0:
            return maximumState
        return maximumValue

    def expValueWhite(self, currentState, depth, depthMax):
        # Is the black king threatened in all of his movements?
        if self.black_king_movements_threatened(currentState):
            if self.black_king_threatened(currentState):
                # It's important to arribe to the checkmate position in the less number of possible movements
                return 99999 / depth
            return 0

        if depth == depthMax:
            return self.evaluate(currentState, True)
        blackState = self.getBlackState(currentState)
        whiteState = self.getWhiteState(currentState)
        white_rook_state = None
        for i in currentState:
            if i[2] == 2:
                white_rook_state = i
        # Create a list of all the values
        values = []
        for state in self.getListNextStatesB(blackState):
            newWhiteState = whiteState.copy()
            # It has removed the black rook? Remove it!
            if white_rook_state != None and white_rook_state[0:2] == state[0][0:2]:
                newWhiteState.remove(white_rook_state)
            state = state + newWhiteState
            # Don't analize the movements in which the white king is threatened
            if not self.black_king_threatened(state):
                # Save all the next values on the list
                value = self.expMaxValueWhite(state, depth + 1, depthMax)
                values.append(value)
        # Assign probabilities and calculate the expectation
        return self.calculateExp(values)

    def expectimaxBlack(self, state, depthMax):
        nextState = self.expMaxValueBlack(state, 0, depthMax)
        copyState = self.copyState(nextState)
        if self.isVisitedSituation(True, copyState):
            return False
        self.listVisitedSituations.append((True, copyState))
        # Get the movement of the piece
        movement = self.getMovement(state, nextState)
        # Move the piece with this movement in the board of the match
        self.chess.move(movement[0], movement[1])
        return True

    def expMaxValueBlack(self, currentState, depth, depthMax):
        # Is the black king threatened in all of his movements?.
        if self.black_king_movements_threatened(currentState):
            # If black king is threatened now, it's in a check mate position!
            if self.black_king_threatened(currentState):
                return -9999
            return 0

        if depth == depthMax:
            return self.evaluate(currentState, False)

        # Assign the maximun value as a very negative number
        maximumValue = -99999
        maximumState = None
        blackState = self.getBlackState(currentState)
        whiteState = self.getWhiteState(currentState)
        white_rook_state = None
        for i in currentState:
            if i[2] == 2:
                white_rook_state = i
        for state in self.getListNextStatesB(blackState):
            newWhiteState = whiteState.copy()
            # It has removed the black rook? Remove it!
            if white_rook_state != None and white_rook_state[0:2] == state[0][0:2]:
                newWhiteState.remove(white_rook_state)
            # Update the state
            state = state + newWhiteState
            # Don't analize the movements in which the white king is threatened
            if not self.black_king_threatened(state):
                valueSate = self.expValueBlack(state, depth + 1, depthMax)
                # It's a good state? Update the maximum value and state
                if valueSate > maximumValue:
                    maximumValue = valueSate
                    maximumState = state

        # If it reach the maximum depth, return the state that represents the next black's movement
        if depth == 0:
            return maximumState
        return maximumValue

    def expValueBlack(self, currentState, depth, depthMax):
        # Is the white king threatened in all of his movements?
        if self.white_king_movements_threatened(currentState):
            if self.white_king_threatened(currentState):
                # It's important to arribe to the checkmate position in the less number of possible movements
                return 99999 / depth
            return 0

        if depth == depthMax:
            return self.evaluate(currentState, False)
        whiteState = self.getWhiteState(currentState)
        blackState = self.getBlackState(currentState)
        black_rook_state = None
        for i in currentState:
            if i[2] == 8:
                black_rook_state = i
        # Create a list of all the values
        values = []
        for state in self.getListNextStatesW(whiteState):
            newBlackState = blackState.copy()
            # It has removed the white rook? Remove it!
            if black_rook_state != None and black_rook_state[0:2] == state[0][0:2]:
                newBlackState.remove(black_rook_state)
            state = state + newBlackState
            if not self.white_king_threatened(state):
                # Save all the next values on the list
                values.append(self.expMaxValueBlack(state, depth + 1, depthMax))

        # Let's calculate the final expectation
        return self.calculateExp(values)

    def expectWhitePodaBlack(self, depthWhite, depthBlack):
        currentState = self.getCurrentState()
        # White pieces are in a check mate position?
        if self.white_check_mate(currentState):
            # The black pieces won!
            return False
        if self.black_king_threatened(currentState):
            # The white pieces won!
            return True
        # Copy the current state
        copyState = self.copyState(currentState)
        self.listVisitedSituations.append((False, copyState))
        # We assign to a variable the color of the pieces that will win, but in no one wins, the tie is represented by 'none'
        colorWin = None
        for i in range(50):
            currentState = self.getCurrentState()
            # White pieces turn!
            if i % 2 == 0:
                if not self.expectimaxWhite(currentState, depthWhite):
                    break
                if self.black_check_mate(currentState):
                    colorWin = True
                    break
            # Black pieces turn!
            else:
                if not self.podaBlack(currentState, depthBlack):
                    break
                if self.white_check_mate(currentState):
                    colorWin = False
                    break

            # Print the board
            self.chess.board.print_board()
        
        # Print the final board
        self.chess.board.print_board()
        return colorWin

    def expectBlackPodaWhite(self, depthWhite, depthBlack):
        currentState = self.getCurrentState()
        # White pieces are in a check mate position?
        if self.white_check_mate(currentState):
            # The black pieces won!
            return False
        if self.black_king_threatened(currentState):
            # The white pieces won!
            return True
        # Copy the current state
        copyState = self.copyState(currentState)
        self.listVisitedSituations.append((False, copyState))
        # We assign to a variable the color of the pieces that will win, but in no one wins, the tie is represented by 'none'
        colorWin = None
        for i in range(50):
            currentState = self.getCurrentState()
            # White pieces turn!
            if i % 2 == 0:
                if not self.podaWhite(currentState, depthWhite):
                    break
                if self.black_check_mate(currentState):
                    colorWin = True
                    break
            # Black pieces turn!
            else:
                if not self.expectimaxBlack(currentState, depthBlack):
                    break
                if self.white_check_mate(currentState):
                    colorWin = False
                    break

            # Print the board
            self.chess.board.print_board()

        # Print the final board
        self.chess.board.print_board()
        return colorWin

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

    # Initial board configuration
    TA[7][0] = 2
    TA[7][5] = 6
    TA[0][0] = 8
    TA[0][5] = 12

    # initialise board
    print("stating AI chess... s")
    aichess = Aichess(TA, True)

    print("printing board")
    aichess.chess.boardSim.print_board()

    print(aichess.expectimax(2,2))

    

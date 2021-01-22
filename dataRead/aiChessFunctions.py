# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 13:55:58 2021

@author: erikv
"""
import chess.pgn
import random

def toInt(board):
        l = [None] * 64
        for sq in chess.scan_reversed(board.occupied_co[chess.WHITE]):  # Check if white
            l[sq] = board.piece_type_at(sq)
        for sq in chess.scan_reversed(board.occupied_co[chess.BLACK]):  # Check if black
            l[sq] = -board.piece_type_at(sq)
        return [0 if v is None else v for v in l]

def makePositions(game):
    tempBoards=[]
    if (game.headers["Result"]=="1-0"):
        winner=1
    else:
        winner=0
    boards=[]
    count=0
    board = game.board()
    #board = game.bitboard()
    for move in game.mainline_moves():
        if count>4 and board.piece_type_at(move.to_square)==None:
            board.push(move)
            tempBoards.append(board)
        else:
            board.push(move)
        count+=1
    if len(tempBoards)>=10:
        tempBoards=random.sample(tempBoards, 10)
    for b in tempBoards:
        turn=int(b.turn)
        whiteCastlingQ=int(b.has_queenside_castling_rights(chess.WHITE))
        whiteCastlingK=int(b.has_kingside_castling_rights(chess.WHITE))
        blackCastlingQ=int(b.has_queenside_castling_rights(chess.BLACK))
        blackCastlingK=int(b.has_kingside_castling_rights(chess.BLACK))
        boards.append(toInt(b)+[turn,whiteCastlingQ,whiteCastlingK,blackCastlingQ,blackCastlingK])
    labels=[winner for x in boards]
    return (boards,labels)
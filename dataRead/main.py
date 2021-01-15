# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 20:14:11 2021

@author: erikv
"""
import chess.pgn
import aiChessFunctions as acf
import listReader as lr
pgn = open("C:\\Users\erikv\Desktop\Chess games\lichess.pgn")
count=0
evaluatedCount=0
boards=[]
labels=[]
while(count<1): #reads all the games
    game=chess.pgn.read_game(pgn)
    if (game.headers["Result"]!="1/2-1/2"):
        count+=1
        tempBoards,tempLabels=acf.makePositions(game)
        boards+=tempBoards
        labels+=tempLabels
    if evaluatedCount%1000==0:
        print(evaluatedCount)
    evaluatedCount+=1

lr.write(boards,'bitboards.txt')
lr.write(labels,'bitlabels.txt')
#b = lr.read('bitboards.txt')
#l = lr.read('bitlabels.txt')

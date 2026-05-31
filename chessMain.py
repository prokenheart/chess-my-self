import pygame as p
import chessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
MAINBACKGROUND = p.transform.scale(p.image.load("images/mainbackground.png"), (WIDTH, HEIGHT))

PLAYPOSITION = chessEngine.PLAYPOSITION
PLAYBUTTON = chessEngine.PLAYBUTTON

SETTINGPOSITION = chessEngine.SETTINGPOSITION
SETTINGBUTTON = chessEngine.SETTINGBUTTON

REPLAYPOSITION = chessEngine.REPLAYPOSITION
REPLAYBUTTON = chessEngine.REPLAYBUTTON

p.init()
screen = p.display.set_mode((WIDTH,HEIGHT))
clock = p.time.Clock()
gs = chessEngine.GameState()

def play():
    validMoves = gs.getAllValidMoves()
    chessEngine.loadImages()

    sqSelected = ()     # Luu vi tri click dau
    playerClicks = []   # Luu 2 lan click
    gs.drawGameState(screen)
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:    # Thoat game
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:       # Bat su kien click
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                sqSelected = (row,col)
                if (gs.board[sqSelected[0]][sqSelected[1]] == "--") and (len(playerClicks)==0):     # Nhan lan dau tien vao o trong
                    gs.drawGameState(screen)
                    if gs.moveLog != []: # To mau do
                        lastRow = gs.moveLog[len(gs.moveLog)-1].endRow
                        lastCol = gs.moveLog[len(gs.moveLog)-1].endCol
                        gs.drawPickBorder(screen,lastRow,lastCol,"red")
                    gs.drawPickBorder(screen,row,col,"yellow")
                    
                elif (gs.board[sqSelected[0]][sqSelected[1]] != "--") and (len(playerClicks)==0):   # Nhan lan dau tien vao o co
                    gs.drawGameState(screen)
                    if (gs.board[sqSelected[0]][sqSelected[1]][0]=="w" and gs.whiteToMove) or (gs.board[sqSelected[0]][sqSelected[1]][0]=="b" and not gs.whiteToMove):
                        playerClicks.append(sqSelected) # Them quan co muon di chuyen
                        for pieceMove in validMoves:
                            if pieceMove.startRow == row and pieceMove.startCol == col:
                                gs.drawSuggest(screen,pieceMove.endRow,pieceMove.endCol)
                    if gs.moveLog != []: # To mau do
                        lastRow = gs.moveLog[len(gs.moveLog)-1].endRow
                        lastCol = gs.moveLog[len(gs.moveLog)-1].endCol
                        gs.drawPickBorder(screen,lastRow,lastCol,"red")            
                    gs.drawPickBorder(screen,row,col,"yellow")
                    
                elif len(playerClicks)==1:  # O muon di chuyen
                    playerClicks.append(sqSelected) # Them o muon di chuyen
                    move = chessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                    playerClicks=[]
                    if move in validMoves:  # Nuoc di hop le
                        gs.makeMove(move)
                        gs.updateCastleCondition(move)
                        gs.promotion(move,screen)
                        gs.updateSaveBoard(move)
                        validMoves = gs.getAllValidMoves()
                        gs.drawGameState(screen)
                        gs.drawPickBorder(screen,row,col,"red")
                        gs.drawKingCheck(screen)
                        gs.testMate(screen,validMoves)
                        gs.threeGameState(gs.saveBoard,screen)
                    elif (gs.board[sqSelected[0]][sqSelected[1]] != "--") and (gs.board[sqSelected[0]][sqSelected[1]][0]=="w" and gs.whiteToMove) or (gs.board[sqSelected[0]][sqSelected[1]][0]=="b" and not gs.whiteToMove):
                        gs.drawGameState(screen)
                        playerClicks.append(sqSelected)
                        for pieceMove in validMoves:
                            if pieceMove.startRow == row and pieceMove.startCol == col:
                                gs.drawSuggest(screen,pieceMove.endRow,pieceMove.endCol)
                        if gs.moveLog != []:
                            lastRow = gs.moveLog[len(gs.moveLog)-1].endRow
                            lastCol = gs.moveLog[len(gs.moveLog)-1].endCol
                            gs.drawPickBorder(screen,lastRow,lastCol,"red")        
                        gs.drawPickBorder(screen,row,col,"yellow")
                        
                    else:   # O chon la on trong hoac phe dich
                        gs.drawGameState(screen)
                        if gs.moveLog != []:
                            lastRow = gs.moveLog[len(gs.moveLog)-1].endRow
                            lastCol = gs.moveLog[len(gs.moveLog)-1].endCol
                            gs.drawPickBorder(screen,lastRow,lastCol,"red")
                        gs.drawPickBorder(screen,row,col,"yellow")
            elif e.type == p.KEYDOWN:       #undo Move
                if e.key == p.K_z:
                    if gs.moveLog != []:
                        undoRow = gs.moveLog[len(gs.moveLog)-1].startRow
                        undoCol = gs.moveLog[len(gs.moveLog)-1].startCol
                        gs.updateUndoCastleCon()
                        gs.updateUndoSaveBoard()
                        gs.undoMove()
                        validMoves = gs.getAllValidMoves()
                        gs.drawGameState(screen)
                        gs.drawPickBorder(screen,undoRow,undoCol,"blue")
                        gs.drawKingCheck(screen)

            if gs.isEndGame == True:
                screen.blit(REPLAYBUTTON, p.Rect(REPLAYPOSITION[0],REPLAYPOSITION[1],REPLAYPOSITION[2],REPLAYPOSITION[3]))

        clock.tick(MAX_FPS)
        p.display.flip()

def replay():
    gs.board = [
        ["bR","bN","bB","bQ","bK","bB","bN","bR"],
        ["bp","bp","bp","bp","bp","bp","bp","bp"],
        ["--","--","--","--","--","--","--","--"],
        ["--","--","--","--","--","--","--","--"],
        ["--","--","--","--","--","--","--","--"],
        ["--","--","--","--","--","--","--","--"],
        ["wp","wp","wp","wp","wp","wp","wp","wp"],
        ["wR","wN","wB","wQ","wK","wB","wN","wR"]
    ]
    gs.whiteToMove = True
    gs.moveLog = []
    gs.whiteKingLocation = (7,4)
    gs.blackKingLocation = (0,4)

    gs.moved = {'00' : False,
                '04' : False,
                '07' : False,
                '70' : False,
                '74' : False,
                '77' : False}
    
    gs.startCastle = ['00','04','07','70','74','77']
    gs.saveBoard = []
    gs.isEndGame = False
    play()

running = True
while running:
    
    screen.fill(p.Color('white'))
    screen.blit(MAINBACKGROUND, p.Rect(0,0,WIDTH,HEIGHT))
    screen.blit(PLAYBUTTON, p.Rect(PLAYPOSITION[0],PLAYPOSITION[1],PLAYPOSITION[2],PLAYPOSITION[3]))
    screen.blit(SETTINGBUTTON, p.Rect(SETTINGPOSITION[0],SETTINGPOSITION[1],SETTINGPOSITION[2],SETTINGPOSITION[3]))
    for e in p.event.get():
        if e.type == p.QUIT:    # Thoat game
            running = False
        elif e.type == p.MOUSEBUTTONDOWN:       # Bat su kien click
            location = p.mouse.get_pos()
            if chessEngine.isInside(location[0], location[1], PLAYPOSITION[0],PLAYPOSITION[1],PLAYPOSITION[2],PLAYPOSITION[3]):
                play()
    
    p.display.flip()


import pygame as p

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION

ALPHABET = ["a", "b", "c", "d", "e", "f", "g", "h"]

IMAGES = {}

PLAYPOSITION = [int(2.5*SQ_SIZE), int(6.5*SQ_SIZE), int(3*SQ_SIZE), int(1.25*SQ_SIZE)]
PLAYBUTTON = p.transform.scale(p.image.load("images/play.png"), (PLAYPOSITION[2], PLAYPOSITION[3]))

SETTINGPOSITION = [int(0.25*SQ_SIZE), int(0.25*SQ_SIZE), int(0.75*SQ_SIZE), int(0.75*SQ_SIZE)]
SETTINGBUTTON = p.transform.scale(p.image.load("images/setting.png"), (SETTINGPOSITION[2], SETTINGPOSITION[3]))

REPLAYPOSITION = [int(1*SQ_SIZE), int(5*SQ_SIZE), int(2.5*SQ_SIZE), int(1.25*SQ_SIZE)]
REPLAYBUTTON = p.transform.scale(p.image.load("images/replay.png"), (REPLAYPOSITION[2], REPLAYPOSITION[3]))

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def isInside(colPoint, rowPoint, left, top, width, height):
    if colPoint < left or colPoint > left+width:
        return False
    if rowPoint < top or rowPoint > top+height:
        return False
    return True

class GameState():
    def __init__(self):
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]
        self.moveFunction = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                             'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K':self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)

        self.moved = {'00' : False,
                      '04' : False,
                      '07' : False,
                      '70' : False,
                      '74' : False,
                      '77' : False}
        self.startCastle = ['00','04','07','70','74','77']

        self.saveBoard = []
        self.isEndGame = False

    def drawGameState(self, screen):
        self.drawBoard(screen)
        self.drawPieces(screen)

    def drawBoard(self, screen):
        colors = [p.Color("white"), p.Color("gray")]
        for r in range (DIMENSION):
            for c in range (DIMENSION):
                color = colors[((r+c)%2)]
                p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        
    def drawPieces(self, screen):
        font = p.font.Font('freesansbold.ttf', 16)
        colors = [p.Color("gray"), p.Color("white")]
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                piece = self.board[r][c]
                if piece != "--":
                    screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
                if c==0:
                    text = font.render(str(DIMENSION-r), True, colors[((r+c)%2)])
                    textRect = text.get_rect()
                    textRect.center = (int(c*SQ_SIZE+SQ_SIZE*0.1),int(r*SQ_SIZE+SQ_SIZE*0.2))
                    screen.blit(text, textRect)
                if r==7:
                    text = font.render(str(ALPHABET[c]), True, colors[((r+c)%2)])
                    textRect = text.get_rect()
                    textRect.center = (int(c*SQ_SIZE+SQ_SIZE*0.9),int(r*SQ_SIZE+SQ_SIZE*0.85))
                    screen.blit(text, textRect)
    
    def drawPickBorder(self, screen, row, col, color):
        p.draw.rect(screen,p.Color(color),p.Rect(col*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE),5)

    def drawKingCheck(self, screen):
        if self.inCheck():
            if self.whiteToMove:
                self.drawPickBorder(screen,self.whiteKingLocation[0],self.whiteKingLocation[1],p.Color("gold"))
            else:
                self.drawPickBorder(screen,self.blackKingLocation[0],self.blackKingLocation[1],p.Color("gold"))

    def drawSuggest(self, screen, r, c):
        p.draw.circle(screen, p.Color('olivedrab1'), [c*SQ_SIZE+int(0.5*SQ_SIZE), r*SQ_SIZE+int(0.5*SQ_SIZE)], 10, 0)

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove #switch turn
        #update king location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        if len(self.moveLog)>=2:
            self.afterEnpassant()

        if self.moveLog != []:
            self.afterCastle()

    def undoMove(self):
        if self.moveLog != []:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

        if self.moveLog != []:
            self.undoEnpassant()
        self.undoCastle(move)
        

    def threeGameState(self, saveBoard, screen):
        count = 0
        if len(saveBoard)>=3:
            for i in range(0,len(saveBoard)):
                if saveBoard[len(saveBoard)-1]==saveBoard[i]:
                    count+=1
        if count>=3:
            self.printTheEnd(screen,'Stalemate!!!',"")

    def updateUndoSaveBoard(self):
        if self.moveLog!=[]:
            move = self.moveLog[len(self.moveLog)-1]
            if move.saveBoard == []:
                self.saveBoard.pop()
            else:
                self.saveBoard = move.saveBoard
                self.saveBoard.pop()

    def updateSaveBoard(self, move):
        save = self.convertSaveBoardToString(self.board)
        
        if move.pieceCaptured != "--":  # An quan
            move.saveBoard = self.saveBoard
            self.saveBoard = []
        if move.pieceMoved[1] == "p":   # Tot di chuyen
            move.saveBoard = self.saveBoard
            self.saveBoard = []
        if move.castle != -1:   # Nhap thanh
            move.saveBoard = self.saveBoard
            self.saveBoard = []
        if move.pieceMoved == "wK" and (self.moved['70']==False or self.moved['77']==False):
            if move.moved['74']:
                move.saveBoard = self.saveBoard
                self.saveBoard = []
        elif move.pieceMoved == "bK" and (self.moved['00']==False or self.moved['07']==False):
            if move.moved['04']:
                move.saveBoard = self.saveBoard
                self.saveBoard = []
        elif move.pieceMoved == "wR" and self.moved['74']==False:
            if move.moved['70'] or move.moved['70']:
                move.saveBoard = self.saveBoard
                self.saveBoard = []
        elif move.pieceMoved == "bR" and self.moved['04']==False:
            if move.moved['00'] or move.moved['00']:
                move.saveBoard = self.saveBoard
                self.saveBoard = []

        if len(self.moveLog) >=2: # Bat tot qua duong
            lastMove = self.moveLog[len(self.moveLog)-2]
            if lastMove.isEnpassant != ():
                move.saveBoard = self.saveBoard
                self.saveBoard = []
        
        self.saveBoard.append(save)

    def convertSaveBoardToString(self, board):
        saveBoard = ""
        for r in range(8):
            for c in range(8):
                saveBoard = saveBoard + board[r][c]
        return saveBoard

    def undoCastle(self, move):
        if move.pieceMoved[1] == "K":
            if abs(move.startCol-move.endCol)==2:
                self.board[move.startRow][move.rook] = self.board[move.startRow][move.castle]
                self.board[move.startRow][move.castle] = "--"
            move.castle = -1
            move.rook = -1


    def afterCastle(self):
        move = self.moveLog[len(self.moveLog)-1]
        if move.pieceMoved[1]=="K" and move.startCol==4 and move.endCol==2:
            self.board[move.startRow][3] = self.board[move.startRow][0]
            self.board[move.startRow][0] = "--"
            move.castle = 3
            move.rook = 0
        elif move.pieceMoved[1]=="K" and move.startCol==4 and move.endCol==6:
            self.board[move.startRow][5] = self.board[move.startRow][7]
            self.board[move.startRow][7] = "--"
            move.castle = 5
            move.rook = 7
            
    def updateCastleCondition(self, move):
        isMoved = str(move.startRow) + str(move.startCol)
        if isMoved in self.startCastle:
            self.moved[isMoved] = True
            move.moved[isMoved] = True
        
        isAttacked = str(move.endRow) + str(move.endCol)
        if isAttacked in self.startCastle:
            self.moved[isAttacked] = True
            move.moved[isAttacked] = True

    def updateUndoCastleCon(self):
        if self.moveLog!=[]:
            move = self.moveLog[len(self.moveLog)-1]
            isMoved = str(move.startRow) + str(move.startCol)
            if isMoved in self.startCastle:
                if move.moved[isMoved] == True:
                    self.moved[isMoved] = False
                    move.moved[isMoved] = False

    def castle(self, validmoves):
        leftWhiteClear = True
        rightWhiteClear = True
        leftBlackClear = True
        rightBlackClear = True

        if self.whiteToMove:
            if (not self.moved['70']) and (not self.moved['74']) and (not self.inCheck()) and (not self.squareUnderAttack(7,2)):
                for c in range(1,4):
                    if self.board[7][c] != "--":
                        leftWhiteClear = False
                        break
                if leftWhiteClear:
                    validmoves.append(Move((7,4), (7,2), self.board))
            if (not self.moved['77']) and (not self.moved['74']) and (not self.inCheck()) and (not self.squareUnderAttack(7,6)):
                for c in range(5,7):
                    if self.board[7][c] != "--":
                        rightWhiteClear = False
                        break
                if rightWhiteClear:
                    validmoves.append(Move((7,4), (7,6), self.board))
        else:
            if (not self.moved['00']) and (not self.moved['04']) and (not self.inCheck()) and (not self.squareUnderAttack(0,2)):
                for c in range(1,4):
                    if self.board[0][c] != "--":
                        leftBlackClear = False
                        break
                if leftBlackClear:
                    validmoves.append(Move((0,4), (0,2), self.board))
            if (not self.moved['07']) and (not self.moved['04']) and (not self.inCheck()) and (not self.squareUnderAttack(0,6)):
                for c in range(5,7):
                    if self.board[0][c] != "--":
                        rightBlackClear = False
                        break
                if rightBlackClear:
                    validmoves.append(Move((0,4), (0,6), self.board))
        return validmoves

    def undoEnpassant(self):
        move = self.moveLog[len(self.moveLog)-1]
        if move.isEnpassant!=():
            self.board[move.isEnpassant[0]][move.isEnpassant[1]] = move.pieceMoved

    def afterEnpassant(self):
        lastMove = self.moveLog[len(self.moveLog)-2]
        if lastMove.isEnpassant != ():
            move = self.moveLog[len(self.moveLog)-1]
            if move.pieceMoved == "wp" and move.endRow==2 and move.endCol==lastMove.isEnpassant[1]:
                self.board[lastMove.isEnpassant[0]][lastMove.isEnpassant[1]] = "--"
            elif move.pieceMoved == "bp" and move.endRow==5 and move.endCol==lastMove.isEnpassant[1]:
                self.board[lastMove.isEnpassant[0]][lastMove.isEnpassant[1]] = "--"

    def enpassant(self, validmoves):
        if self.moveLog != []:
            move = self.moveLog[len(self.moveLog)-1]
            if self.whiteToMove:
                enpassantPawn = "wp"
            else:
                enpassantPawn = "bp"

            if move.pieceMoved[1] == "p" and abs(move.startRow-move.endRow)==2:
                if move.endCol>=0 and move.endCol<=6 and self.board[move.endRow][move.endCol+1] == enpassantPawn:
                    move.isEnpassant = (move.endRow,move.endCol)
                    validmoves.append(Move((move.endRow,move.endCol+1), ((move.startRow+move.endRow)//2,move.endCol), self.board))
                if move.endCol<=7 and move.endCol>=1 and self.board[move.endRow][move.endCol-1] == enpassantPawn:
                    move.isEnpassant = (move.endRow,move.endCol)
                    validmoves.append(Move((move.endRow,move.endCol-1), ((move.startRow+move.endRow)//2,move.endCol), self.board))
        return validmoves

    def pickPromotion(self,r,c,pick):
        side = not self.whiteToMove
        if side:
            promotionPieces = ["wQ", "wR", "wB", "wN"]
        else:
            promotionPieces = ["bQ", "bR", "bB", "bN"]
        self.board[r][c] = promotionPieces[pick//2]

    def promotion(self, move, screen):
        if move.pieceMoved[1] == "p" and (move.endRow == 0 or move.endRow == 7):
            self.drawGameState(screen)
            self.printPromotion(screen)
            running = True
            while running:
                for e in p.event.get():
                    if e.type == p.MOUSEBUTTONDOWN:       # Bat su kien click
                        location = p.mouse.get_pos()
                        col = location[0]//SQ_SIZE
                        row = location[1]//SQ_SIZE
                        if row == 4 or row == 3:
                            self.pickPromotion(move.endRow,move.endCol,col)
                            running = False
                p.display.flip()

        
    def printPromotion(self, screen):
        side = not self.whiteToMove
        p.draw.rect(screen,p.Color("white"),p.Rect(0,3*SQ_SIZE,8*SQ_SIZE,2*SQ_SIZE))
        if side:
            promotionPieces = ["wQ", "wR", "wB", "wN"]
        else:
            promotionPieces = ["bQ", "bR", "bB", "bN"]

        for piece in range(len(promotionPieces)):
            image = p.transform.scale(p.image.load("images/" + promotionPieces[piece] + ".png"), (SQ_SIZE, SQ_SIZE))
            screen.blit(image, p.Rect((0.5+piece*2)*SQ_SIZE,3.5*SQ_SIZE,SQ_SIZE,SQ_SIZE))

    def testMate(self,screen, validmove):
        if validmove == []:
            self.isEndGame = True
            
            if self.inCheck():
                if self.whiteToMove:
                    self.printTheEnd(screen,'Checkmate!!!',"Black Win")
                else:
                    self.printTheEnd(screen,'Checkmate!!!',"White Win")
            else:
                self.printTheEnd(screen,'Stalemate!!!',"")

    def printTheEnd(self, screen, wEnd, side):
        p.draw.rect(screen,p.Color("white"),p.Rect(0,int(2.5*SQ_SIZE),8*SQ_SIZE,int(1.5*SQ_SIZE)))
        font = p.font.Font('freesansbold.ttf', 32)
        text = font.render(wEnd, True, 'red')
        textRect = text.get_rect()
        textRect.center = (WIDTH//2,3*SQ_SIZE)
        screen.blit(text, textRect)
        sideWin = font.render(side, True, 'blue')
        sideRect = sideWin.get_rect()
        sideRect.center = (WIDTH//2,(3*SQ_SIZE)+(SQ_SIZE//2))
        screen.blit(sideWin, sideRect)

    def getAllValidMoves(self):
        moves = self.getAllPosibleMoves()
        for i in range(len(moves)-1,-1,-1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.pop(i)
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        moves = self.enpassant(moves)
        moves = self.castle(moves)
        return moves   

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
            
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPosibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllPosibleMoves(self):
        moves = []
        if self.whiteToMove:
            turn = "w"
        else:
            turn = "b"
        for r in range (8):
            for c in range (8):
                if self.board[r][c][0] == turn:
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r,c,moves)
        return moves
        
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:    #white pawn
            if self.board[r-1][c] == "--":  #move forward
                moves.append(Move((r,c), (r-1,c), self.board))
                if r==6 and self.board[r-2][c] == "--":     #move forward from start
                    moves.append(Move((r,c), (r-2,c), self.board))
            if c-1 >= 0:    #capture to the left
                if self.board[r-1][c-1][0] == "b":
                    moves.append(Move((r,c), (r-1,c-1), self.board))
            if c+1 <= 7:    #capture to to the right
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r,c), (r-1,c+1), self.board))

        else:                   #black pawn
            if self.board[r+1][c] == "--":  #move forward
                moves.append(Move((r,c), (r+1,c), self.board))
                if r==1 and self.board[r+2][c] == "--":     #move forward from start
                    moves.append(Move((r,c), (r+2,c), self.board))
            if c-1 >= 0:    #capture to the left
                if self.board[r+1][c-1][0] == "w":
                    moves.append(Move((r,c), (r+1,c-1), self.board))
            if c+1 <= 7:    #capture to to the right
                if self.board[r+1][c+1][0] == "w":
                    moves.append(Move((r,c), (r+1,c+1), self.board))

    def getRookMoves(self, r, c, moves):
        directions = ((-1,0), (1,0), (0,1), (0,-1))
        if self.whiteToMove:
            enemy = "b"
        else:
            enemy = "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0<=endRow<=7 and 0<=endCol<=7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c), (endRow,endCol), self.board))
                    elif endPiece[0] == enemy:
                        moves.append(Move((r,c), (endRow,endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getBishopMoves(self, r, c, moves):
        directions = ((-1,1), (1,1), (-1,-1), (1,-1))
        if self.whiteToMove:
            enemy = "b"
        else:
            enemy = "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0<=endRow<=7 and 0<=endCol<=7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c), (endRow,endCol), self.board))
                    elif endPiece[0] == enemy:
                        moves.append(Move((r,c), (endRow,endCol), self.board))
                        break
                    else:
                        break
                else:
                    break
    
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKnightMoves(self, r, c, moves):
        knigtmoves = ((-2,1), (-1,2), (1,2), (2,1), (2,-1), (1,-2), (-1,-2), (-2,-1))
        if self.whiteToMove:
            ally = "w"
        else:
            ally = "b"

        for m in knigtmoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0<=endRow<=7 and 0<=endCol<=7:
                if self.board[endRow][endCol][0] != ally:
                    moves.append(Move((r,c), (endRow,endCol), self.board))

    def getKingMoves(self, r, c, moves):
        kingmoves = ((-1,0), (1,0), (0,1), (0,-1), (-1,1), (1,1), (-1,-1), (1,-1))
        if self.whiteToMove:
            ally = "w"
        else:
            ally = "b"

        for m in kingmoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0<=endRow<=7 and 0<=endCol<=7:
                if self.board[endRow][endCol][0] != ally:
                    moves.append(Move((r,c), (endRow,endCol), self.board))

class Move():

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k,v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k,v in filesToCols.items()}


    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol
        self.isEnpassant = ()
        self.castle = -1
        self.rook = -1
        self.moved = {'00' : False,
                      '04' : False,
                      '07' : False,
                      '70' : False,
                      '74' : False,
                      '77' : False}
        
        self.saveBoard = []

    def __eq__(self, other):
        if isinstance(other,Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
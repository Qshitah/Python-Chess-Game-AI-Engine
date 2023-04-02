"""
This class is responsable of storing all information about the current state of a chess game.
It will also will be responsable for determining the valid moves at the current state.
It will also keep a move log.
"""


class GameState():
    def __init__(self):
        #board is 8x8 2D list, each element of list has 2 characters.
        #the first character represent the color of the piece "b", "w".
        #The second character represent the type of character.
        #"--" represent an empty space with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]     
        ]

        self.moveFunctions = {"p": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
        "B":self.getBishopMoves,"Q": self.getQueenMoves,"K":self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enPassantPossible = () #Coordinate for the square where en passant capture is possible
        self.currentCastlingRights = CastleRights(True, True, True, True)
        #Track Log For Changing
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs
                                            , self.currentCastlingRights.bks, self.currentCastlingRights.bks)]


    def makeMove(self,move):
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.startRow][move.startCol] = "--"
        self.moveLog.append(move) #Log and save the move 
        self.whiteToMove = not self.whiteToMove #swap Players
        #update location of king
        if move.pieceMoved == "wk":
            self.whiteKingLocation = (move.endRow,move.endCol)
        elif move.pieceMoved == "bk":
            self.blackKingLocation = (move.endRow,move.endCol)

        #Enpassant move
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = "--" #Capturing the pawn

        #If Pawn moves twice,next move can capture enpassant
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2: #Only on 2 squares pawn advances
            self.enPassantPossible = ((move.startRow + move.endRow)//2, move.endCol)
        else: self.enPassantPossible = ()

        #Castle Move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #Kingside Castle Move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1] #Moves the rook
                self.board[move.endRow][move.endCol + 1] = '--' #Erase old rook
            else:#Queenside Castle Move
                self.board[move.endRow][move.endCol + 1]= self.board[move.endRow][move.endCol - 2] #Moves the rook
                self.board[move.endRow][move.endCol - 2] = '--'
        
        #Updating castling rights - Whenever it's a rook or king move
        self.updateCastlingRights(move) 
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs
                                            , self.currentCastlingRights.bks, self.currentCastlingRights.bks))
        

    """
    Undo the last move
    """
    def undoMove(self):
        if len(self.moveLog) != 0: #Make sure there is move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #swap Players
            #update location of king
            if move.pieceMoved == "wk":
                self.whiteKingLocation = (move.startRow,move.startCol)
            elif move.pieceMoved == "bk":
                self.blackKingLocation = (move.startRow,move.startCol)
            #Undo EnPassant Move
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = "--" #remove the pawn that was added in the wrong square
                self.board[move.startRow][move.endCol] = move.pieceCaptured #put the pawn back on the correct square it was captured from
                self.enPassantPossible = (move.endRow, move.endCol) #allow an enpassant to happen on the next move
            #Undo a 2 square pawn advance
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2: #Only on 2 squares pawn advances
                self.enPassantPossible = ()
            
            #Undo Castling Move
            self.castleRightsLog.pop() #get rid of the new castle rights from the move we are undoing
            self.currentCastlingRights = self.castleRightsLog[-1] #set the currentCastleRights to the last one in the list

            #Undo Castle Move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1]= self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:
                    self.board[move.endRow][move.endCol - 2]= self.board[move.endRow][move.endCol + 1] #Moves the rook
                    self.board[move.endRow][move.endCol + 1] = '--'

    def updateCastlingRights(self,move):
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0 : #left Rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7: #Right Rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0 : #left Rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7: #Right Rook
                    self.currentCastlingRights.bks = False
            

    
    def getValidMoves(self):
        
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        moves = []

        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
            self.getCastleMoves(kingRow, kingCol, moves)
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
            self.getCastleMoves(kingRow, kingCol, moves)

        if self.inCheck:
            if len(self.checks) == 1: #Only 1 check, block check or move king
                moves = self.getAllPossibleMoves()

                #To block a check move u must move a piece into one of the squares between enemy piece and king
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] # Enemy piece that causing the check
                validSquares = [] #Squares that piece can move to
                # if knight, must capture knight or move king , other piece can be blocked
                if pieceChecking[1] == "N":
                    validSquares[(checkRow,checkCol)]
                else:
                    for i in range(1,8):
                        validSq = (kingRow + check[2] * i, kingCol + check[3] * i) # check[2/3] are the check directions
                        validSquares.append(validSq)
                        if validSq[0] == checkRow and validSq[1] == checkCol: #once you get to the piece end checks
                            break
                #get rid of any moves that don't block check or move king
                for i in range(len(moves) -1, -1, -1):
                    if moves[i].pieceMoved[1] != "K": #move doesn't move king so it must capture or block
                        if not (moves[i].endRow,moves[i].endCol) in validSquares: #move doesn't block check or capture piece
                            moves.remove(moves[i])
            else: #double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else: #not in check so all moves are fine
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck: self.checkMate = True 
            else: self.staleMate = True
        else: 
            self.checkMate = False
            self.staleMate = False
        
        
        
        return moves

    '''
    Determine if enemy can attack the square r,c
    '''
    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove #switch the opponenet turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove #switch the turn back 
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: #square is under attack
                return True
        return False 


    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if(turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves) #call the appropriate move function based on piece type
        return moves



    '''
    Get all the pawn move for the pawn located at row, col and add these moves to the list
    '''
    def getPawnMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove: #white pawn move
            if self.board[r-1][c] == "--": #1 square jump and check the jump is clear and empty
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((r,c), (r-1,c), self.board))
                    if(r==6):
                        if self.board[r-2][c] == "--" : #2 square jump and check the jump is clear and first row
                            moves.append(Move((r,c), (r-2,c), self.board))

            if c-1>=0: #Capture to the left
                if self.board[r-1][c-1][0] == "b": #any enemy piece
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append(Move((r,c), (r-1,c-1), self.board))
                elif (r-1,c-1) == self.enPassantPossible :
                    moves.append(Move((r,c), (r-1,c-1), self.board, True))

            if c+1<=7: #Capture to the right
                if self.board[r-1][c+1][0] == "b": #any enemy piece
                    if not piecePinned or pinDirection == (-1,1):
                        moves.append(Move((r,c), (r-1,c+1), self.board))
                elif (r-1,c+1) == self.enPassantPossible :
                    moves.append(Move((r,c), (r-1,c+1), self.board, True))

        else: #Black moves
            if self.board[r+1][c] == "--": #1 square jump and check the jump is clear and empty
                if not piecePinned or pinDirection == (1,0):
                    moves.append(Move((r,c), (r+1,c), self.board))
                    if(r==1):
                        if self.board[r+2][c] == "--" : #2 square jump and check the jump is clear and first row
                            moves.append(Move((r,c), (r+2,c), self.board))

            if c-1>=0: #Capture to the left
                if self.board[r+1][c-1][0] == "w": #any enemy piece
                    if not piecePinned or pinDirection == (1,-1):
                        moves.append(Move((r,c), (r+1,c-1), self.board))
                elif (r+1,c-1) == self.enPassantPossible :
                    moves.append(Move((r,c), (r+1,c-1), self.board, True))

            if c+1<=7: #Capture to the right
                if self.board[r+1][c+1][0] == "w": #any enemy piece
                    if not piecePinned or pinDirection == (1,1):
                        moves.append(Move((r,c), (r+1,c+1), self.board))
                elif (r+1,c+1) == self.enPassantPossible :
                    moves.append(Move((r,c), (r+1,c+1), self.board, True))

    '''
    Get all the Rook move for the rook located at row, col and add these moves to the list
    '''
    def getRookMoves(self, r, c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                if self.board[r][c][1] != "Q": #Can't remove queen from pins on rook moves, only remove it on bishop move
                    self.pins.remove(self.pins[i])
                break

        directions = ((1,0),(-1,0),(0,1),(0,-1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8): #Can move max of 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8 : #stay on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": #Valid space
                            moves.append(Move((r,c), (endRow,endCol), self.board))
                        elif endPiece[0] == enemyColor: #enemy piece
                            moves.append(Move((r,c), (endRow,endCol), self.board))
                            break
                        else: #Friendly piece
                            break
                else: #out board
                    break
    '''
    Get all the Knight move for the knight located at row, col and add these moves to the list
    '''
    def getKnightMoves(self, r, c,moves):
        piecePinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        
        directions = ((-2,-1),(-2,1),(-1,-2),(-1,2),(2,-1),(2,1),(1,-2),(1,2))
        allyColor = "w" if self.whiteToMove else "b"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8 : #stay on board
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if allyColor != endPiece[0]: #not Ally piece also empty space
                        moves.append(Move((r,c), (endRow,endCol), self.board))

    '''
    Get all the Bishop move for the bishop located at row, col and add these moves to the list
    '''
    def getBishopMoves(self, r, c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((1,1),(-1,-1),(1,-1),(-1,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8): #Can move max of 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8 : #stay on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": #Valid space
                            moves.append(Move((r,c), (endRow,endCol), self.board))
                        elif endPiece[0] == enemyColor: #enemy piece
                            moves.append(Move((r,c), (endRow,endCol), self.board))
                            break
                        else: #Friendly piece
                            break
                else: #out board
                    break

    '''
    Get all the Queen move for the queen located at row, col and add these moves to the list
    '''
    def getQueenMoves(self, r, c,moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    '''
    Get all the King move for the king located at row, col and add these moves to the list
    '''
    def getKingMoves(self, r, c,moves):
        rowMoves = (-1,-1,-1,0,0,1,1,1)
        colMoves = (-1,0,1,-1,1,-1,0,1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8 : #stay on board
                endPiece = self.board[endRow][endCol]
                if allyColor != endPiece[0]: #not Ally piece also empty space
                    #place king on end square and check for checks
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow,endCol)
                    else:
                        self.blackKingLocation = (endRow,endCol)
                    inCheck,pins,checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c), (endRow,endCol), self.board))
                    #place king to an original position
                    if allyColor == "w":
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)

    '''
    Generate all valid castle moves for the king at (r,c) and add them to a list of moves
    '''
    def getCastleMoves(self, r, c, moves ):
        if self.squareUnderAttack(r, c):
            return #Can't castle while we are in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves )
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves )
        
    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r,c), (r,c+2), self.board, isCastleMove= True))
    
    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r, c-2) and not self.squareUnderAttack(r, c-3):
                moves.append(Move((r,c), (r,c-2), self.board, isCastleMove= True))
    '''
    Return if the player is in check, a list of pins , and a list of checks
    '''

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        #Check outward from kings pins and checks, keep a track of pins
        directions = ((-1, 0),(0, -1),(1, 0),(0, 1),(-1, -1),(-1, 1),(1, -1),(1, 1))
        for i in range(len(directions)):
            d = directions[i]
            possiblePins = () #Reset possible pins
            for j in range(1,8):
                endRow = startRow + d[0] * j
                endCol = startCol + d[1] * j
                if 0 <= endRow < 8 and 0 <= endCol < 8 :
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePins == (): #Alliend piece could be pinned
                            possiblePins = (endRow,endCol,d[0],d[1])
                        else: #Allied piece not pinned or checked possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        typed = endPiece[1]
                        #There are 5 Possibilities hara in this complex conditional
                        #1.) Orthognolly away from a king and piece is a rook
                        #2.) Diagonally away from a king and piece is a bishop
                        #3.) 1 square away from a king and piece is a pawn
                        #4.) Any direction and piece is a queen
                        #5.) Any direction 1 square away and a piece is a king 
                        # (This is a necessary to prevent a king move to a square controlled by another king)
                        if(0<= i <= 3 and typed == "R") or \
                                (4 <= i <= 7 and typed == "B") or \
                                (j == 1 and typed == "p" and ((enemyColor == "w" and 6<= i <= 7) or (enemyColor == "b" and 4<= i <= 5))) or \
                                (typed == "Q") or (j == 1 and typed == "K"):
                            if possiblePins == (): #No piece is blocking, so check
                                inCheck = True
                                checks.append((endRow,endCol,d[0],d[1]))
                                break
                            else: #Piece is blocking so pin
                                pins.append(possiblePins)
                                break
                        else: break #Enemy piece not applying blocking
                else: break

        #Knight check
        directions = ((-2,-1),(-2,1),(-1,-2),(-1,2),(2,-1),(2,1),(1,-2),(1,2))
        for d in directions:
            endRow = startRow + d[0]
            endCol = startCol + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8 : #stay on board
                endPiece = self.board[endRow][endCol]
                if enemyColor == endPiece[0] and endPiece[1] == "N": #Enemy knight attacking king
                    inCheck = True
                    checks.append((endRow,endCol,d[0],d[1]))
            else: break
        return inCheck, pins, checks

class CastleRights():
    def __init__(self,wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs
class Move():
    #maps key to values
    #key: value

    ranktoRows = {"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    rowtoRanks = {v: k for k,v in ranktoRows.items()}
    filetoCols = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    coltoFiles = {v:k for k,v in filetoCols.items()}
    def __init__(self,startSQ, endSQ , board, enPassantPossible = False, isCastleMove = False ):
        self.startRow = startSQ[0]
        self.startCol = startSQ[1]
        self.endRow = endSQ[0]
        self.endCol = endSQ[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        #Pawn Promotion
        self.isPromotionPawn = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)
        #En Passant
        self.isEnPassantMove = enPassantPossible
        if self.isEnPassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        #Castle Move
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol
        
    
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.RankFile(self.startRow,self.startCol) + self.RankFile(self.endRow,self.endCol)
    
    def RankFile(self,r,c):
        return self.coltoFiles[c] + self.rowtoRanks[r]
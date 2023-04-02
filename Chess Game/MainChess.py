"""
This is our main driver.
It will be responsible of handling user input and displaying the current GameState object
"""
import pygame as p
import EngineChess

WIDTH = HEIGHT = 512 
DIMENSION = 8 #Dimension of chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #For animation later on
IMAGES = {}

"""
Initialize a global dictionary of images.
This will be exactly called once in the main
"""

def loadImages():
    pieces = ["bp","bR", "bN", "bB", "bQ", "bK","wp","wR", "wN", "wB", "wQ", "wK"]
    for i in pieces:
        IMAGES[i] = p.transform.scale(p.image.load(f"images/{i}.png"),(SQ_SIZE,SQ_SIZE))

'''
The main driver for our code. This will Handle user input and the graphics.
'''

def main():
    #Initialize p
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    time = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = EngineChess.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made
    animate = False #flag variable for when we should animate a move
    loadImages() #only do this once, before the while loop.
    running = True
    sqSelected = () #no square is selected, keep the track of the last click of the user (row,col)
    playerClicks = [] #Keep track the player clicks
    gameOver = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() #(x,y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row,col): #The user click the same square twice
                        sqSelected = () #deselect
                        playerClicks = [] #clear player clicks
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected) #Append both 1st and 2nd click
                    if len(playerClicks) == 2 : #After 2nd click
                        move = EngineChess.Move(playerClicks[0],playerClicks[1],gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                #Pawn Promotion
                                if move.isPromotionPawn:
                                    print("Entrez q for Queen")
                                    print("Entrez r for Rook")
                                    print("Entrez b for Bishop")
                                    print("Entrez k for Knight")
                                    promotion = ""
                                    while promotion != "Q" and promotion != "R" and promotion != "B" and promotion != "N":
                                        promotion = input("").upper()
                                    gs.board[validMoves[i].endRow][validMoves[i].endCol] = validMoves[i].pieceMoved[0] + promotion
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                                playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #when pressed z undo Move
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = True
                    animate = False
                    if gameOver == True:
                        gameOver = False

                if e.key == p.K_r: #reset the board when 'r' is pressed
                    gs = EngineChess.GameState()
                    validMoves = gs.getValidMoves()
                    moveMade = False #flag variable for when a move is made
                    animate = False #flag variable for when we should animate a move
                    sqSelected = () #no square is selected, keep the track of the last click of the user (row,col)
                    playerClicks = [] #Keep track the player clicks
        
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1],screen,gs.board,time)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
        drawGameState(screen,gs, validMoves, sqSelected)
        
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen,'Black Wins by Checkmate')
            else:
                drawText(screen,'White Wins by Checkmate')
        elif gs.staleMate:
            gameOver = True
            drawText(screen,'StaleMate')

        time.tick(MAX_FPS)
        p.display.flip() #Update the full display Surface to the screen

"""
Responsable for all the graphics within a current game state.
"""
def drawGameState(screen,gs, validMoves, sqSelected):
    drawBoard(screen) #draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected) #highlighting or move suggestions.
    drawPieces(screen,gs.board) #draw pieces on top of the board

"""
Draw the squares on the board.
The top left square always white.
"""
def drawBoard(screen):
    global colors
    colors = [p.Color("white"),p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)] #it will pick the color based on the result 0 for white and 1 for gray
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))


"""
Draw the pieces on the board using the state GameCurrent.board
"""
def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                 # blit stands for Block Transfer—and it's going to copy the contents of one Surface onto another Surface .
                 screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

'''
Highlight square selected and moves for piece selected
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"): #Making sure that sqSelected is a piece that can be moved
            #Highlight selected square
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100) #Transperancy value -> 0 transparent; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            #Highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s,(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

'''
Animating a move
'''
def animateMove(move, screen, board, clock):
    global colors
    coords = [] #list of coords that animation will move through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 #frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r,c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece into rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved],p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont('Helvitca', 32, True, False)
    textObject = font.render(text, 2, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject,textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject,textLocation.move(2,2))

if __name__ == "__main__":
    main()
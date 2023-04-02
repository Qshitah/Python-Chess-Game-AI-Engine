# Python-Chess-Game-AI-Engine
Python Chess Game Using Pygame
UI improvements:
-Flip board options (display from black perspective)
-Change color of board/pieces - different piece skins
-Mouse click/drag for pieces
-Animation Moves
-Highlighting Moves 

Engine improvements:
-Add 50 move draw and 3 move repeating draw rule (Castling Rule/ En Passant)
-Move ordering - look at checks, captures and threats first, prioritize castling/king safety, look at pawn moves last (this will improve alpha-beta pruning). Also start with moves that previously scored higher (will also improve pruning).
-Calculate both players moves given a position
-Change move calculation to make it more efficient. Instead of recalculating all moves, start with moves from previous board and change based on last move made.
-Use a numpy array instead of 2d list of strings or store the board differently.
-Hash board positions already visited to improve computation time for transpositions.
-If move is a capture move, even at max depth, continue evaluating until no captures remain

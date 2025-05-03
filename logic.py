import pygame
import random
import copy


# ===== HELPER FUNCTIONS =====

def directions(x, y, minX=0, minY=0, maxX=7, maxY=7):
    """Check to determine which directions are valid from current cell

    # HOW IT WORKS:
    # Imagine you're standing on a square (x, y) on the board.
    # This function figures out all the neighbouring squares you could
    # possibly step onto (left, right, up, down, and diagonally)
    # without falling off the edge of the 8x8 board.
    # It returns a list of coordinates for these valid neighbouring squares.
    """
    validdirections = []
    if x != minX: validdirections.append((x - 1, y))  # Left
    if x != minX and y != minY: validdirections.append((x - 1, y - 1))  # Top-left
    if x != minX and y != maxY: validdirections.append((x - 1, y + 1))  # Bottom-left

    if x != maxX: validdirections.append((x + 1, y))  # Right
    if x != maxX and y != minY: validdirections.append((x + 1, y - 1))  # Top-right
    if x != maxX and y != maxY: validdirections.append((x + 1, y + 1))  # Bottom-right

    if y != minY: validdirections.append((x, y - 1))  # Up
    if y != maxY: validdirections.append((x, y + 1))  # Down

    return validdirections


def loadImages(path, size):
    """Load an image into the game, and scale the image

    # HOW IT WORKS:
    # Need to get a picture from a file into our game? This does the trick!
    # It loads the image file specified by 'path', resizes it to the given 'size',
    # and makes sure any transparent parts of the image stay transparent (`convert_alpha()`).
    """
    img = pygame.image.load(f"{path}").convert_alpha()
    img = pygame.transform.scale(img, size)
    return img


def loadSpriteSheet(sheet, row, col, newSize, size):
    """Creates an empty surface, loads a portion of the spritesheet onto the surface, then return that surface as img

    # HOW IT WORKS:
    # Sometimes, game artists pack lots of small images into one big image file
    # (called a spritesheet, like a sheet of stickers). This function is like a
    # precise pair of scissors: it cuts out just one specific small image
    # (at position row, col) from the big 'sheet', resizes it, and gives it back.
    """
    image = pygame.Surface((32, 32)).convert_alpha()
    image.blit(sheet, (0, 0), (row * size[0], col * size[1], size[0], size[1]))
    image = pygame.transform.scale(image, newSize)
    image.set_colorkey('Black')
    return image


# ===== GAME CLASSES =====

class Othello:
    """Main game class that handles the overall game loop and player turns

    # WHAT IT DOES:
    # This is the main control center for the entire Othello game.
    # It sets up the game window you see on the screen, keeps track of
    # whose turn it is, creates the game board, and manages the overall
    # flow of the game from start to finish.
    """

    def __init__(self):
        # Initialize pygame and create the game window
        pygame.init()
        self.screen = pygame.display.set_mode((1100, 800))
        pygame.display.set_caption('Othello')

        # Set up player tokens (1 = white, -1 = black)
        self.player1 = 1
        self.player2 = -1

        # White player (1) goes first
        self.currentPlayer = 1

        self.time = 0

        # Define board size (standard Othello is 8x8)
        self.rows = 8
        self.columns = 8

        # Create the game board
        self.grid = Grid(self.rows, self.columns, (80, 80), self)

        # Game is running
        self.RUN = True

    def run(self):
        """Main game loop - keeps running until the game ends

        # HOW IT WORKS:
        # This is the engine that keeps the game alive! It's a loop that
        # continuously does three things very quickly:
        # 1. Checks if you've done anything (like clicked the mouse).
        # 2. Updates the game's state based on what happened.
        # 3. Redraws everything on the screen.
        # This loop repeats until you close the game window.
        """
        while self.RUN == True:
            self.input()
            self.update()
            self.draw()

    def input(self):
        """Handle user inputs like mouse clicks

        # HOW IT WORKS:
        # This function listens for your actions, primarily mouse clicks.
        # - If you right-click, it prints the board's internal state (useful for debugging).
        # - If you left-click, it figures out which square you clicked on.
        #   - It checks if placing a piece there is a valid Othello move.
        #   - If it *is* valid, it places your piece, flips the opponent's pieces
        #     according to the rules, and then switches turns to the other player.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUN = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # Right mouse button
                    self.grid.printGameLogicBoard()

                if event.button == 1:  # Left mouse button
                    # Convert mouse position to grid coordinates
                    x, y = pygame.mouse.get_pos()
                    x, y = (x - 80) // 80, (y - 80) // 80

                    # Find all valid moves for current player
                    validCells = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)

                    if not validCells:
                        # No valid moves available
                        pass
                    else:
                        # Check if clicked cell is a valid move
                        if (y, x) in validCells:
                            # Place token
                            self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, y, x)

                            # Find which opponent tokens need to be flipped
                            swappableTiles = self.grid.swappableTiles(y, x, self.grid.gridLogic, self.currentPlayer)

                            # Flip those tokens with animation
                            for tile in swappableTiles:
                                self.grid.animateTransitions(tile, self.currentPlayer)
                                self.grid.gridLogic[tile[0]][tile[1]] *= -1

                            # Switch to other player's turn
                            self.currentPlayer *= -1
                            self.time = pygame.time.get_ticks()

    def update(self):
        """Update game state (not used in this implementation)

        # WHAT IT DOES:
        # This function is meant for things that need to happen continuously
        # in the background, like updating animations frame-by-frame or
        # maybe having a computer player think about its next move.
        # In this current version, it's empty, but it's here if needed later!
        """
        pass

    def draw(self):
        """Draw all game elements on screen

        # HOW IT WORKS:
        # Time to refresh the display! This function handles drawing everything
        # you see in the game window.
        # 1. It fills the background (currently black).
        # 2. It tells the 'grid' object to draw the board and all the pieces.
        # 3. Finally, it updates the screen to show the newly drawn picture.
        """
        self.screen.fill((0, 0, 0))
        self.grid.drawGrid(self.screen)
        pygame.display.update()


class Grid:
    """Represents the game board and handles board-related logic

    # WHAT IT DOES:
    # Think of this as the virtual game board. It doesn't just look like the board,
    # it also knows the rules! It handles:
    # - Keeping track of where every piece is (or if a square is empty).
    # - Figuring out where the current player can legally place a piece.
    # - Handling the flipping of pieces when they are captured.
    # - Drawing the board itself and all the pieces on it.
    """

    def __init__(self, rows, columns, size, main):
        self.GAME = main
        self.y = rows
        self.x = columns
        self.size = size

        # Load token images
        self.whitetoken = loadImages('assets/WhiteToken.png', size)
        self.blacktoken = loadImages('assets/BlackToken.png', size)

        # Load transition animation images (for flipping tokens)
        self.transitionWhiteToBlack = [loadImages(f'assets/BlackToWhite{i}.png', self.size) for i in range(1, 4)]
        self.transitionBlackToWhite = [loadImages(f'assets/WhiteToBlack{i}.png', self.size) for i in range(1, 4)]

        # Load background images
        self.bg = self.loadBackGroundImages()

        # Dictionary to store token objects
        self.tokens = {}

        # Create the board background image
        self.gridBg = self.createbgimg()

        # Create the logical representation of the board (what's actually in each space)
        self.gridLogic = self.regenGrid(self.y, self.x)

    def loadBackGroundImages(self):
        """Load background tile images from a spritesheet

        # HOW IT WORKS:
        # To make the board look like nice wood, we need different wood tile images.
        # This function loads a 'spritesheet' (one big image file containing many
        # smaller tile images) and uses the `loadSpriteSheet` helper function to
        # cut out all the individual wood tile pieces we'll need.
        """
        alpha = 'ABCDEFGHI'
        spriteSheet = pygame.image.load('assets/wood.png').convert_alpha()
        imageDict = {}
        for i in range(3):
            for j in range(7):
                imageDict[alpha[j] + str(i)] = loadSpriteSheet(spriteSheet, j, i, (self.size), (32, 32))
        return imageDict

    def createbgimg(self):
        """Create the game board background

        # HOW IT WORKS:
        # Let's build the visual background for our game board!
        # This function takes all those little wood tile images we loaded earlier
        # and arranges them in a grid pattern, like tiling a floor. It uses
        # different tiles for the edges to create a nice border effect.
        # The result is one big image of the complete, empty board background.
        """
        gridBg = [
            ['C0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'E0'],  # Top border
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],  # Alternating A/B tiles with borders
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'E2'],  # Bottom border
        ]
        image = pygame.Surface((960, 960))
        for j, row in enumerate(gridBg):
            for i, img in enumerate(row):
                image.blit(self.bg[img], (i * self.size[0], j * self.size[1]))
        return image

    def regenGrid(self, rows, columns):
        """Generate an empty grid for logic use

        # HOW IT WORKS:
        # This creates the internal "map" or "brain" of the game board.
        # It's basically a list of lists representing the rows and columns.
        # It starts by filling every square with 0 (meaning empty).
        # Then, it places the initial four Othello pieces in the center,
        # setting up the board for the start of the game.
        # (Remember: 1 means white piece, -1 means black piece, 0 is empty).
        """
        grid = []
        for y in range(rows):
            line = []
            for x in range(columns):
                line.append(0)
            grid.append(line)

        # Place the 4 starting tokens in the center
        self.insertToken(grid, 1, 3, 3)  # White at (3,3)
        self.insertToken(grid, -1, 3, 4)  # Black at (3,4)
        self.insertToken(grid, 1, 4, 4)  # White at (4,4)
        self.insertToken(grid, -1, 4, 3)  # Black at (4,3)

        return grid

    def drawGrid(self, window):
        """Draw the board and all tokens

        # HOW IT WORKS:
        # This function is responsible for drawing the current state of the game
        # onto the game window.
        # 1. It draws the wooden board background image first.
        # 2. Then, it goes through all the 'token' objects (the pieces) and tells
        #    each one to draw itself in its correct spot.
        # 3. Finally, it finds all the valid moves for the current player and draws
        #    small white rectangles on those squares as helpful hints.
        """
        window.blit(self.gridBg, (0, 0))

        # Draw all tokens
        for token in self.tokens.values():
            token.draw(window)

        # Show available moves for current player
        availMoves = self.findAvailMoves(self.gridLogic, self.GAME.currentPlayer)
        if self.GAME.currentPlayer == 1: # Only show hints for the human player (assuming white)
            for move in availMoves:
                # Draw a small white square hint in the middle of valid move cells
                pygame.draw.rect(window, 'White', (80 + (move[1] * 80) + 30, 80 + (move[0] * 80) + 30, 20, 20))


    def printGameLogicBoard(self):
        """Print the current board state to the console (for debugging)

        # WHAT IT DOES:
        # This is a handy tool for the programmer! It prints a simple text version
        # of the game board to the console (the text output window).
        # It shows 0 for empty, 1 for white, and -1 for black, making it easy
        # to see the exact state of the game's logic at any time.
        """
        print('  | A | B | C | D | E | F | G | H |')
        for i, row in enumerate(self.gridLogic):
            line = f'{i} |'.ljust(3, " ")
            for item in row:
                line += f"{item}".center(3, " ") + '|'
            print(line)
        print()

    def findValidCells(self, grid, curPlayer):
        """Performs a check to find all empty cells that are adjacent to opposing player

        # HOW IT WORKS (Part 1 of finding moves):
        # Before we figure out *exactly* where you can move, let's find the
        # possible *candidates*. This function scans the board for all empty squares (0)
        # that are directly next to (horizontally, vertically, or diagonally)
        # at least one of the *opponent's* pieces. These are potential places
        # for a valid move, but we'll need to check them more thoroughly later.
        """
        validCellToClick = []
        for gridX, row in enumerate(grid):
            for gridY, col in enumerate(row):
                # Skip if cell is not empty
                if grid[gridX][gridY] != 0:
                    continue

                # Check all directions from this cell
                DIRECTIONS = directions(gridX, gridY)

                for direction in DIRECTIONS:
                    dirX, dirY = direction
                    checkedCell = grid[dirX][dirY]

                    # Skip if adjacent cell is empty or belongs to current player
                    if checkedCell == 0 or checkedCell == curPlayer:
                        continue

                    # Add this cell as a potential move if not already added
                    if (gridX, gridY) in validCellToClick:
                        continue

                    validCellToClick.append((gridX, gridY))
        return validCellToClick

    def swappableTiles(self, x, y, grid, player):
        """Find all tokens that would be flipped if player places at position (x,y)

        # HOW IT WORKS (The core Othello capture rule):
        # This is where the magic happens! Given a potential move (at row x, column y)
        # for a 'player', this function figures out exactly which opponent pieces
        # would be flipped (captured).
        # It looks outwards from the potential move spot in all 8 directions.
        # If it finds a straight line of one or more opponent pieces *followed immediately
        # by one of the player's own pieces*, then all those opponent pieces in that
        # line are marked as 'swappable'. It returns a list of all swappable pieces.
        """
        surroundCells = directions(x, y)
        if len(surroundCells) == 0:
            return []

        swappableTiles = []
        for checkCell in surroundCells:
            checkX, checkY = checkCell
            difX, difY = checkX - x, checkY - y  # Direction to keep checking
            currentLine = []

            RUN = True
            while RUN:
                # If we find opponent's token, add it to potentially flippable tokens
                if grid[checkX][checkY] == player * -1:
                    currentLine.append((checkX, checkY))
                # If we find our own token, we can flip everything in between
                elif grid[checkX][checkY] == player:
                    RUN = False
                    break
                # If we find an empty space, we can't flip anything in this direction
                elif grid[checkX][checkY] == 0:
                    currentLine.clear()
                    RUN = False
                    break # Need to break here too!

                # Continue checking in the same direction
                checkX += difX
                checkY += difY

                # Stop if we go off the board
                if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                    currentLine.clear()
                    RUN = False

            # Add all flippable tokens from this direction to our total
            if len(currentLine) > 0:
                swappableTiles.extend(currentLine)

        return swappableTiles


    def findAvailMoves(self, grid, currentPlayer):
        """Takes the list of validCells and checks each to see if playable

        # HOW IT WORKS (Part 2 of finding moves):
        # Now we confirm which potential moves are *actually* valid.
        # 1. It first gets the list of candidate squares from `findValidCells`.
        # 2. Then, for each candidate square, it uses `swappableTiles` to check
        #    if placing a piece there would actually *flip* any opponent pieces.
        # 3. Only if placing a piece *does* flip at least one opponent piece,
        #    is the square considered a valid, playable move in Othello.
        # It returns a list of coordinates for all the truly valid moves.
        """
        validCells = self.findValidCells(grid, currentPlayer)
        playableCells = []

        for cell in validCells:
            x, y = cell
            # Skip if we already confirmed this cell is playable
            # (Might happen if it's adjacent to opponent pieces in multiple directions)
            if cell in playableCells:
                continue

            # Check which tokens would be flipped by placing here
            swapTiles = self.swappableTiles(x, y, grid, currentPlayer)

            # If at least one token would be flipped, this is a valid move
            if len(swapTiles) > 0:
                playableCells.append(cell)

        return playableCells


    def insertToken(self, grid, curplayer, y, x):
        """Place a new token on the board

        # HOW IT WORKS:
        # This function adds a new piece to the board.
        # It updates the game's internal map (`grid`) to record the new piece's
        # position and owner (`curplayer`). It also creates a visual `Token` object
        # (using the correct white or black image) and stores it so it can be drawn
        # on the screen later.
        """
        tokenImage = self.whitetoken if curplayer == 1 else self.blacktoken
        self.tokens[(y, x)] = Token(curplayer, y, x, tokenImage, self.GAME)
        grid[y][x] = self.tokens[(y, x)].player

    def animateTransitions(self, cell, player):
        """Animate token flipping when captured

        # HOW IT WORKS:
        # Adds a nice visual touch! When a piece (at coordinates `cell`)
        # gets captured by the `player`, this makes it look like it's flipping over.
        # It quickly shows a sequence of "in-between" images (like the piece
        # spinning) before settling on the final new color.
        """
        if player == 1: # If the capturing player is white, the captured piece turns white
            self.tokens[(cell[0], cell[1])].transition(self.transitionWhiteToBlack, self.whitetoken)
            self.tokens[(cell[0], cell[1])].player = 1 # Update the token's player attribute
        else: # If the capturing player is black, the captured piece turns black
            self.tokens[(cell[0], cell[1])].transition(self.transitionBlackToWhite, self.blacktoken)
            self.tokens[(cell[0], cell[1])].player = -1 # Update the token's player attribute


class Token:
    """Represents a single token (game piece) on the board

    # WHAT IT DOES:
    # This class represents a single Othello piece (either black or white)
    # that sits on the board. It holds information about:
    # - Which player it belongs to (1 for white, -1 for black).
    # - Its position on the board grid (row and column).
    # - The actual image used to draw it on the screen.
    # - How to animate it when it gets flipped.
    """

    def __init__(self, player, gridX, gridY, image, main):
        self.player = player  # 1 for white, -1 for black
        self.gridX = gridX  # Board position (row)
        self.gridY = gridY  # Board position (column)

        # Screen position (in pixels) - calculated based on grid position
        self.posX = 80 + (gridY * 80)
        self.posY = 80 + (gridX * 80)

        self.GAME = main # A link back to the main game object, needed for drawing animations
        self.image = image  # Token image to display (starts as either black or white)

    def transition(self, transitionImages, tokenImage):
        """Animate this token flipping to the opposite color

        # HOW IT WORKS:
        # This handles the visual animation for a *single* piece flipping over.
        # It rapidly cycles through a short list of `transitionImages` (showing
        # the piece part-way through its flip), redrawing the *entire* game screen
        # after showing each image to create the illusion of movement.
        # Finally, it sets the piece's `image` to the new final color (`tokenImage`).
        """
        # Show 3 transition frames, holding each for 10 loop cycles
        for i in range(30):
            self.image = transitionImages[i // 10]
            # We need to redraw the *whole game* screen each frame
            # to see the animation happening correctly.
            self.GAME.draw()
        # After the loop, set the final image for the token's new color
        self.image = tokenImage

    def draw(self, window):
        """Draw this token on the screen

        # HOW IT WORKS:
        # Nice and simple: This just takes the token's current image
        # (which might be white, black, or one of the transition images)
        # and draws it onto the game `window` at the token's calculated
        # screen position (`posX`, `posY`).
        """
        window.blit(self.image, (self.posX, self.posY))


# ===== PROGRAM ENTRY POINT =====
if __name__ == '__main__':
    """This is where the program starts running

    # WHAT HAPPENS HERE:
    # This special `if` block is the official starting point when you run this Python file.
    # 1. It creates a new instance of our main `Othello` game class.
    # 2. It calls the `run()` method on that game instance, which starts the main game loop.
    # 3. When the game loop eventually finishes (because the player closed the window),
    #    `pygame.quit()` is called to shut down the Pygame library cleanly.
    """
    game = Othello()
    game.run()
    pygame.quit()

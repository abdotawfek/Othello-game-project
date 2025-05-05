import pygame
import random
import copy

def directions(x, y, minX=0, minY=0, maxX=7, maxY=7):
    validdirections = []
    if x != minX: validdirections.append((x - 1, y))
    if x != minX and y != minY: validdirections.append((x - 1, y - 1))
    if x != minX and y != maxY: validdirections.append((x - 1, y + 1))
    if x != maxX: validdirections.append((x + 1, y))
    if x != maxX and y != minY: validdirections.append((x + 1, y - 1))
    if x != maxX and y != maxY: validdirections.append((x + 1, y + 1))
    if y != minY: validdirections.append((x, y - 1))
    if y != maxY: validdirections.append((x, y + 1))
    return validdirections

def loadImages(path, size):
    img = pygame.image.load(f"{path}").convert_alpha()
    img = pygame.transform.scale(img, size)
    return img

def loadSpriteSheet(sheet, row, col, newSize, size):
    image = pygame.Surface((32, 32)).convert_alpha()
    image.blit(sheet, (0, 0), (row * size[0], col * size[1], size[0], size[1]))
    image = pygame.transform.scale(image, newSize)
    image.set_colorkey('Black')
    return image

class Othello:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1100, 800))
        pygame.display.set_caption('Othello - Two Player')
        self.player1 = 1  # White
        self.player2 = -1  # Black
        self.currentPlayer = 1
        self.time = 0
        self.rows = 8
        self.columns = 8
        self.gameOver = False
        self.grid = Grid(self.rows, self.columns, (80, 80), self)
        self.RUN = True
        self.font = pygame.font.SysFont('Arial', 24, True, False)

    def run(self):
        while self.RUN == True:
            self.input()
            self.update()
            self.draw()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUN = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.grid.printGameLogicBoard()
                if event.button == 1 and not self.gameOver:
                    x, y = pygame.mouse.get_pos()
                    x, y = (x - 80) // 80, (y - 80) // 80
                    validCells = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)
                    if not validCells:
                        pass
                    else:
                        if (y, x) in validCells:
                            self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, y, x)
                            swappableTiles = self.grid.swappableTiles(y, x, self.grid.gridLogic, self.currentPlayer)
                            for tile in swappableTiles:
                                self.grid.animateTransitions(tile, self.currentPlayer)
                                self.grid.gridLogic[tile[0]][tile[1]] *= -1
                            self.currentPlayer *= -1
                if self.gameOver and event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    button_x_min = 390 + 80
                    button_x_max = 390 + 80 + 160
                    button_y_min = 240 + 160
                    button_y_max = 240 + 160 + 80
                    if button_x_min <= x <= button_x_max and button_y_min <= y <= button_y_max:
                        self.grid.newGame()
                        self.gameOver = False
                        self.currentPlayer = 1
                        self.time = pygame.time.get_ticks()

    def update(self):
        self.grid.player1Score = self.grid.calculatePlayerScore(self.player1)
        self.grid.player2Score = self.grid.calculatePlayerScore(self.player2)
        if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
            otherPlayer = self.currentPlayer * -1
            if not self.grid.findAvailMoves(self.grid.gridLogic, otherPlayer):
                self.gameOver = True
            else:
                self.currentPlayer = otherPlayer
                
                print(f"Player {'White' if self.currentPlayer == 1 else 'Black'}'s turn (no moves available for the other player)")

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.grid.drawGrid(self.screen)
        
        if not self.gameOver:
            turn_text = f"Current Turn: {'White' if self.currentPlayer == 1 else 'Black'}"
            turn_surface = self.font.render(turn_text, True, 'White')
            self.screen.blit(turn_surface, (900, 300))
        
        # Display if player needs to skip turn
        if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer) and not self.gameOver:
            skip_text = "No moves available. Click to skip."
            skip_surface = self.font.render(skip_text, True, 'Yellow')
            self.screen.blit(skip_surface, (750, 350))
            
        if self.gameOver:
            end_screen_img = self.grid.endScreen()
            end_screen_x = (1100 - 320) // 2
            end_screen_y = (800 - 320) // 2
            self.screen.blit(end_screen_img, (end_screen_x, end_screen_y))
        pygame.display.update()

class Grid:
    def __init__(self, rows, columns, size, main):
        self.GAME = main
        self.y = rows
        self.x = columns
        self.size = size
        self.whitetoken = loadImages('WhiteToken.png', size)
        self.blacktoken = loadImages('BlackToken.png', size)
        self.font = pygame.font.SysFont('Arial', 20, True, False)
        self.transitionWhiteToBlack = [loadImages(f'BlackToWhite{i}.png', self.size) for i in range(1, 4)]
        self.transitionBlackToWhite = [loadImages(f'WhiteToBlack{i}.png', self.size) for i in range(1, 4)]
        self.player1Score = 0
        self.player2Score = 0
        self.bg = self.loadBackGroundImages()
        self.tokens = {}
        self.gridBg = self.createbgimg()
        self.gridLogic = self.regenGrid(self.y, self.x)

    def newGame(self):
        self.tokens.clear()
        self.gridLogic = self.regenGrid(self.y,self.x)

    def loadBackGroundImages(self):
        alpha = 'ABCDEFGHI'
        spriteSheet = pygame.image.load('wood.png').convert_alpha()
        imageDict = {}
        for i in range(3):
            for j in range(7):
                imageDict[alpha[j] + str(i)] = loadSpriteSheet(spriteSheet, j, i, (self.size), (32, 32))
        return imageDict

    def endScreen(self):
        end_screen_img = pygame.Surface((320, 320))
        end_screen_img.fill((50, 50, 50))
        
        white_score = self.player1Score
        black_score = self.player2Score
        
        if white_score > black_score:
            winner_text = "White Player Wins!"
        elif black_score > white_score:
            winner_text = "Black Player Wins!"
        else:
            winner_text = "It's a Tie!"
            
        score_text = f"White: {white_score} - Black: {black_score}"
        
        end_text = self.font.render(winner_text, True, 'White')
        end_text_rect = end_text.get_rect(center=(160, 80))
        end_screen_img.blit(end_text, end_text_rect)
        
        score_display = self.font.render(score_text, True, 'White')
        score_rect = score_display.get_rect(center=(160, 120))
        end_screen_img.blit(score_display, score_rect)
        
        button_rect = pygame.Rect(80, 160, 160, 80)
        pygame.draw.rect(end_screen_img, 'White', button_rect)
        button_text = self.font.render('Play Again', True, 'Black')
        button_text_rect = button_text.get_rect(center=button_rect.center)
        end_screen_img.blit(button_text, button_text_rect)
        return end_screen_img

    def createbgimg(self):
        gridBg = [
            ['C0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'E0'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'E2'],
        ]
        image = pygame.Surface((960, 960))
        for j, row in enumerate(gridBg):
            for i, img in enumerate(row):
                image.blit(self.bg[img], (i * self.size[0], j * self.size[1]))
        return image

    def calculatePlayerScore(self, player):
        score = 0
        for row in self.gridLogic:
            for col in row:
                if col == player:
                    score += 1
        return score

    def regenGrid(self, rows, columns):
        grid = []
        for y in range(rows):
            line = []
            for x in range(columns):
                line.append(0)
            grid.append(line)
        self.insertToken(grid, 1, 3, 3)
        self.insertToken(grid, -1, 3, 4)
        self.insertToken(grid, 1, 4, 4)
        self.insertToken(grid, -1, 4, 3)
        return grid

    def drawScore(self, player, score):
        textImg = self.font.render(f'{player} : {score}', 1, 'White')
        return textImg

    def drawGrid(self, window):
        window.blit(self.gridBg, (0, 0))
        window.blit(self.drawScore('White', self.player1Score), (900, 100))
        window.blit(self.drawScore('Black', self.player2Score), (900, 200))
        for token in self.tokens.values():
            token.draw(window)
        availMoves = self.findAvailMoves(self.gridLogic, self.GAME.currentPlayer)
        for move in availMoves:
            highlight_color = 'White' if self.GAME.currentPlayer == 1 else 'Black'
            pygame.draw.rect(window, highlight_color, (80 + (move[1] * 80) + 30, 80 + (move[0] * 80) + 30, 20, 20))

    def printGameLogicBoard(self):
        print('  | A | B | C | D | E | F | G | H |')
        for i, row in enumerate(self.gridLogic):
            line = f'{i} |'.ljust(3, " ")
            for item in row:
                line += f"{item}".center(3, " ") + '|'
            print(line)
        print()

    def findValidCells(self, grid, curPlayer):
        validCellToClick = []
        for gridX, row in enumerate(grid):
            for gridY, col in enumerate(row):
                if grid[gridX][gridY] != 0:
                    continue
                DIRECTIONS = directions(gridX, gridY)
                for direction in DIRECTIONS:
                    dirX, dirY = direction
                    checkedCell = grid[dirX][dirY]
                    if checkedCell == 0 or checkedCell == curPlayer:
                        continue
                    if (gridX, gridY) in validCellToClick:
                        continue
                    validCellToClick.append((gridX, gridY))
        return validCellToClick

    def swappableTiles(self, x, y, grid, player):
        surroundCells = directions(x, y)
        if len(surroundCells) == 0:
            return []
        swappableTiles = []
        for checkCell in surroundCells:
            checkX, checkY = checkCell
            difX, difY = checkX - x, checkY - y
            currentLine = []
            RUN = True
            while RUN:
                if grid[checkX][checkY] == player * -1:
                    currentLine.append((checkX, checkY))
                elif grid[checkX][checkY] == player:
                    RUN = False
                    break
                elif grid[checkX][checkY] == 0:
                    currentLine.clear()
                    RUN = False
                    break
                checkX += difX
                checkY += difY
                if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                    currentLine.clear()
                    RUN = False
            if len(currentLine) > 0:
                swappableTiles.extend(currentLine)
        return swappableTiles

    def findAvailMoves(self, grid, currentPlayer):
        validCells = self.findValidCells(grid, currentPlayer)
        playableCells = []
        for cell in validCells:
            x, y = cell
            if cell in playableCells:
                continue
            swapTiles = self.swappableTiles(x, y, grid, currentPlayer)
            if len(swapTiles) > 0:
                playableCells.append(cell)
        return playableCells

    def insertToken(self, grid, curplayer, y, x):
        tokenImage = self.whitetoken if curplayer == 1 else self.blacktoken
        self.tokens[(y, x)] = Token(curplayer, y, x, tokenImage, self.GAME)
        grid[y][x] = self.tokens[(y, x)].player

    def animateTransitions(self, cell, player):
        if player == 1:
            self.tokens[(cell[0], cell[1])].transition(self.transitionWhiteToBlack, self.whitetoken)
            self.tokens[(cell[0], cell[1])].player = 1
        else:
            self.tokens[(cell[0], cell[1])].transition(self.transitionBlackToWhite, self.blacktoken)
            self.tokens[(cell[0], cell[1])].player = -1

class Token:
    def __init__(self, player, gridX, gridY, image, main):
        self.player = player
        self.gridX = gridX
        self.gridY = gridY
        self.posX = 80 + (gridY * 80)
        self.posY = 80 + (gridX * 80)
        self.GAME = main
        self.image = image

    def transition(self, transitionImages, tokenImage):
        for i in range(30):
            self.image = transitionImages[i // 10]
            self.GAME.draw()
        self.image = tokenImage

    def draw(self, window):
        window.blit(self.image, (self.posX, self.posY))

if __name__ == '__main__':
    game = Othello()
    game.run()
    pygame.quit()


import pygame
import random
import copy

def loadImages(path, size):
    img = pygame.image.load(f"{path}").convert_alpha()
    img = pygame.transform.scale(img,size)
    return img

# حته معقده سيكا
def loadspritesheet(sheet,row,col,newsize,size):
    image = pygame.Surface((32, 32)).convert_alpha() # دي كده قطعه واحده جاهزة من غير مكان فعلي
    image.blit(sheet, (0, 0), (row * size[0], col * size[1], size[0], size[1])) # هنا بتاخد القطعه الجاهزة وتحطها في مكانها 
    image = pygame.transform.scale(image, newsize) # هنا بتظبطها في مكانها حرفيا 
    image.set_colorkey('Black') # هنا بتحدد اللون الي هيكون شفاف
    return image

class Othello:
    def __init__ (self):
        pygame.init()
        # هنا كنا بنحهز المساحه الي هنشغل عليها البرنامج
        self.screen = pygame.display.set_mode((800,800))
        pygame.display.set_caption(" OTHELLO GAME ")
        # هنا بنحدد اللعبه شغاله ولا لا
        self.run = True
        self.rows = 8 # صفوف الرقعه
        self.columns = 8 # اعمدة الرقعه 
        self.grid = Grid( self.rows,self.columns,(80,80),self) #الرقعه نفسها 

    def Run(self):# هنا كنا بنعمل الداله الي اول مبنفتح البرنامج بتتنفذ 
        while self.run:
            self.Input()
            self.Update()
            self.Draw()
    
    def Input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # ده امر في حاله اللاعب كان عايز يقفل اللعبه 
                self.run = False
            if event.type == pygame.MOUSEBUTTONDOWN: # هنا بيشوف انت لو دست علي left_click
                if event.button == 1:
                    self.grid.printboard() # لو دست هيعرضلك الرقعه في حالتها الحاليه 
    
    def Update(self):
        pass
    
    def Draw(self):
        self.screen.fill((0,0,0)) 
        self.grid.drawGrid(self.screen) # بيستدعي داله ترسم الخلفيه بتاعت اللعبه
        pygame.display.update()
class Grid:
    def __init__(self,rows,columns,size,main):
        self.GAME = main # عمليه ربط بين Othello calss و Grid classs عن طريق main
        self.Y = rows
        self.X = columns
        self.size =size
        self.whitetoken = loadImages("D:\my project\WhiteToken.png", size)
        self.blacktoken = loadImages("D:\my project\BlackToken.png", size)
        self.transitionWhitetoBlack = [loadImages(f'D:\my project\BlacktoWhite{i}.png', self.size) for i in range(1,4)]
        self.transitionBlacktoWhite = [loadImages(f'D:\my project\WhitetoBlack{i}.png', self.size) for i in range(1,4)]
        self.bg = self.loadBGimages()
        self.gridBg = self.createbgimg()
        
        self.gridlogic = self.regenGrid(self.Y,self.X) # بتحفظ الرقعه الفعليه
    
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
    
    def regenGrid(self, rows,columns):
        grid = []
        for y in range(rows):
            line = []#كده انت بتعمل قائمه جديده كل مرة 
            for x in range(columns):
                line.append(0) # وهنا بتملاها اصفار لحد الاخر 
            grid.append(line) # وهنا بتعمل {{LIST OF LISTS}}   
        return grid # هنا بترجعها علي انها {[key][value]}
    
    def loadBGimages(self):
        alpha = "ABCDEFGHI"
        spritesheet = pygame.image.load("D:\my project\wood.png").convert_alpha() # convert_alpha is here for optimized performance
        imagedect  = {}
        for i in range(3):
            for j in range(7):
                imagedect[alpha[j]+str(i)] = loadspritesheet(spritesheet,j,i,(self.size),(32,32))
        return imagedect    
    
    def drawGrid(self, window):
        window.blit(self.gridBg, (0, 0))    # كماله drawgrid        

    def printboard(self):
        print("  | A | B | C | D | E | F | G | H | ")
        for i , row in enumerate(self.gridlogic): # enumerate بتساعدك عن طريق انها بترجع القيمه وقيمه العد كمان 
            line = f"{i} |".ljust(3, " ") # left_justify عشان القيمه تبقي بعيده عن الرقم الصف ب حد معين كل مرة 
            for item in row:
                line += f"{item}".center(3 , " ")+ "|" # center عشان القيمه تبقي متنصفه جوة مساحه محددة لكل قيمه 
            print(line)
        print()
if __name__ == "__main__":
    game = Othello()
    game.Run()
    pygame.quit()
           

import pygame as pg
import pygame.display as disp
import pygame.freetype as ft
import levels as lv
from functools import partial

pg.init()
screen = disp.set_mode((1280, 720))
clock = pg.time.Clock()
running = True
LettersLeft = 0

global INACTIVE, ACTIVE, CORRECT, BUTTON, BACKGROUND, BLACK
INACTIVE = pg.Color("white")
ACTIVE = pg.Color("skyblue")
CORRECT = pg.Color("green4")
BUTTON = pg.Color("blue4")
BACKGROUND = pg.Color("gray74")
BLACK = pg.Color("black")

global FONT1
FONT1 = ft.SysFont("Calibri", 50, False, False)

class Textbox:
    def __init__(self, x: int, y: int, width: int, height: int, textcolor: pg.Color, screen: pg.Surface):
        self.x = x
        self.y = y
        self.rect = pg.Rect(x, y, width, height)
        self.textcolor = textcolor
        self.screen = screen
        
        self.color = INACTIVE
        self.active = False

        self.text, self.textfield = "", pg.Surface

    def draw(self) -> None:
        pg.draw.rect(self.screen, self.color, self.rect)
        self.textfield, self.textrect = FONT1.render(self.text, self.textcolor)
        # Centrer tekst
        text_pos = (self.rect.x + (self.rect.width - self.textfield.get_width()) // 2,
                    self.rect.y + (self.rect.height - self.textfield.get_height()) // 2)
        self.screen.blit(self.textfield, text_pos)

    def check_events(self, event) -> None:
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos): # Håndterer aktivering af klik. Kan laves mere effektiv?
            self.active = not self.active
        if event.type == pg.MOUSEBUTTONDOWN and not self.rect.collidepoint(event.pos):
            self.active = False
        self.color = ACTIVE if self.active else INACTIVE

        if event.type == pg.KEYDOWN and self.active:
            if event.key not in (pg.K_RETURN, pg.K_SPACE, pg.K_BACKSPACE):
                self.text = event.unicode
            if event.key == pg.K_RETURN:
                self.checkcorrect()
        
        self.draw()
    
    def checkcorrect(self, correctarray) -> bool:
        if correctarray[self.x][self.y] == self.text:
            self.color = CORRECT
            LettersLeft -= 1
            return True
        else:
            self.text = ""
            return False
        

class Button:
    def __init__(self, coordinates: tuple, color: pg.Color, textcolor: pg.Color, width: int, height: int, screen, text: str, function):
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.width = width
        self.height = height
        self.rect = pg.Rect(self.x, self.y, self.width, self.height)

        self.color = color
        self.textcolor = textcolor
        self.text = text
        self.textfield = pg.Surface
        self.screen = screen

        self.function = function

    def draw(self):
        pg.draw.rect(self.screen, self.color, self.rect)

        if self.text != '':
            self.textfield, self.textrect = FONT1.render(self.text, self.textcolor)
            # Centrer tekst
            text_pos = (self.rect.x + (self.rect.width - self.textfield.get_width()) // 2,
                        self.rect.y + (self.rect.height - self.textfield.get_height()) // 2)
            self.screen.blit(self.textfield, text_pos)

    def event_check(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.function()
        

def show_grid(levelarray, list, gridsize):
    for y, row in enumerate(levelarray):
        for x, value in enumerate(row):
            if value == 1:
                box = Textbox(x*gridsize+200, y*gridsize+200, gridsize-2, gridsize-2, BLACK, screen)
                list.append(box)
                # print(x,y)
                # print(x*gridsize+200,y*gridsize+200)

def load_level(levelarray, list, gridsize, lvl: int, imagearray):
    show_grid(levelarray, list, gridsize)

    for line in imagearray:
        img = pg.image.load(imagepath(line[0])).convert()
        img = pg.transform.scale(img, (50, 50))
        screen.blit(img, line[1])
    # show images
        # -||-

def won(level):
    levelheight = len(level)
    levelwidth = len(level[0])
    global LettersLeft
    if LettersLeft == 0:
        for row in range(levelheight):
            for column in range(levelwidth):
                if level[row][column] !=0:
                    LettersLeft +=1
    
    if LettersLeft == 0:
        win_screen()
        # waitForUserPress()

def imagepath(filename: str):
    return f".\\images\\{filename}"

def main_screen(screen):
    """Kort, modulær startskærm. Returnerer valgt level (1..3) eller None ved luk."""
    clock_local = pg.time.Clock()
    W, H = screen.get_size()

    # Knappestørrelse + layout
    BW, BH, GAP = 160, 160, 40
    start_x = (W - (3 * BW + 2 * GAP)) // 2
    y = 200
    buttons = [pg.Rect(start_x + i * (BW + GAP), y, BW, BH) for i in range(3)]

    small = ft.SysFont("Calibri", 24)
    tiny = ft.SysFont("Calibri", 12)

    def draw_thumb(surf, r):
        t = pg.Rect(r.x + 20, r.y + 15, r.w - 40, r.h - 70)
        pg.draw.rect(surf, (210, 210, 210), t)
        pg.draw.line(surf, (180, 180, 180), t.topleft, t.bottomright, 2)
        pg.draw.line(surf, (180, 180, 180), t.topright, t.bottomleft, 2)

    def center_render(surf, text, font, color, y_pos):
        txt_surf, _ = font.render(text, color)
        surf.blit(txt_surf, (W // 2 - txt_surf.get_width() // 2, y_pos))

    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                return None
            if e.type == pg.KEYDOWN and e.key in (pg.K_1, pg.K_2, pg.K_3):
                try:
                    return int(e.unicode)
                except Exception:
                    pass
            if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                for idx, r in enumerate(buttons, 1):
                    if r.collidepoint(e.pos):
                        return idx

        # Tegning
        screen.fill(BACKGROUND)
        pg.draw.rect(screen, (220, 220, 220), (0, 0, W, 70))
        center_render(screen, "Krydsord", FONT1, BLACK, 20)
        center_render(screen, "Vælg et level og begynd det sjove", small, BLACK, 100)

        for i, r in enumerate(buttons, 1):
            pg.draw.rect(screen, (150, 150, 150), r.inflate(4, 4))
            pg.draw.rect(screen, (200, 200, 200), r)
            draw_thumb(screen, r)
            lbl_surf, _ = ft.SysFont("Calibri", 18).render(f"Level {i}", BLACK)
            screen.blit(lbl_surf, (r.centerx - lbl_surf.get_width() // 2, r.bottom - 28))
            pv_surf, _ = tiny.render("Lille preview", (130, 130, 130))
            screen.blit(pv_surf, (r.x + 8, r.y + 6))

        pg.display.flip()
        clock_local.tick(60)

def win_screen():
    screen.fill(BACKGROUND)
    win_textfield, win_rect = FONT1.render("Tillykke, du har vundet!",CORRECT)
    win_pos = (win_rect.x + (win_rect.width - win_textfield.get_width()) // 2,
               win_rect.y + (win_rect.height - win_textfield.get_height()) // 2)
    screen.blit(win_textfield, win_pos)

screen.fill((100,100,255)) #Baggrundsfarve

ft.Font.render_to(FONT1, screen, pg.Rect(500,50,300,300), "Hello World", BLACK, (255,255,255)) #Viser tekst på "screen"
    
# Tekstbokse
testgrid = [
    [0,1,1,0,1],
    [1,1,0,0,1],
    [0,1,0,1,1],
    [0,1,0,0,1],
    [0,1,1,1,1]
]
testgridsize: int = 30


testbox = Textbox(20,20,50,50,CORRECT,screen)
boxes = [testbox]

testbutton = Button((100, 100), CORRECT, BLACK, 100, 100, screen, "Test", win_screen)
showlevelbutton = Button((200, 100), CORRECT, BLACK, 100, 50, screen, "Vis level", partial(show_grid, lv.level1, boxes, testgridsize))
buttons = [testbutton, showlevelbutton]


for box in boxes:
    box.draw()
for button in buttons:
    button.draw()

load_level(lv.level1, boxes, 60, 2, lv.level1_images)

#Gameloop test
while running:
    clock.tick(60) # 60 FPS


    # Lyt efter input. Hvis spillet lukkes, stoppes spillet
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        for box in boxes: #Håndter textbokse
            box.check_events(event)
        for button in buttons: #Håndter knapper
            button.event_check(event)
    
    # Render

    disp.flip() #Render næste frame
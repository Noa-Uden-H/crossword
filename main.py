import pygame as pg
import pygame.display as disp
import pygame.freetype as ft

pg.init()
screen = disp.set_mode((1280, 720))
clock = pg.time.Clock()
running = True

global INACTIVE, ACTIVE, CORRECT, BUTTON, BACKGROUND, BLACK
INACTIVE = pg.Color("white")
ACTIVE = pg.Color("skyblue")
CORRECT = pg.Color("green4")
BUTTON = pg.Color("blue4")
BACKGROUND = pg.Color("gray74")
BLACK = pg.Color("black")

global FONT1
FONT1 = ft.SysFont("Calibri", 20, False, False)

class Textbox:
    def __init__(self, x=int, y=int, width=int, height=int, textcolor=pg.Color, screen=pg.Surface):
        self.x = x
        self.y = y
        self.rect = pg.Rect(x, y, width, height)
        self.textcolor = textcolor
        self.screen = screen
        
        self.color = INACTIVE
        self.active = False

        self.text, self.textrect = "", pg.rect
        self.textfield = pg.Surface

    def draw(self):
        self.textfield, self.textrect = FONT1.render(self.text, self.textcolor)
        self.screen.blit(self.textfield, self.rect)
        pg.draw.rect(self.screen, self.color, self.rect)

    def check_events(self, event):
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
    
    def checkcorrect(self):
        return
        

class Button:
    def x():
        return

def show_level():
    return

def won():
    return

def main_screen():
    return

def main():
    return

screen.fill((100,100,255)) #Baggrundsfarve

ft.Font.render_to(FONT1, screen, pg.Rect(500,50,300,300), "Hello World", BLACK, (255,255,255)) #Viser tekst på "screen"
    
# Tekstbokse
testbox = Textbox(20,20,50,50,CORRECT,screen)
boxes = [testbox]

#Gameloop test
while running:
    clock.tick(60) # 60 FPS

    # Lyt efter input. Hvis spillet lukkes, stoppes spillet
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        for box in boxes: #Håndter textbokse
            box.draw()
            box.check_events(event)
    
    # Render
    
    disp.flip() #Render næste frame
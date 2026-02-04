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

def toggle(var: bool):
    if var == False:
        var = True
    else:
        var = False

class Textbox:
    def __init__(self, x=int, y=int, width=int, height=int):
        self.x = x
        self.y = y
        self.rect = pg.Rect(x, y, width, height)
        self.textfield

    def x():
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

#Gameloop test
while running:
    clock.tick(60) # 60 FPS

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    screen.fill((100,100,255))

    # Render
    ft.Font.render_to(FONT1, screen, pg.Rect(50,50,200,200), "Calibri", BLACK, (255,255,255))
    disp.flip()
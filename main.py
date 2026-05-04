# =========================
# IMPORTS
# =========================
import pygame as pg
import pygame.display as disp
import pygame.freetype as ft
import levels as lv
from functools import partial


# =========================
# INITIALISERING
# =========================
pg.init()
screen = disp.set_mode((1280, 720))
clock = pg.time.Clock()
game_running = True
# Antal felter der stadig mangler at blive udfyldt korrekt
remaining_letters = 0

# =========================
# FARVER (DESIGN TIL ÆLDRE BRUGERE)
# =========================
COLOR_INACTIVE = pg.Color("white")        # tomt felt
COLOR_ACTIVE = pg.Color("skyblue")        # markeret felt
COLOR_CORRECT = pg.Color("green4")        # korrekt svar
COLOR_INCORRECT = pg.Color("red3")        # forkert svar
COLOR_BUTTON = pg.Color("blue4")          # knapper
COLOR_BACKGROUND = pg.Color("gray74")     # baggrund
COLOR_TEXT = pg.Color("black")            # standard tekst

# =========================
# FONT (STOR FOR LÆSBARHED)
# =========================
UI_FONT = ft.SysFont("Calibri", 50, False, False)

class Level():
    def __init__(self, level_nr, level_array):
        ...
        # Evt Lettersleft og running?

# =========================
# CROSSWORD CELL (ET FELT I GRID)
# =========================
class CrosswordCell:
    """
    Repræsenterer ét felt i krydsordet.
    Håndterer input, visning og korrekthed.
    """
    def __init__(self, x: int, y: int, width: int, height: int, textcolor: pg.Color, screen: pg.Surface) -> None:
        self.x = x
        self.y = y
        self.rect = pg.Rect(x, y, width, height)
        self.textcolor = textcolor
        self.screen = screen
        
        self.color = COLOR_INACTIVE
        self.is_active = False

        self.text, self.textfield = "", pg.Surface

    def draw(self) -> None:
        """
        Tegner cellen og dens bogstav på skærmen
        """
        pg.draw.rect(self.screen, self.color, self.rect)                        # Tegner selve rektanglet
        self.textfield, self.textrect = UI_FONT.render(self.text, self.textcolor) # Loader teksten (bogstavet)
        text_pos = (self.rect.x + (self.rect.width - self.textfield.get_width()) // 2,  # Centrer tekst
                    self.rect.y + (self.rect.height - self.textfield.get_height()) // 2)
        self.screen.blit(self.textfield, text_pos)                              # Tegner teksten

    def handle_events(self, event, solution_grid) -> None:
        """
        Håndterer klik og tastaturinput
        """
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):  # Håndterer aktivering af klik. Kan laves mere effektiv?
            self.is_active = not self.is_active
        if event.type == pg.MOUSEBUTTONDOWN and not self.rect.collidepoint(event.pos):
            self.is_active = False
        self.color = COLOR_ACTIVE if self.is_active else COLOR_INACTIVE

        if event.type == pg.KEYDOWN and self.is_active:                             # Håndterer indtastning
            if event.key not in (pg.K_RETURN, pg.K_SPACE, pg.K_BACKSPACE):
                self.text = event.unicode
            if event.key == pg.K_RETURN:
                self.check_answer(solution_grid)
        
        self.draw()
    
    def check_answer(self, correctarray) -> None:
        """
        Tjekker om bogstavet er korrekt i forhold til løsningen
        """
        global remaining_letters

        if correctarray[self.x][self.y] == self.text:   # Tag højde for gridsize
            self.color = COLOR_CORRECT
            remaining_letters -= 1
        else:
            self.text = ""
        
# =========================
# UI BUTTON (GENANVENDIG KNAP)
# =========================
class UI_Button:
    def __init__(self, coordinates: tuple, color: pg.Color, textcolor: pg.Color, width: int, height: int, screen, text: str, function):
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.width = width
        self.height = height
        self.rect = pg.Rect(self.x, self.y, self.width, self.height)

        self.base_color = color
        self.hover_color = pg.Color("dodgerblue3")

        self.textcolor = textcolor
        self.text = text
        self.textfield = pg.Surface
        self.screen = screen

        self.function = function

    def draw(self):
        """
        Tegner knappen med hover-effekt
        """
        mouse_pos = pg.mouse.get_pos()

        # Skift farve ved hover
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.base_color

        pg.draw.rect(self.screen, color, self.rect, border_radius=10)    # Tegner knappens rektangel

        # Tekst på knap
        if self.text != '': # Kører kun, hvis der er en tekst på knappen
            self.textfield, self.textrect = UI_FONT.render(self.text, self.textcolor)
            # Centrer tekst
            text_pos = (self.rect.x + (self.rect.width - self.textfield.get_width()) // 2,
                        self.rect.y + (self.rect.height - self.textfield.get_height()) // 2)
            self.screen.blit(self.textfield, text_pos)  # Tegner teksten

    def event_check(self, event):   # Checker, om knappen er blevet klikket på
        """
        Kalder funktion når knappen trykkes
        """
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.function()
        

# =========================
# GRID CREATION (CENTRERING AF KRYDSORD)
# =========================
def create_centered_crossword(level_layout, cell_size) -> list:  # Looper igennem levelarray og genererer en liste af Textbox-objekter for hvert felt med 1.
    """
    Opretter krydsords-grid og centrerer det på skærmen
    """
    cells = []

    # Beregn startposition så grid er centreret
    start_x = (1280 - len(level_layout[0]) * cell_size) // 2
    start_y = (720 - len(level_layout) * cell_size) // 2

    for y, row in enumerate(level_layout):
        for x, value in enumerate(row):
            if value == 1:
                box = CrosswordCell(
                    start_x + x * cell_size,
                    start_y + y * cell_size,
                    cell_size - 2,
                    cell_size - 2,
                    COLOR_TEXT,
                    screen
                    )
                cells.append(box)

    return cells

# =========================
# FEEDBACK BAR (TOPPEN AF SKÆRMEN)
# =========================
def render_feedback_bar(message, is_correct=True):
    """
    Viser feedback til spilleren (grøn = korrekt, rød = forkert)
    """

    color = COLOR_CORRECT if is_correct else COLOR_INCORRECT

    pg.draw.rect(screen, color, (0, 0, 1280, 60))

    text_surface, _ = UI_FONT.render(message, pg.Color("white"))
    screen.blit(text_surface, (20, 10))

# =========================
# START MENU
# =========================
def show_start_menu():
    """
    Startskærm hvor spilleren vælger level
    """
    screen.fill(COLOR_BACKGROUND)   #Rykket uden for while-loop (skal kun gøres en gang)

    while True:

        title, _ = UI_FONT.render("Krydsord", COLOR_TEXT)
        screen.blit(title, (500, 50))

        # Knapper til levels
        level_1_btn = UI_Button((300, 300), COLOR_BUTTON, COLOR_TEXT, 200, 80, screen, "Level 1", lambda: 1)
        level_2_btn = UI_Button((550, 300), COLOR_BUTTON, COLOR_TEXT, 200, 80, screen,  "Level 2", lambda: 2)

        buttons = [level_1_btn, level_2_btn]

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return None

            for btn in buttons:         # Ændret til kun et for-loop
                btn.event_check(event)  # Ændret til at bruge UI_Buttons indbyggede funktion event_check
                btn.draw()

        pg.display.flip()

# =========================
# GAMEPLAY LOOP (ET LEVEL)
# =========================
def play_crossword_level(level_data, solution_data):
    """
    Selve spillet hvor brugeren løser krydsordet
    """

    global remaining_letters, game_running

    cell_size = 60

    # Opret grid
    cells = create_centered_crossword(level_data, cell_size)

    # Hvor mange felter der skal udfyldes
    remaining_letters = sum(row.count(1) for row in level_data)

    hint_button = UI_Button((50, 650), COLOR_BUTTON, 200, 60, "Hint", lambda: print("Hint"))

    while True:
        screen.fill(COLOR_BACKGROUND)

        # Vis status
        render_feedback_bar(f"Tilbage: {remaining_letters}", True)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_running = False

            # Input til felter
            for cell in cells:
                cell.handle_event(event, solution_data)

            hint_button.handle_event(event)

        # Tegn grid
        for cell in cells:
            cell.draw()

        # Tegn knap
        hint_button.draw(screen)

        # Tjek om spillet er vundet
        if remaining_letters <= 0:
            show_win_screen()
            return

        pg.display.flip()
        clock.tick(60)

# =========================
# WIN SCREEN
# =========================
def show_win_screen():
    """
    Vises når spilleren har klaret krydsordet
    """

    screen.fill(COLOR_BACKGROUND)

    text, _ = UI_FONT.render("Tillykke, du vandt!", COLOR_CORRECT)
    screen.blit(text, (450, 300))

    pg.display.flip()
    pg.time.wait(2000)

# =========================
# MAIN LOOP (PROGRAM START)
# =========================
while game_running:

    chosen_level = show_start_menu()

    if chosen_level == 1:
        play_crossword_level(lv.level1, lv.level1_correct)

    elif chosen_level == 2:
        play_crossword_level(lv.level2, lv.level2_correct)

    else:
        game_running = False


def imagepath(filename: str):   # Tilføjer ".\images\" inden hvert billedes filnavn
    return f".\\images\\{filename}"

# ====================================
# Alt under her skal nok slettes - skal noget af det bruges?

def load_level(levelarray, list, gridsize, lvl: int, imagearray):
    create_centered_crossword(levelarray, list, gridsize)   # Laver griddet af tekstbokse

    for line in imagearray:                 # Laver billederne
        img = pg.image.load(imagepath(line[0])).convert()
        img = pg.transform.scale(img, (50, 50))
        screen.blit(img, line[1])

def calculate_remaining_letters(level):
    levelheight = len(level)
    levelwidth = len(level[0])
    global remaining_letters
    if remaining_letters == 0:
        for row in range(levelheight):
            for column in range(levelwidth):
                if level[row][column] !=0:
                    remaining_letters +=1
    
    if remaining_letters == 0:
        win_screen()

# def main_screen(screen):        # Omskriv med Button-class og evt sæt fonts under Globals
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
        screen.fill(COLOR_BACKGROUND)
        pg.draw.rect(screen, (220, 220, 220), (0, 0, W, 70))
        center_render(screen, "Krydsord", UI_FONT, COLOR_TEXT, 20)
        center_render(screen, "Vælg et level og begynd det sjove", small, COLOR_TEXT, 100)

        for i, r in enumerate(buttons, 1):
            pg.draw.rect(screen, (150, 150, 150), r.inflate(4, 4))
            pg.draw.rect(screen, (200, 200, 200), r)
            draw_thumb(screen, r)
            lbl_surf, _ = ft.SysFont("Calibri", 18).render(f"Level {i}", COLOR_TEXT)
            screen.blit(lbl_surf, (r.centerx - lbl_surf.get_width() // 2, r.bottom - 28))
            pv_surf, _ = tiny.render("Lille preview", (130, 130, 130))
            screen.blit(pv_surf, (r.x + 8, r.y + 6))

        pg.display.flip()
        clock_local.tick(60)

def win_screen():
    screen.fill(COLOR_BACKGROUND)
    win_textfield, win_rect = UI_FONT.render("Tillykke, du har vundet!",COLOR_CORRECT)
    win_pos = (win_rect.x + (win_rect.width - win_textfield.get_width()) // 2,
               win_rect.y + (win_rect.height - win_textfield.get_height()) // 2)
    screen.blit(win_textfield, win_pos)
    # Wait for user input and exit 

screen.fill((100,100,255)) #Baggrundsfarve

ft.Font.render_to(UI_FONT, screen, pg.Rect(500,50,300,300), "Hello World", COLOR_TEXT, (255,255,255)) #Viser tekst på "screen"
    
# Tekstbokse
testgrid = [
    [0,1,1,0,1],
    [1,1,0,0,1],
    [0,1,0,1,1],
    [0,1,0,0,1],
    [0,1,1,1,1]
]
testgridsize: int = 30


testbox = CrosswordCell(20,20,50,50,COLOR_CORRECT,screen)
boxes = [testbox]

testbutton = UI_Button((100, 100), COLOR_CORRECT, COLOR_TEXT, 100, 100, screen, "Test", win_screen)
showlevelbutton = UI_Button((200, 100), COLOR_CORRECT, COLOR_TEXT, 100, 50, screen, "Vis level", partial(create_centered_crossword, lv.level1, boxes, testgridsize))
buttons = [testbutton, showlevelbutton]

#Looper igennem hhv. box og button-listerne og tegner dem
for box in boxes:
    box.draw()
for button in buttons:
    button.draw()

load_level(lv.level1, boxes, 60, 2, lv.level1_images)

#Gameloop test
while game_running:
    clock.tick(60) # 60 FPS


    # Lyt efter input. Hvis spillet lukkes, stoppes spillet
    for event in pg.event.get():
        if event.type == pg.QUIT:
            game_running = False
        for box in boxes:               #Lyt efter events for boxes
            box.handle_events(event)     #Håndter textbokse
        for button in buttons:          #Lyt efter events for buttons
            button.event_check(event)   #Håndter knapper
    
    # Render

    disp.flip() #Render næste frame
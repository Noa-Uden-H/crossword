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
game_running: bool = True
cell_size: int = 60

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

# =========================
# LEVEL INFO
# =========================
class Level():
    """
    Gemmer information om levelet, spillet og "gamestate"
    """
    def __init__(self, level_nr):
        self.level_nr = level_nr
        self.remaining_letters: int = 0

        if level_nr == 1:
            self.level_data = lv.level1_array[0]
            self.solution_data = lv.level1_array[1]
            self.images_data = lv.level1_array[2]
        elif level_nr == 2:
            self.level_data = lv.level2_array[0]
            self.solution_data = lv.level2_array[1]
            self.images_data = lv.level2_array[2]
        else:
            raise Exception("Level doesn't exist")
        
        levelheight = len(self.level_data)
        levelwidth = len(self.level_data[0])
        for row in range(levelheight):
            for column in range(levelwidth):
                if self.level_data[row][column] !=0:
                    self.remaining_letters +=1


# =========================
# CROSSWORD CELL (ET FELT I GRID)
# =========================
class CrosswordCell:
    """
    Repræsenterer ét felt i krydsordet.
    Håndterer input, visning og korrekthed.
    """
    def __init__(self, x: int, y: int, start_x: int, start_y: int, width: int, height: int, textcolor: pg.Color, screen: pg.Surface) -> None:
        self.x = x
        self.y = y
        self.rect = pg.Rect(start_x + x * cell_size, start_y + y * cell_size, width, height)
        self.textcolor = textcolor
        self.screen = screen
        
        self.color = COLOR_INACTIVE
        self.is_active = False

        self.text, self.textfield = "", pg.Surface

    def draw(self) -> None:
        """
        Tegner cellen og dens bogstav på skærmen
        """
        pg.draw.rect(self.screen, self.color, self.rect)                                # Tegner selve rektanglet
        self.textfield, self.textrect = UI_FONT.render(self.text, self.textcolor)       # Loader teksten (bogstavet)
        text_pos = (self.rect.x + (self.rect.width - self.textfield.get_width()) // 2,  # Centrer tekst
                    self.rect.y + (self.rect.height - self.textfield.get_height()) // 2)
        self.screen.blit(self.textfield, text_pos)                                      # Tegner teksten

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

        if correctarray[self.y][self.x] == self.text:
            self.color = COLOR_CORRECT
            GAME.remaining_letters -= 1
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
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):  # Hvis knappen klikkes returneres funktionen
            return self.function()
        return None
        
def imagepath(filename: str):   # Tilføjer ".\images\" inden hvert billedes filnavn
    return f".\\images\\{filename}"

# =========================
# GRID CREATION (CENTRERING AF KRYDSORD)
# =========================
def create_centered_crossword() -> list:  # Looper igennem levelarray og genererer en liste af Textbox-objekter for hvert felt med 1.
    """
    Opretter krydsords-grid og centrerer det på skærmen
    """
    cells = []
    global GAME, cell_size

    # Beregn startposition så grid er centreret
    start_x = (1280 - len(GAME.level_data[0]) * cell_size) // 2
    start_y = ((720 - len(GAME.level_data) * cell_size) // 2) + 30 #Giver plads til billeder over griddet

    for y, row in enumerate(GAME.level_data):
        for x, value in enumerate(row):
            if value == 1:
                box = CrosswordCell(
                    x, y,
                    start_x, start_y,
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
def show_start_menu() -> int:
    """
    Startskærm hvor spilleren vælger level
    """
    screen.fill(COLOR_BACKGROUND)   #Rykket uden for while-loop (skal kun gøres en gang)
    global game_running

    while game_running:

        title, _ = UI_FONT.render("Krydsord", COLOR_TEXT)
        screen.blit(title, (500, 50))

        # Knapper til levels
        level_1_btn = UI_Button((300, 300), COLOR_BUTTON, COLOR_TEXT, 200, 80, screen, "Level 1", lambda: 1)
        level_2_btn = UI_Button((550, 300), COLOR_BUTTON, COLOR_TEXT, 200, 80, screen,  "Level 2", lambda: 2)

        buttons = [level_1_btn, level_2_btn]

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return None

            for btn in buttons:         # Loop igennem alle knapper og tjekker for events og tegner knapperne
                result = btn.event_check(event)
                btn.draw()
                if result is not None:
                    return result

        pg.display.flip()

# =========================
# GAMEPLAY LOOP (ET LEVEL)
# =========================
def play_crossword_level():
    """
    Selve spillet hvor brugeren løser krydsordet
    """

    global GAME, game_running

    # Opret grid
    cells = create_centered_crossword()

    hint_button = UI_Button((50, 650), COLOR_BUTTON, COLOR_TEXT, 200, 60, screen, "Hint", lambda: print("Hint"))
    
    screen.fill(COLOR_BACKGROUND)

    for line in GAME.images_data:                 # Laver billederne
        img = pg.image.load(imagepath(line[0])).convert()
        img = pg.transform.scale(img, (50, 50))
        screen.blit(img, line[1])

    while game_running:

        # Vis status
        render_feedback_bar(f"Tilbage: {GAME.remaining_letters}", True)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_running = False

            # Input til felter
            for cell in cells:
                cell.handle_events(event, GAME.solution_data)

            hint_button.event_check(event)

        # Tegn grid
        for cell in cells:
            cell.draw()

        # Tegn knap
        hint_button.draw()

        # Tjek om spillet er vundet
        if GAME.remaining_letters <= 0:
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
    GAME = Level(chosen_level)

    if chosen_level != None:
        play_crossword_level()
    else:
        game_running = False

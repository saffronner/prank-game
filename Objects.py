import pygame
from pygame.locals import *
from random import choice

TILE_SIZE = 50
MAP_TILEWIDTH, MAP_TILEHEIGHT = 10, 10
MAP_WIDTH, MAP_HEIGHT = TILE_SIZE * MAP_TILEWIDTH, TILE_SIZE * MAP_TILEHEIGHT
BG_COLOR = (255, 255, 255)
PLAYER_WIGGLE_EVENT = pygame.USEREVENT + 1
PLAYER_MOVE_EVENT = pygame.USEREVENT + 2


class Entity:
    def __init__(
        self,
        img: pygame.Surface,
        xpos: int,
        ypos: int,
        x_offset_px: int = 0,
        y_offset_px: int = 0,
    ) -> None:
        self.x_tilepos = xpos
        self.y_tilepos = ypos
        self.img = img
        self.x_offset_px = x_offset_px
        self.y_offset_px = y_offset_px

    def draw(self, screen: pygame.Surface) -> None:
        # // T_SIZE gets tile coord, * again gets pos
        left = self.x_tilepos * TILE_SIZE
        top = self.y_tilepos * TILE_SIZE
        screen.blit(self.img, (left + self.x_offset_px, top + self.y_offset_px))


class Fence(Entity):
    pass


pygame.font.init()
font = pygame.font.Font('assets/hero-speak.ttf', 14)
text = font.render('the creator of this game said they wanted to show you something cool.', True, (0,0,0), wraplength=MAP_WIDTH - 20)


class Interactable(Entity):
    def __init__(
        self,
        img: pygame.Surface,
        xpos: int,
        ypos: int,
        dialogue: list[str] = [""],
        x_offset_px: int = 0,
        y_offset_px: int = 0,
    ) -> None:
        self.x_tilepos = xpos
        self.y_tilepos = ypos
        self.img = img
        self.dialogue = dialogue
        self.dialogue_idx = -1
        self.waiting_to_talk = False
        self.x_offset_px = x_offset_px
        self.y_offset_px = y_offset_px
        self.lol = pygame.image.load("assets/image.jpg")

    def draw(self, screen: pygame.Surface) -> None:
        if self.dialogue_idx == 2:
            screen.blit(self.lol, (0,0))

        super().draw(screen)
    
        if self.dialogue_idx > -1:
            text = font.render(self.dialogue[self.dialogue_idx], True, (0,0,0), wraplength=MAP_WIDTH - 20)
            screen.blit(text, (10, (MAP_TILEHEIGHT - 3) * TILE_SIZE))

    def advance_dialogue(self) -> None:
        print("advanced")
        self.dialogue_idx += 1
        if self.dialogue_idx == len(self.dialogue):
            self.dialogue_idx = -1

    def interact(self) -> None:
        self.waiting_to_talk = True
        print("interacted!")

    # def __hash__(self) -> int:
    #     return hash((self.xpos, self.ypos))

    # def __eq__(self, __value: object) -> bool:
    #     """UNSAFE"""
    #     return self.xpos == __value.xpos and self.ypos == __value.ypos


class Player(Entity):
    def __init__(
        self,
        img: pygame.Surface,
        img_l: pygame.Surface,
        img_r: pygame.Surface,
        xpos: int,
        ypos: int,
    ) -> None:
        self.x_tilepos = xpos
        self.y_tilepos = ypos
        self.img = img
        self.img_idle = img
        self.img_rotleft = img_l
        self.img_rotright = img_r
        self.x_offset_px = -20
        self.y_offset_px = -20

        self.is_wiggling = False
        self.max_wiggles = 3
        self.wiggle_counter = 0

        self.path: list[tuple[int, int]] = [(0, 0)]
        self.path_idx: int = 0
        self.moving: bool = False

    def move(self):
        if self.path_idx == len(self.path):
            self.moving = False
        else:
            self.x_tilepos, self.y_tilepos = self.path[self.path_idx]
            self.path_idx += 1

    def move_withpath(self, path: list[tuple[int, int]]) -> None:
        self.path = path
        self.path_idx = 0
        pygame.time.set_timer(PLAYER_MOVE_EVENT, 200, len(path) + 1)
        self.moving = True

    def standingwiggle(self) -> None:
        if not self.is_wiggling:
            pygame.time.set_timer(PLAYER_WIGGLE_EVENT, 200, self.max_wiggles + 1)

    def wiggle(self) -> None:
        if not self.is_wiggling:
            self.img = choice((self.img_rotleft, self.img_rotright))
            self.is_wiggling = True
            self.wiggle_counter = self.max_wiggles
            return

        if self.img == self.img_rotleft:
            self.img = self.img_rotright
        else:
            self.img = self.img_rotleft

        self.wiggle_counter -= 1

        if self.wiggle_counter == 0:
            self.is_wiggling = False
            self.img = self.img_idle


class Menu:
    def __init__(self) -> None:
        pass


class GameState:
    def __init__(self) -> None:
        self.hborder = pygame.image.load("assets/horizontal_border.png")
        self.playing: bool = True
        self.pause_before_closing: bool = False
        self.player = Player(
            pygame.image.load("assets/wizard.png"),
            pygame.image.load("assets/wizard_rotleft.png"),
            pygame.image.load("assets/wizard_rotright.png"),
            xpos=0,
            ypos=0,
        )
        self.menu = Menu()
        self.wizard_img = pygame.image.load("assets/wizard.png")
        self.hover_img = pygame.image.load("assets/hover.png")
        self.interactables_lookup = dict()
        self.entities: list[Entity] = [
            Interactable(
                pygame.image.load("assets/guy.png"),
                xpos=5,
                ypos=5,
                dialogue=[
                    "hi!",
                    "the creator of this game said they wanted to show you something cool.",
                    "check this out!",
                ],
            ),
            self.player,
            Fence(pygame.image.load("assets/fence.png"), xpos=2, ypos=3),
            Fence(pygame.image.load("assets/fence.png"), xpos=3, ypos=3),
            Fence(pygame.image.load("assets/fence.png"), xpos=4, ypos=3),
        ]
        self.interactables: list[Interactable] = [
            self.entities[0]
        ]

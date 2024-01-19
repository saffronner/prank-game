from Objects import *
import pygame
from pygame.locals import *


class Queue:
    """unsafe but uh. probably marginally faster? queue implementation"""

    def __init__(self):
        self.front_idx = 0
        self.q = []

    def enq(self, item):
        self.q.append(item)

    def deq(self):
        """unsafe. requires `len(self.q) > 0` aka `not self.is_empty()"""
        self.front_idx += 1
        return self.q[self.front_idx - 1]

    def is_empty(self) -> bool:
        return len(self.q) == self.front_idx

    def __len__(self):
        return len(self.q) - self.front_idx


def pathfind(
    x_from: int, y_from: int, x_to: int, y_to: int, gamestate: GameState
) -> list[tuple[int, int]]:
    """note: for all 2d tuple coords and the `ignore` cache, t[0] is x and t[1] is y"""

    # set up cache: ignore and visited list
    ignore: list[list[bool]] = []
    for _ in range(MAP_TILEHEIGHT):
        ignore.append([False] * (MAP_TILEHEIGHT - 4))
        ignore[-1].extend([True] * 4)

    for en in gamestate.entities:
        ignore[en.x_tilepos][en.y_tilepos] = True

    if ignore[x_to][y_to]: # TODO move upwards?
        return None

    # set up q
    q: Queue = Queue()
    start_path: list[tuple[int, int]] = [(x_from, y_from)]
    q.enq(start_path)

    # bfs
    end: tuple[int, int] = (x_to, y_to)
    
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while not q.is_empty():
        path: list[tuple[int, int]] = q.deq()
        node: tuple[int, int] = path[-1]

        if node == end:
            return path

        for dx, dy in directions:
            # cull bad directions. assume entity only moves 1 tile at a time
            if dx == -1 and node[0] == 0:
                # continue if moving left when node's x is already 0. etc etc
                continue

            if dx == 1 and node[0] == MAP_TILEWIDTH - 1:
                continue

            if dy == -1 and node[1] == 0:
                continue

            if dy == 1 and node[1] == MAP_TILEHEIGHT - 1:
                continue

            new_x = node[0] + dx
            new_y = node[1] + dy

            if not ignore[new_x][new_y]:
                ignore[new_x][new_y] = True
                newpath = list(path)  # copy path
                newpath.append((new_x, new_y))
                q.enq(newpath)
    return None


def draw_mousehover(screen: pygame.Surface, img: pygame.Surface):
    mousex, mousey = pygame.mouse.get_pos()
    left = mousex // TILE_SIZE * TILE_SIZE
    top = mousey // TILE_SIZE * TILE_SIZE
    screen.blit(img, (left, top))
    # pygame.draw.rect(screen, (0, 0, 0), [left, top, TILE_SIZE, TILE_SIZE])


def update(dt, gamestate: GameState):
    """
    Update game. Called once per frame.
    dt is the amount of time passed since last frame.
    If you want to have constant apparent movement no matter your framerate,
    what you can do is something like

    x += v * dt

    and this will scale your velocity based on time. Extend as necessary."""

    for event in pygame.event.get():
        if event.type == QUIT:
            gamestate.playing = False
        elif event.type == PLAYER_MOVE_EVENT:
            gamestate.player.move()
        elif event.type == PLAYER_WIGGLE_EVENT:
            gamestate.player.wiggle()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if (
                x // TILE_SIZE == gamestate.player.x_tilepos
                and y // TILE_SIZE == gamestate.player.y_tilepos
            ):
                gamestate.player.standingwiggle()
            else:
                mousex, mousey = pygame.mouse.get_pos()
                left_tile = mousex // TILE_SIZE
                top_tile = mousey // TILE_SIZE 
                
                for inter in gamestate.interactables:
                    if inter.x_tilepos == left_tile and inter.y_tilepos == top_tile:
                        inter.interact()

                path = pathfind(gamestate.player.x_tilepos, gamestate.player.y_tilepos, left_tile, top_tile, gamestate)
                if path is not None:
                    gamestate.player.move_withpath(path)
                else:
                    backupleft = left_tile - 1
                    backuptop = top_tile + 0
                    if backupleft > 0:
                        path = pathfind(gamestate.player.x_tilepos, gamestate.player.y_tilepos, backupleft, backuptop, gamestate)
                    if path is not None:
                        gamestate.player.move_withpath(path)
                    else:
                        backupleft = left_tile + 1
                        backuptop = top_tile + 0
                        if backupleft < MAP_TILEWIDTH:
                            path = pathfind(gamestate.player.x_tilepos, gamestate.player.y_tilepos, backupleft, backuptop, gamestate)
                        if path is not None:
                            gamestate.player.move_withpath(path)
                        else:
                            backupleft = left_tile + 0
                            backuptop = top_tile - 1
                            if backuptop > 0:
                                path = pathfind(gamestate.player.x_tilepos, gamestate.player.y_tilepos, backupleft, backuptop, gamestate)
                            if path is not None:
                                gamestate.player.move_withpath(path)
                            else:
                                backupleft = left_tile + 0
                                backuptop = top_tile + 1
                                path = None
                                if backuptop < MAP_TILEHEIGHT:
                                    path = pathfind(gamestate.player.x_tilepos, gamestate.player.y_tilepos, backupleft, backuptop, gamestate)
                                if path is not None:
                                    gamestate.player.move_withpath(path)

                    
        elif event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_SPACE:
                    print("pressed space")

    for inter in gamestate.interactables:
        if inter.waiting_to_talk and not gamestate.player.moving:
            inter.waiting_to_talk = False
            inter.advance_dialogue()


def draw(screen: pygame.Surface, gamestate: GameState):
    """
    Draw things to the window. Called once per frame.
    """
    screen.fill(BG_COLOR)

    for en in gamestate.entities:
        en.draw(screen)

    draw_mousehover(screen, gamestate.hover_img)

    screen.blit(gamestate.hborder, (0, (MAP_TILEHEIGHT - 4) * TILE_SIZE))

    
    # create a text surface object,
    # on which text is drawn on it.
    # screen.blit(text, (10, (MAP_TILEHEIGHT - 3) * TILE_SIZE))

    pygame.display.update()


def main():
    gamestate = GameState()

    pygame.init()

    fps = 60.0
    fpsClock = pygame.time.Clock()

    screen = pygame.display.set_mode((MAP_WIDTH, MAP_HEIGHT), flags=0, vsync=1)
    # screen = pygame.display.set_mode((MAP_WIDTH, MAP_HEIGHT), flags=pygame.SCALED, vsync=1)
    screen.fill(BG_COLOR)
    pygame.display.update()

    dt = 1 / fps
    while gamestate.playing:
        update(dt, gamestate)
        draw(screen, gamestate)

        dt = fpsClock.tick(fps)

    if gamestate.pause_before_closing:
        fpsClock.tick(1)


if __name__ == "__main__":
    main()

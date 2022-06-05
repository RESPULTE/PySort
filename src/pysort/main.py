from collections import deque
from itertools import zip_longest
from pysort.lib import *

from typing import Callable, List, Tuple
import pygame
import random


pygame.init()
pygame.font.init()


class Settings:
    FPS = 60
    PADDING = 5

    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 700

    FONT = pygame.font.SysFont("Arial", 25)
    FONT_DEFAULT_COLOR = (255, 0, 255)
    FONT_HOVERED_COLOR = (0, 255, 255)
    FONT_CLICKED_COLOR = (0, 0, 0)

    SORTING_ALGORITHM_MENU_RECT = pygame.Rect(670, 100, 300, 400)

    BUTTON_DEAFULT_COLOR = (130, 17, 56)
    BUTTON_HOVERED_COLOR = (255, 0, 0)
    BUTTON_CLICKED_COLOR = (0, 0, 255)

    SORTING_DISPLAYER_RECT = pygame.Rect(25, 100, 600, 500)
    SORTING_DISPLAYER_COLUMN_COLOR_INITIAL = (13, 53, 156)
    SORTING_DISPLAYER_COLUMN_COLOR_END = (130, 200, 200)

    TITLE_RECT = pygame.Rect(100, 20, 800, 65)
    TITLE_FONT_COLOR = (0, 0, 100)
    BACKGROUND_COLOR = (255, 255, 255)


class Button(pygame.Surface):
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        container: "DropDownMenu",
        text: str = "",
        func: Callable = None,
    ) -> None:
        super().__init__((w, h))

        self.text = text
        self.func = func

        self.relative_pos = (x, y)
        self.container = container
        self._current_color = Settings.BUTTON_DEAFULT_COLOR
        self._current_font_color = Settings.FONT_DEFAULT_COLOR

        self.render()
        self.container.blit(self, (x, y))
        self.absolute_rect: pygame.Rect = self.get_rect(topleft=(x + container.x, y + container.y))

    def render(self) -> None:
        self.fill(self._current_color)
        font_surface = Settings.FONT.render(self.text, True, self._current_font_color)
        self.blit(font_surface, font_surface.get_rect(center=self.get_rect().center))

    def set_hovered(self) -> None:
        self._current_color = Settings.BUTTON_HOVERED_COLOR
        self._current_font_color = Settings.FONT_HOVERED_COLOR

        self.render()
        self.container.blit(self, self.relative_pos)

    def set_clicked(self) -> None:
        self._current_color = Settings.BUTTON_CLICKED_COLOR
        self._current_font_color = Settings.FONT_CLICKED_COLOR

        self.render()
        self.container.blit(self, self.relative_pos)

    def set_default(self) -> None:
        self._current_color = Settings.BUTTON_DEAFULT_COLOR
        self._current_font_color = Settings.FONT_DEFAULT_COLOR

        self.render()
        self.container.blit(self, self.relative_pos)


class DropDownMenu(pygame.Surface):
    def __init__(self, text_list: List[str], func_list: List[Callable], container: pygame.Surface, **kwargs) -> None:
        self.container = container
        self.x, self.y, self.w, self.h = Settings.SORTING_ALGORITHM_MENU_RECT
        super().__init__((self.w, self.h))

        self.buttons: List[Button] = []

        total_btn = len(func_list)
        btn_h = (self.h - (Settings.PADDING * (total_btn + 0.5))) // total_btn
        btn_x = btn_y = Settings.PADDING
        btn_w = self.w - Settings.PADDING * 2
        for text, fn in zip_longest(text_list, func_list, fillvalue=None):
            btn = Button(btn_x, btn_y, btn_w, btn_h, text=text, container=self, func=fn, **kwargs)
            btn_y += btn_h + Settings.PADDING
            self.buttons.append(btn)

        self.clicked_button: Button = None
        self.hovered_button: Button = None

        self.container.blit(self, (self.x, self.y))

    def query(self, x: int, y: int, clicked: bool = False) -> None:
        clicked_btn_func = None

        for btn in self.buttons:

            if btn is self.clicked_button:
                continue

            if not btn.absolute_rect.collidepoint(x, y):
                if btn is self.hovered_button:
                    btn.set_default()
                    self.hovered_button = None

            elif clicked:
                if self.clicked_button != None:
                    self.clicked_button.set_default()

                btn.set_clicked()
                self.clicked_button = btn
                self.hovered_button = None

                clicked_btn_func = btn.func

            elif btn is not self.hovered_button:
                if self.hovered_button != None:
                    self.hovered_button.set_default()

                btn.set_hovered()
                self.hovered_button = btn

            self.container.blit(self, (self.x, self.y))

        return clicked_btn_func


class Title(pygame.Surface):
    def __init__(self, container: pygame.Surface) -> None:
        self.x, self.y, self.w, self.h = Settings.TITLE_RECT
        super().__init__((self.w, self.h))
        self.container = container
        self.fill(Settings.BACKGROUND_COLOR)

    def set(self, text: str) -> None:
        self.fill(Settings.BACKGROUND_COLOR)
        font_surface = Settings.FONT.render("SELECTED: " + text, True, Settings.TITLE_FONT_COLOR)
        self.blit(font_surface, (self.x, (self.h - self.y) // 2))
        self.container.blit(self, (self.x, self.y))


class SortingDisplayer(pygame.Surface):
    def __init__(self, container: pygame.Surface) -> None:
        self.x, self.y, self.w, self.h = Settings.SORTING_DISPLAYER_RECT
        super().__init__((self.w, self.h))

        self.dataset = []
        self.dataset_size = 0
        self.sort_algo: Callable[[MutableSequence[CT]], Iterable] = None
        self.container = container

        self.generate_data(100)
        self.render()

    def start(self) -> None:
        sorter = self.sort_algo(self.dataset)
        clock = pygame.time.Clock()

        run = True
        while run:
            clock.tick(Settings.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        exhaust(sorter)

            try:
                next(sorter)
                self.render()
                pygame.display.update(Settings.SORTING_DISPLAYER_RECT)

            except StopIteration:
                self.render()
                pygame.display.update(Settings.SORTING_DISPLAYER_RECT)
                break

    def generate_data(self, n: int) -> List[int]:
        self.dataset_size = n
        self.dataset.clear()
        self.dataset.extend([random.randint(1, n) for _ in range(1, n + 1)])

    def render(self) -> None:
        self.fill((0, 0, 0))
        ir, ig, ib = Settings.SORTING_DISPLAYER_COLUMN_COLOR_INITIAL
        er, eg, eb = Settings.SORTING_DISPLAYER_COLUMN_COLOR_END
        dr, dg, db = er - ir, eg - ig, eb - ib

        x = 0
        w = self.w / self.dataset_size
        for data in self.dataset:
            ratio = data / self.dataset_size

            size = ratio * self.h
            y = self.h - size
            h = size

            color = (int(ratio * dr) + ir, int(ratio * dg) + ig, int(ratio * db) + ib)

            pygame.draw.rect(self, color, (x, y, w, h))
            x += w

        self.container.blit(self, (self.x, self.y))

    def set(self, sort_algo: Callable) -> None:
        self.sort_algo = sort_algo


def exhaust(iterable: Iterable) -> None:
    deque(iterable, 0)


def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((Settings.SCREEN_WIDTH, Settings.SCREEN_HEIGHT))
    screen.fill(Settings.BACKGROUND_COLOR)

    dataset_size = {
        10: "teeny-weeny",
        100: "meh",
        1_000: "average",
        10_000: "respectable",
        100_000: "humungous",
        1_000_000: "oh lawd",
    }
    sorting_algorithms = [bubble_sort, insertion_sort, selection_sort, merge_sort]
    for algo in sorting_algorithms:
        algo.__name__ = algo.__name__.replace("_", " ").upper()

    sorting_algorithm_names = [fn.__name__ for fn in sorting_algorithms]

    menu = DropDownMenu(text_list=sorting_algorithm_names, func_list=sorting_algorithms, container=screen)
    displayer = SortingDisplayer(container=screen)
    title = Title(container=screen)

    running = True
    start_sort = False
    screen.blit(title, (title.x, title.y))
    clock = pygame.time.Clock()
    while running:
        clock.tick(Settings.FPS)

        mouse_pos = pygame.mouse.get_pos()
        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    start_sort = True

        if not start_sort:
            sort_algo = menu.query(*mouse_pos, clicked=clicked)
            if sort_algo != None:
                displayer.set(sort_algo)
                title.set(sort_algo.__name__)
        else:
            displayer.start()
            start_sort = False

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

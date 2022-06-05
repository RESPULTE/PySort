from itertools import zip_longest
from pysort.lib import *

from typing import Callable, List, Tuple
import pygame
import random


class Settings:
    FPS = 60
    PADDING = 15

    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 700

    FONT = "Comic Sans MS"
    FONT_SIZE = 25
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
        self.default_color = Settings.BUTTON_DEAFULT_COLOR
        self.hovered_color = Settings.BUTTON_HOVERED_COLOR
        self.clicked_color = Settings.BUTTON_CLICKED_COLOR
        self._current_color = Settings.BUTTON_DEAFULT_COLOR

        self.text = text
        self.font = pygame.font.SysFont(Settings.FONT, Settings.FONT_SIZE)
        self.default_font_color = Settings.FONT_DEFAULT_COLOR
        self.clicked_font_color = Settings.FONT_CLICKED_COLOR
        self.hovered_font_color = Settings.FONT_HOVERED_COLOR
        self._current_font_color = Settings.FONT_DEFAULT_COLOR

        self.relative_pos = (x, y)
        self.container = container

        self.render()
        self.container.blit(self, (x, y))
        self.absolute_rect: pygame.Rect = self.get_rect(topleft=(x + container.x, y + container.y))

    def render(self) -> None:
        self.fill(self._current_color)
        font_surface = self.font.render(self.text, True, self._current_font_color)
        self.blit(font_surface, font_surface.get_rect(center=self.get_rect().center))

    def set_hovered(self) -> None:
        self._current_color = self.hovered_color
        self._current_font_color = self.hovered_font_color
        self.container.hovered_button = self

        self.render()
        self.container.blit(self, self.relative_pos)

    def set_clicked(self) -> None:
        self._current_color = self.clicked_color
        self._current_font_color = self.clicked_font_color
        self.container.clicked_button = self
        self.container.hovered_button = None

        self.render()
        self.container.blit(self, self.relative_pos)

    def set_default(self) -> None:
        self._current_color = self.default_color
        self._current_font_color = self.default_font_color

        self.render()
        self.container.blit(self, self.relative_pos)


class DropDownMenu(pygame.Surface):
    clicked_ms: int = 150

    def __init__(self, rect: pygame.Rect, text_list: List[str], func_list: List[Callable], **kwargs) -> None:
        x, y, w, h = rect
        self.x, self.y = x, y

        total_btn = len(func_list)
        btn_h = (h - (Settings.PADDING * (total_btn + 1))) // total_btn
        super().__init__((w, h))

        self.buttons: List[Button] = []
        btn_x = btn_y = Settings.PADDING
        btn_w = w - Settings.PADDING * 2
        for text, fn in zip_longest(text_list, func_list, fillvalue=None):
            btn = Button(btn_x, btn_y, btn_w, btn_h, text=text, container=self, func=fn, **kwargs)
            btn_y += btn_h + Settings.PADDING
            self.buttons.append(btn)

        self.clicked_button: Button = None
        self.hovered_button: Button = None

    def query(self, x: int, y: int, clicked: bool = False) -> None:
        for btn in self.buttons:

            if btn is self.clicked_button:
                continue

            if not btn.absolute_rect.collidepoint(x, y):
                if btn is self.hovered_button:
                    btn.set_default()
                continue

            if clicked:
                if self.clicked_button != None:
                    self.clicked_button.set_default()
                btn.set_clicked()
                return btn

            elif btn is not self.hovered_button:
                if self.hovered_button != None:
                    self.hovered_button.set_default()
                btn.set_hovered()


class SortingDisplayer(pygame.Surface):
    def __init__(self, container: pygame.Surface) -> None:
        self.x, self.y, self.w, self.h = Settings.SORTING_DISPLAYER_RECT
        super().__init__((self.w, self.h))

        self.dataset = []
        self.dataset_size = 0
        self.sort_algo = None
        self.container = container

        self.generate_data(100)
        self.render()

    def start(self) -> None:
        if self.sort_algo is None:
            raise Exception

    def generate_data(self, n: int) -> List[int]:
        self.dataset_size = n
        self.dataset.clear()
        self.dataset.extend([random.randint(1, n) for _ in range(1, n + 1)])

    def render(self) -> None:
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

    def set(self, sort_algo: Callable) -> None:
        self.sort_algo = sort_algo


def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((Settings.SCREEN_WIDTH, Settings.SCREEN_HEIGHT))

    dataset_size = {
        10: "teeny-weeny",
        100: "meh",
        1_000: "average",
        10_000: "respectable",
        100_000: "humungous",
        1_000_000: "oh lawd",
    }
    sorting_algorithms = [bubble_sort, insertion_sort, selection_sort]
    sorting_algorithm_names = [fn.__name__ for fn in sorting_algorithms]
    menu = DropDownMenu(
        rect=Settings.SORTING_ALGORITHM_MENU_RECT, text_list=sorting_algorithm_names, func_list=sorting_algorithms
    )
    displayer = SortingDisplayer(container=screen)

    running = True
    start_sort = False
    clock = pygame.time.Clock()
    while running:
        dt = clock.tick(Settings.FPS)

        screen.fill((255, 255, 255))

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

        screen.blit(menu, (menu.x, menu.y))
        screen.blit(displayer, (displayer.x, displayer.y))

        sort_algo = menu.query(*mouse_pos, clicked=clicked)
        if sort_algo != None:
            displayer.set(sort_algo)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

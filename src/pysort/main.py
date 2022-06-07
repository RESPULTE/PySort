from collections import deque
from itertools import zip_longest
from pysort.lib import *

from typing import Callable, List, Optional, Tuple
import itertools
import pygame
import random


pygame.init()
pygame.font.init()
# TODO:
# seperate the surfaces from one another in the displayer class, a seperate surface for guide messages, display & etc.
# clean up the setting's naming
# get tim sort done
# make it so that the sorting does not run in a seperate while loop from the main one


class Settings:
    FPS = 60
    PADDING = 5

    SMALL_DATASET = 50
    MEDIUM_DATASET = 200
    LARGE_DATASET = 1000

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
    SORTING_ALGORITHM_GUIDE_TEXT_1 = "PRESS ENTER TO START"
    SORTING_ALGORITHM_GUIDE_TEXT_2 = "SELECT DATASET SIZE"
    SORTING_ALGORITHM_GUIDE_TEXT_3 = "SELECT SORTING ALGORITHM"
    SORTING_ALGORITHM_GUIDE_TEXT_4 = "SORTING DONE"

    SORTING_ALGORITHM_GUIDE_TEXT_BACKGROUND_COLOR = (50, 37, 89)

    SORTING_DISPLAYER_COLUMN_COLOR_INITIAL = (13, 53, 156)
    SORTING_DISPLAYER_COLUMN_COLOR_END = (130, 200, 200)
    SORTING_ALGORITHM_COLUMN_COLOR_HIGHLIGHT = (255, 0, 0)

    TITLE_RECT = pygame.Rect(100, 20, 800, 65)
    TITLE_TEXT = "1: Small Dataset [50] | 2: Medium Dataset [200] | 3: Large Dataset [1000]"
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

    def update(self, x: int, y: int, clicked: bool = False) -> None:
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
    def __init__(self, container: pygame.Surface, text: str) -> None:
        self.x, self.y, self.w, self.h = Settings.TITLE_RECT
        super().__init__((self.w, self.h))
        self.container = container
        self.fill(Settings.BACKGROUND_COLOR)

        font_surface = Settings.FONT.render(text, True, Settings.TITLE_FONT_COLOR)
        self.blit(font_surface, (self.x, (self.h - self.y) // 2))
        self.container.blit(self, (self.x, self.y))


class SortingDisplayer(pygame.Surface):
    def __init__(self, container: pygame.Surface, n: int = 100) -> None:
        self.x, self.y, self.w, self.h = Settings.SORTING_DISPLAYER_RECT
        self.w *= 5
        self.h *= 5
        super().__init__((self.w, self.h))

        self.dataset = OperationLoggingList()
        self.dataset_size = 0
        self.sort_algo: Callable[[MutableSequence[CT]], None] = None
        self.sorter: Iterable = None
        self.container = container

        self.column_width = 0
        self.is_sorted = False
        self.sorting = False

        self.render_default(Settings.SORTING_ALGORITHM_GUIDE_TEXT_2)

    def start(self) -> None:
        if self.sort_algo is None:
            self.render_default(Settings.SORTING_ALGORITHM_GUIDE_TEXT_3)
            return

        elif self.dataset_size == 0:
            self.render_default(Settings.SORTING_ALGORITHM_GUIDE_TEXT_2)
            return

        self.sorter = self.sort_algo(self.dataset)
        self.sorting = True

    def sort(self) -> None:
        try:
            data_to_highlight = next(self.sorter)
            self.render(data_to_highlight)
            self.render_info()

        except StopIteration:
            self.render()
            self.render_default(Settings.SORTING_ALGORITHM_GUIDE_TEXT_4)
            self.render_info()
            self.dataset.reset()
            self.is_sorted = True
            self.sorting = False

    def render_dataset(self, n: int) -> None:
        self.dataset_size = n
        self.dataset.clear()
        self.dataset.extend(list(range(1, n + 1)))
        random.shuffle(self.dataset)

        self.column_width = self.w / self.dataset_size

        self.render()

    def render(self, data_to_highlight: Optional[int] = None) -> None:
        self.fill((0, 0, 0))
        ir, ig, ib = Settings.SORTING_DISPLAYER_COLUMN_COLOR_INITIAL
        er, eg, eb = Settings.SORTING_DISPLAYER_COLUMN_COLOR_END
        dr, dg, db = er - ir, eg - ig, eb - ib

        x = 0
        for data in self.dataset:
            ratio = data / self.dataset_size

            h = ratio * self.h
            y = self.h - h

            color = (int(ratio * dr) + ir, int(ratio * dg) + ig, int(ratio * db) + ib)
            pygame.draw.rect(self, color, (x, y, self.column_width, h))
            x += self.column_width

        if data_to_highlight != None:
            ratio = data_to_highlight / self.dataset_size

            h = ratio * self.h
            y = self.h - h

            x = self.dataset.index(data_to_highlight) * self.column_width
            pygame.draw.rect(self, Settings.SORTING_ALGORITHM_COLUMN_COLOR_HIGHLIGHT, (x, y, self.column_width, h))

        scaled_displayer = pygame.transform.scale(self, Settings.SORTING_DISPLAYER_RECT.size)
        self.container.blit(scaled_displayer, (self.x, self.y))

    def render_default(self, text: str) -> None:
        scaled_displayer = pygame.transform.scale(self, Settings.SORTING_DISPLAYER_RECT.size)
        font_surf = Settings.FONT.render(text, True, Settings.FONT_DEFAULT_COLOR)
        font_surf_rect = font_surf.get_rect(center=scaled_displayer.get_rect().center)
        pygame.draw.rect(
            scaled_displayer, Settings.SORTING_ALGORITHM_GUIDE_TEXT_BACKGROUND_COLOR, font_surf_rect.inflate(25, 25)
        )
        scaled_displayer.blit(font_surf, font_surf_rect.topleft)
        pygame.draw.rect(scaled_displayer, Settings.FONT_DEFAULT_COLOR, font_surf_rect.inflate(25, 25), 3)

        self.container.blit(scaled_displayer, (self.x, self.y))

    def render_info(self) -> None:
        scaled_displayer = pygame.transform.scale(self, Settings.SORTING_DISPLAYER_RECT.size)
        font_surf = Settings.FONT.render(
            f"array reads: {self.dataset.num_array_reads} | array writes: {self.dataset.num_array_write}",
            True,
            Settings.FONT_DEFAULT_COLOR,
        )
        font_surf_rect = font_surf.get_rect(topleft=scaled_displayer.get_rect().topleft)
        font_surf_rect.w += 25
        font_surf_rect.h += 25

        pygame.draw.rect(scaled_displayer, Settings.SORTING_ALGORITHM_GUIDE_TEXT_BACKGROUND_COLOR, font_surf_rect)
        scaled_displayer.blit(font_surf, font_surf.get_rect(center=font_surf_rect.center).topleft)
        pygame.draw.rect(scaled_displayer, Settings.FONT_DEFAULT_COLOR, font_surf_rect, 3)

        self.container.blit(scaled_displayer, (self.x, self.y))

    def reset_data(self) -> None:
        random.shuffle(self.dataset)
        self.render()

    def set(self, sort_algo: Callable) -> None:
        self.sort_algo = sort_algo
        if self.dataset_size != 0:
            self.render()
            self.render_default(Settings.SORTING_ALGORITHM_GUIDE_TEXT_1)

    def update(self) -> None:
        ...


def exhaust(iterable: Iterable) -> None:
    deque(iterable, 0)


def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((Settings.SCREEN_WIDTH, Settings.SCREEN_HEIGHT))
    screen.fill(Settings.BACKGROUND_COLOR)

    sorting_algorithms = [bubble_sort, insertion_sort, selection_sort, merge_sort, tim_sort]
    for algo in sorting_algorithms:
        algo.__name__ = algo.__name__.replace("_", " ").title()
    sorting_algorithm_names = [fn.__name__ for fn in sorting_algorithms]

    menu = DropDownMenu(text_list=sorting_algorithm_names, func_list=sorting_algorithms, container=screen)
    displayer = SortingDisplayer(container=screen)
    title = Title(container=screen, text=Settings.TITLE_TEXT)

    running = True
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
                    if displayer.sorting:
                        exhaust(displayer.sorter)
                    else:
                        displayer.start()

                if not displayer.sorting:
                    if event.key == pygame.K_1:
                        displayer.render_dataset(Settings.SMALL_DATASET)

                    elif event.key == pygame.K_2:
                        displayer.render_dataset(Settings.MEDIUM_DATASET)

                    elif event.key == pygame.K_3:
                        displayer.render_dataset(Settings.LARGE_DATASET)

        menu.update(*mouse_pos, clicked=clicked)

        if not displayer.sorting and menu.clicked_button != None:
            displayer.set(menu.clicked_button.func)

        if displayer.sorting:
            displayer.sort()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

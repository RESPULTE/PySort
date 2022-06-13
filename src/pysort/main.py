from functools import partial
from pysort.lib import *

from typing import Callable, List, Optional, Tuple
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

    SMALL_DATASET = 50
    MEDIUM_DATASET = 200
    LARGE_DATASET = 1000

    SCREEN_RECT_SIZE = (1000, 700)

    FONT = pygame.font.SysFont("Arial", 30)
    FONT_BACKGROUND_COLOR = (50, 37, 89)
    FONT_DEFAULT_COLOR = (255, 0, 255)
    FONT_HOVERED_COLOR = (255, 255, 255)
    FONT_CLICKED_COLOR = (255, 255, 255)

    BUTTON_HOVERED_COLOR = (195, 30, 0)
    BUTTON_CLICKED_COLOR = (0, 30, 195)

    MENU_RECT = pygame.Rect(740, 390, 250, 300)
    MENU_BACKGROUND_COLOR = (0, 0, 0)
    MENU_BUTTON_RECT_PADDING = 5

    SORTING_INFO_RECT_SIZE = (350, 35)
    SORTING_INFO_POSITION = "topleft"
    SORTING_DISPLAYER_RECT = pygame.Rect(0, 0, 3000, 2500)

    MESSAGE_RECT_SIZE = (300, 45)
    MESSAGE_RECT_PADDING = (25, 25)
    MESSAGE_POSITION = "center"
    MESSAGE_SORTING_DONE = "SORTING DONE"
    MESSAGE_PROMPT_TO_START = "PRESS ENTER TO START"
    MESSAGE_SELECT_DATASET_SIZE = "SELECT DATASET SIZE"
    MESSAGE_SELECT_SORTING_ALGORITHM = "SELECT SORTING ALGORITHM"

    COLOR_SCHEME_R = ((110, 13, 53), (200, 200, 130), (0, 255, 0))
    COLOR_SCHEME_G = ((10, 80, 20), (10, 224, 154), (255, 0, 255))
    COLOR_SCHEME_B = ((13, 53, 156), (130, 200, 200), (255, 0, 0))
    CURRENT_COLOR_SCHEME = COLOR_SCHEME_B

    GUIDE_RECT_SIZE = (500, 35)
    GUIDE_TEXT = "1: Small [50] | 2: Medium [200] | 3: Large [1000]"
    BACKGROUND_COLOR = (30, 30, 30)


def render_bordered_text(
    surface: pygame.Surface,
    text: str,
    size: tuple[int, int],
    pos: str,
    font_color: Tuple[int, int, int] = (0, 0, 0),
    bg_color: Tuple[int, int, int] = Settings.BACKGROUND_COLOR,
    border_color: Tuple[int, int, int] = Settings.BACKGROUND_COLOR,
    x: int = 0,
    y: int = 0,
) -> None:
    font_surf = Settings.FONT.render(text, True, font_color)
    font_surf = pygame.transform.scale(font_surf, size)

    surf_rect = surface.get_rect()
    font_surf_rect = font_surf.get_rect(center=getattr(surf_rect, pos))
    font_surf_rect.x += x
    font_surf_rect.y += y

    bg_font_surf_rect = font_surf_rect.inflate(Settings.MESSAGE_RECT_PADDING).clamp(surf_rect)
    font_surf_rect.center = bg_font_surf_rect.center

    pygame.draw.rect(surface, bg_color, bg_font_surf_rect)
    surface.blit(font_surf, font_surf_rect.topleft)
    pygame.draw.rect(surface, border_color, bg_font_surf_rect, 3)


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
        self.rect = self.get_rect()

        self.relative_pos = (x, y)
        self.container = container
        self._current_color = Settings.FONT_BACKGROUND_COLOR
        self._current_font_color = Settings.FONT_DEFAULT_COLOR

        self.render()
        self.container.blit(self, (x, y))
        self.absolute_rect: pygame.Rect = self.get_rect(topleft=(x + container.x, y + container.y))

    def render(self) -> None:
        self.fill(self._current_color)
        font_surface = Settings.FONT.render(self.text, True, self._current_font_color)
        self.blit(font_surface, font_surface.get_rect(center=self.rect.center))

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
        self._current_color = Settings.FONT_BACKGROUND_COLOR
        self._current_font_color = Settings.FONT_DEFAULT_COLOR

        self.render()
        self.container.blit(self, self.relative_pos)


class DropDownMenu(pygame.Surface):
    def __init__(self, text_list: List[str], func_list: List[Callable], container: pygame.Surface, **kwargs) -> None:
        self.container = container
        self.x, self.y, self.w, self.h = Settings.MENU_RECT
        super().__init__((self.w, self.h))
        self.fill(Settings.MENU_BACKGROUND_COLOR)

        self.buttons: List[Button] = []

        total_btn = len(func_list)
        btn_h = (self.h - (Settings.MENU_BUTTON_RECT_PADDING * (total_btn + 0.5))) // total_btn
        btn_w = self.w - Settings.MENU_BUTTON_RECT_PADDING * 2
        btn_x = btn_y = Settings.MENU_BUTTON_RECT_PADDING

        for text, fn in zip(text_list, func_list):
            btn = Button(btn_x, btn_y, btn_w, btn_h, text=text, container=self, func=fn, **kwargs)
            btn_y += btn_h + Settings.MENU_BUTTON_RECT_PADDING
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


class SortingDisplayer(pygame.Surface):
    def __init__(self, container: pygame.Surface) -> None:
        self.x, self.y, self.w, self.h = Settings.SORTING_DISPLAYER_RECT
        super().__init__((self.w, self.h))

        self.dataset_size = 0
        self.dataset = OperationLoggingList()
        self.container = container

        self.column_width = 0

        self.sorting = False
        self.sort_algo: Callable[[MutableSequence[CT]], None] = None
        self.sorter: Iterable = None

        self.message_renderer = partial(
            render_bordered_text,
            surface=self.container,
            size=Settings.MESSAGE_RECT_SIZE,
            pos=Settings.MESSAGE_POSITION,
            font_color=Settings.FONT_DEFAULT_COLOR,
            bg_color=Settings.FONT_BACKGROUND_COLOR,
            border_color=Settings.FONT_DEFAULT_COLOR,
        )

        self.info_renderer = partial(
            render_bordered_text,
            surface=self.container,
            size=Settings.SORTING_INFO_RECT_SIZE,
            pos=Settings.SORTING_INFO_POSITION,
            font_color=Settings.FONT_DEFAULT_COLOR,
            bg_color=Settings.FONT_BACKGROUND_COLOR,
            border_color=Settings.FONT_DEFAULT_COLOR,
        )

        self.message_renderer(text=Settings.MESSAGE_SELECT_DATASET_SIZE)

    def start(self) -> None:
        if self.dataset_size == 0:
            return

        elif self.sort_algo is None:
            self.message_renderer(text=Settings.MESSAGE_SELECT_SORTING_ALGORITHM)
            return

        self.sorter = self.sort_algo(self.dataset)
        self.sorting = True

    def sort(self) -> None:
        try:
            data_to_highlight = next(self.sorter)
            self.render(data_to_highlight)
            self.info_renderer(
                text=f"array reads: {self.dataset.num_array_reads} | array writes: {self.dataset.num_array_write}"
            )
        except StopIteration:
            self.render()
            self.message_renderer(text=Settings.MESSAGE_SORTING_DONE)
            self.info_renderer(
                text=f"array reads: {self.dataset.num_array_reads} | array writes: {self.dataset.num_array_write}"
            )

            self.dataset.reset()
            self.sorting = False

    def generate_data(self, n: int) -> None:
        if n == self.dataset_size:
            random.shuffle(self.dataset)
            return

        self.dataset_size = n
        self.dataset.clear()
        self.dataset.extend(list(range(1, n + 1)))
        random.shuffle(self.dataset)

        self.column_width = self.w / self.dataset_size

    def render(self, data_to_highlight: Optional[int] = None) -> None:
        self.fill(Settings.BACKGROUND_COLOR)

        ir, ig, ib = Settings.CURRENT_COLOR_SCHEME[0]
        er, eg, eb = Settings.CURRENT_COLOR_SCHEME[1]
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
            pygame.draw.rect(self, Settings.CURRENT_COLOR_SCHEME[2], (x, y, self.column_width, h))

        pygame.transform.scale(self, Settings.SCREEN_RECT_SIZE, self.container)

    def set_sort_algo(self, sort_algo: Callable) -> None:
        self.sort_algo = sort_algo
        if self.dataset_size != 0:
            self.message_renderer(text=Settings.MESSAGE_PROMPT_TO_START)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_RETURN:
            if self.sorting:
                exhaust(self.sorter)
            else:
                self.start()

        if not self.sorting:
            if event.key == pygame.K_1:
                self.generate_data(Settings.SMALL_DATASET)

            elif event.key == pygame.K_2:
                self.generate_data(Settings.MEDIUM_DATASET)

            elif event.key == pygame.K_3:
                self.generate_data(Settings.LARGE_DATASET)

        self.render()

    def update(self, new_sorting_func: Callable[[MutableSequence[CT]], None]) -> None:
        if not self.sorting:
            if new_sorting_func != None and new_sorting_func != self.sort_algo:
                self.set_sort_algo(new_sorting_func)
            return
        self.sort()


def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(Settings.SCREEN_RECT_SIZE)
    screen.fill(Settings.BACKGROUND_COLOR)

    sorting_algorithms = [
        bubble_sort,
        insertion_sort,
        selection_sort,
        merge_sort,
        tim_sort,
        radix_sort,
        quick_sort,
        iterative_quick_sort,
    ]
    for algo in sorting_algorithms:
        algo.__name__ = algo.__name__.replace("_", " ").title()
    sorting_algorithm_names = [fn.__name__ for fn in sorting_algorithms]

    menu = DropDownMenu(text_list=sorting_algorithm_names, func_list=sorting_algorithms, container=screen)
    displayer = SortingDisplayer(container=screen)

    running = True
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
                displayer.handle_event(event)

                if event.key == pygame.K_r:
                    Settings.CURRENT_COLOR_SCHEME = Settings.COLOR_SCHEME_R
                elif event.key == pygame.K_g:
                    Settings.CURRENT_COLOR_SCHEME = Settings.COLOR_SCHEME_G
                elif event.key == pygame.K_b:
                    Settings.CURRENT_COLOR_SCHEME = Settings.COLOR_SCHEME_B

        new_sorting_algo = menu.update(*mouse_pos, clicked=clicked)
        displayer.update(new_sorting_algo)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

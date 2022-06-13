from typing import TYPE_CHECKING, Callable, List, Tuple, MutableSequence, Iterable
import pygame
import random

import vizsort.lib

if TYPE_CHECKING:
    from vizsort.lib._type_hint import CT


class Settings:
    FPS = 60
    CAPTION = "VizSort"
    BACKGROUND_COLOR = (30, 30, 30)
    SCREEN_RECT_SIZE = (1000, 700)

    SMALL_DATASET = 50
    MEDIUM_DATASET = 200
    LARGE_DATASET = 1000

    COLOR_SCHEME_R = ((110, 13, 53), (200, 200, 130), (0, 255, 0))
    COLOR_SCHEME_G = ((10, 80, 20), (10, 224, 154), (255, 0, 255))
    COLOR_SCHEME_B = ((13, 53, 156), (130, 200, 200), (255, 0, 0))
    CURRENT_COLOR_SCHEME = COLOR_SCHEME_B

    FONT_NAME = "Arial"
    FONT_SIZE = 30
    FONT: pygame.font.Font = None

    FONT_BACKGROUND_COLOR = (50, 37, 89)
    FONT_DEFAULT_COLOR = (255, 0, 255)
    FONT_HOVERED_COLOR = (255, 255, 255)
    FONT_CLICKED_COLOR = (255, 255, 255)

    BUTTON_HOVERED_COLOR = (195, 30, 0)
    BUTTON_CLICKED_COLOR = (0, 30, 195)

    MENU_SORTING_ALGO_RECT = (740, 370, 250, 320)
    MENU_DATASET_SIZE_RECT = (10, 640, 350, 50)

    MENU_BACKGROUND_COLOR = (0, 0, 0)
    MENU_BUTTON_RECT_PADDING = 5

    SORTING_INFO_POSITION = "topleft"
    SORTING_DISPLAYER_RECT = (0, 0, 3000, 2500)

    MESSAGE_RECT_PADDING = (25, 25)
    MESSAGE_POSITION = "center"
    MESSAGE_SORTING_DONE = "SORTING DONE"
    MESSAGE_PROMPT_TO_START = "PRESS ENTER TO START"
    MESSAGE_SELECT_DATASET_SIZE = "SELECT DATASET SIZE"
    MESSAGE_SELECT_SORTING_ALGORITHM = "SELECT SORTING ALGORITHM"


def render_bordered_text(
    surface: pygame.Surface,
    text: str,
    pos: str,
    font_color: Tuple[int, int, int] = (0, 0, 0),
    bg_color: Tuple[int, int, int] = Settings.BACKGROUND_COLOR,
    border_color: Tuple[int, int, int] = Settings.BACKGROUND_COLOR,
    x: int = 0,
    y: int = 0,
) -> None:
    font_surf = Settings.FONT.render(text, True, font_color)

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
        container: "Menu",
        text: str = "",
        retval: Callable = None,
    ) -> None:
        super().__init__((w, h))

        self.text = text
        self.retval = retval
        self.rect = self.get_rect()

        self.relative_pos = (x, y)
        self.container = container
        self.absolute_rect: pygame.Rect = self.get_rect(topleft=(x + container.x, y + container.y))

        self._current_color = Settings.FONT_BACKGROUND_COLOR
        self._current_font_color = Settings.FONT_DEFAULT_COLOR

        self.render()

    def render(self) -> None:
        self.fill(self._current_color)
        font_surface = Settings.FONT.render(self.text, True, self._current_font_color)
        self.blit(font_surface, font_surface.get_rect(center=self.rect.center))
        self.container.blit(self, self.relative_pos)

    def set_hovered(self) -> None:
        self._current_color = Settings.BUTTON_HOVERED_COLOR
        self._current_font_color = Settings.FONT_HOVERED_COLOR

        self.render()

    def set_clicked(self) -> None:
        self._current_color = Settings.BUTTON_CLICKED_COLOR
        self._current_font_color = Settings.FONT_CLICKED_COLOR

        self.render()

    def set_default(self) -> None:
        self._current_color = Settings.FONT_BACKGROUND_COLOR
        self._current_font_color = Settings.FONT_DEFAULT_COLOR

        self.render()


class Menu(pygame.Surface):
    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        text_list: List[str],
        retval_list: List[Callable],
        container: pygame.Surface,
        horizontal: bool = True,
    ) -> None:
        self.container = container
        self.x, self.y, self.w, self.h = rect
        super().__init__((self.w, self.h))
        self.fill(Settings.MENU_BACKGROUND_COLOR)

        self.buttons: List[Button] = []
        self.clicked_button: Button = None
        self.hovered_button: Button = None

        if horizontal:
            self.set_horizontal(text_list, retval_list)
            return

        self.set_vertical(text_list, retval_list)

    def update(self, x: int, y: int, clicked: bool = False) -> None:
        clicked_btn_retval = None
        for btn in self.buttons:

            if not btn.absolute_rect.collidepoint(x, y):
                if btn is self.hovered_button:
                    btn.set_default()
                    self.hovered_button = None

            elif clicked:
                if btn is not self.clicked_button:
                    if self.clicked_button != None:
                        self.clicked_button.set_default()
                    btn.set_clicked()
                    self.clicked_button = btn

                self.hovered_button = None
                clicked_btn_retval = btn.retval

            elif btn not in (self.hovered_button, self.clicked_button):
                if self.hovered_button != None:
                    self.hovered_button.set_default()

                btn.set_hovered()
                self.hovered_button = btn

            self.container.blit(self, (self.x, self.y))

        return clicked_btn_retval

    def render(self) -> None:
        self.container.blit(self, (self.x, self.y))

    def set_horizontal(self, text_list, retval_list) -> None:
        total_btn = len(retval_list)
        btn_w = (self.w - (Settings.MENU_BUTTON_RECT_PADDING * (total_btn + 0.5))) // total_btn
        btn_h = self.h - Settings.MENU_BUTTON_RECT_PADDING * 2
        btn_x = btn_y = Settings.MENU_BUTTON_RECT_PADDING

        for text, val in zip(text_list, retval_list):
            btn = Button(btn_x, btn_y, btn_w, btn_h, text=text, container=self, retval=val)
            btn_x += btn_w + Settings.MENU_BUTTON_RECT_PADDING
            self.buttons.append(btn)

        self.container.blit(self, (self.x, self.y))

    def set_vertical(self, text_list, retval_list) -> None:
        total_btn = len(retval_list)
        btn_h = (self.h - (Settings.MENU_BUTTON_RECT_PADDING * (total_btn + 0.5))) // total_btn
        btn_w = self.w - Settings.MENU_BUTTON_RECT_PADDING * 2
        btn_x = btn_y = Settings.MENU_BUTTON_RECT_PADDING

        for text, fn in zip(text_list, retval_list):
            btn = Button(btn_x, btn_y, btn_w, btn_h, text=text, container=self, retval=fn)
            btn_y += btn_h + Settings.MENU_BUTTON_RECT_PADDING
            self.buttons.append(btn)

        self.container.blit(self, (self.x, self.y))


class SortingDisplayer(pygame.Surface):
    def __init__(self, container: pygame.Surface) -> None:
        self.x, self.y, self.w, self.h = Settings.SORTING_DISPLAYER_RECT
        super().__init__((self.w, self.h))

        self.dataset_size = 0
        self.dataset = vizsort.lib.OperationLoggingList()
        self.container = container

        self.column_width = 0
        self.column_to_hightlight = None

        self.sorting = False
        self.sort_algo: Callable[[MutableSequence["CT"]], None] = None
        self.sorter: Iterable = None

        self.message = None
        self.info = None

        self.message = Settings.MESSAGE_SELECT_DATASET_SIZE

    def start(self) -> None:
        if self.dataset_size == 0:
            return

        elif self.sort_algo is None:
            self.message = Settings.MESSAGE_SELECT_SORTING_ALGORITHM
            return

        self.sorter = self.sort_algo(self.dataset)
        self.message = None
        self.sorting = True

    def sort(self) -> None:
        try:
            self.column_to_hightlight = next(self.sorter)
            self.info = f"array reads: {self.dataset.num_array_reads} | array writes: {self.dataset.num_array_write}"

        except StopIteration:
            self.message = Settings.MESSAGE_SORTING_DONE
            self.info = f"array reads: {self.dataset.num_array_reads} | array writes: {self.dataset.num_array_write}"

            self.dataset.reset()
            self.column_to_hightlight = None
            self.sorting = False

    def generate_data(self, n: int) -> None:
        self.message = (
            Settings.MESSAGE_SELECT_SORTING_ALGORITHM if self.sort_algo is None else Settings.MESSAGE_PROMPT_TO_START
        )

        if n == self.dataset_size:
            random.shuffle(self.dataset)
            return

        self.dataset_size = n
        self.dataset.clear()
        self.dataset.extend(list(range(1, n + 1)))
        random.shuffle(self.dataset)

        self.column_width = self.w / self.dataset_size

    def render(self) -> None:
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

        if self.column_to_hightlight != None:
            ratio = self.column_to_hightlight / self.dataset_size

            h = ratio * self.h
            y = self.h - h

            x = self.dataset.index(self.column_to_hightlight) * self.column_width
            pygame.draw.rect(self, Settings.CURRENT_COLOR_SCHEME[2], (x, y, self.column_width, h))

        pygame.transform.scale(self, Settings.SCREEN_RECT_SIZE, self.container)

        if self.message:
            render_bordered_text(
                surface=self.container,
                text=self.message,
                pos=Settings.MESSAGE_POSITION,
                font_color=Settings.FONT_DEFAULT_COLOR,
                bg_color=Settings.FONT_BACKGROUND_COLOR,
                border_color=Settings.FONT_DEFAULT_COLOR,
            )
        if self.info:
            render_bordered_text(
                surface=self.container,
                text=self.info,
                pos=Settings.SORTING_INFO_POSITION,
                font_color=Settings.FONT_DEFAULT_COLOR,
                bg_color=Settings.FONT_BACKGROUND_COLOR,
                border_color=Settings.FONT_DEFAULT_COLOR,
            )

    def set_sort_algo(self, sort_algo: Callable) -> None:
        self.sort_algo = sort_algo
        if self.dataset_size != 0:
            self.message = Settings.MESSAGE_PROMPT_TO_START

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.key != pygame.K_RETURN:
            return

        if self.sorting:
            vizsort.lib.exhaust(self.sorter)
            return

        self.start()

    def update(self, new_sorting_func: Callable[[MutableSequence["CT"]], None], new_dataset_size: int) -> None:
        if self.sorting:
            self.sort()

        if new_sorting_func != None and new_sorting_func != self.sort_algo:
            self.set_sort_algo(new_sorting_func)
        if new_dataset_size != None:
            self.generate_data(new_dataset_size)


def main():
    pygame.init()
    pygame.font.init()
    Settings.FONT = pygame.font.SysFont(Settings.FONT_NAME, Settings.FONT_SIZE)

    screen = pygame.display.set_mode(Settings.SCREEN_RECT_SIZE)
    pygame.display.set_caption(Settings.CAPTION)
    screen.fill(Settings.BACKGROUND_COLOR)

    sorting_algorithm_info = [
        (k.replace("_", " ").title(), v) for k, v in vizsort.lib.__dict__.items() if k.endswith("_sort") and callable(v)
    ]

    sorting_algorithm_names, sorting_algorithms = map(list, zip(*sorting_algorithm_info))
    algo_menu = Menu(
        rect=Settings.MENU_SORTING_ALGO_RECT,
        text_list=sorting_algorithm_names,
        retval_list=sorting_algorithms,
        container=screen,
        horizontal=False,
    )

    dataset_info = [
        (k.removesuffix("_DATASET").title(), v) for k, v in Settings.__dict__.items() if k.endswith("_DATASET")
    ]
    dataset_size_names, dataset_size_values = map(list, zip(*dataset_info))
    size_menu = Menu(
        rect=Settings.MENU_DATASET_SIZE_RECT,
        text_list=dataset_size_names,
        retval_list=dataset_size_values,
        container=screen,
    )

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

        new_sorting_algo = algo_menu.update(*mouse_pos, clicked=clicked)
        new_dataset_size = size_menu.update(*mouse_pos, clicked=clicked)

        displayer.update(new_sorting_algo, new_dataset_size)
        displayer.render()

        if not displayer.sorting:
            size_menu.render()
            algo_menu.render()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

from typing import List, TypeVar
from rigor import Content
from rigor.screens import Screen

T = TypeVar("T")


class MenuScreen(Screen[T]):
    def __init__(self, title: str, options: List[str]):
        super().__init__()
        self.title: str = title
        self._options: List[str] = options
        self._counter = 0

    @property
    def selection(self) -> str:
        return self._options[self._counter]

    def pop(self):
        # Overwrite and reset selection so we start with the first menu entry the next time we enter
        self.reset_selection()
        super().pop()

    def reset_selection(self):
        self._counter = 0

    def render(self) -> Content:
        return Content(self.title, self.selection)

    def on_next(self):
        self._counter = (self._counter + 1) % len(self._options)
        self.refresh()

    def on_prev(self):
        self._counter = (self._counter - 1) % len(self._options)
        self.refresh()

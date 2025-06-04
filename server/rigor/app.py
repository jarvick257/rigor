from typing import Any

from .encoder import EncoderAction
from .display import Display
from .display_update import DisplayUpdate
from .input_handler import InputHandler
from .renderer import Renderer
from .module import Module


class App:
    def __init__(self, input_handler: InputHandler, renderer: Renderer):
        self.renderer: Renderer = renderer
        self.input_handler = input_handler
        self.input_handler.on_input(self._on_input)
        self.input_handler.on_client_state(self._on_client_state)
        self.module: Module | None = None

    def _on_input(self, action: EncoderAction) -> None:
        if self.module is not None:
            self.module.on_input(action)

    def _on_client_state(self, state: bool) -> None:
        if self.module is not None:
            self.module.on_client_state(state)

    def _on_module_update(
        self,
        sender: Display,
        op: DisplayUpdate,
        new_display: Display | None,
    ):
        assert sender is self.module
        assert op == DisplayUpdate.UPDATE
        assert new_display is None
        self._render()

    def _render(self):
        assert self.module is not None
        self.renderer.render(self.module.render())

    def run(self, state: Any, display: Display) -> None:
        self.run_module(Module(state, display))

    def run_module(self, module: Module) -> None:
        self.module = module
        self.module.attach(None, self._on_module_update)
        self._render()
        self.input_handler.run()

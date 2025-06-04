from typing import Callable, Any, Optional, TypeVar, Generic, List

from .content import Content
from .display_update import DisplayUpdate
from .encoder import EncoderAction

from .display import Display

T = TypeVar("T")


class Module(Generic[T], Display):
    """
    The Module class represents a module that can be added to the rigor device.
    It maintains a stack of displays and sends input from the rotary encoder to the server.
    """

    def __init__(self, module_state: T, display: Display):
        """
        Initializes the Module instance with the given state and display.

        :param module_state: The initial state of the module.
        :type module_state: T
        :param display: The display to use for this module.
        :type display: Display
        """
        self.state: T = module_state
        self.stack: List[Display] = []
        self._update_parent = None
        self._push(display)

    def _push(self, display: Display) -> None:
        """
        Pushes the given display onto the stack of displays for this module.

        :param display: The display to push onto the stack.
        :type display: Display
        """
        self.stack.append(display)
        if self._update_parent is not None:
            display.attach(self.state, self._on_child_update)
            self._refresh()

    def _pop(self) -> None:
        """
        Pops the topmost display from the stack of displays for this module.
        """
        if len(self.stack) > 1:
            self.stack[-1].detach()
            self.stack = self.stack[:-1]
            self._refresh()
        elif self._update_parent:
            self._update_parent(self, DisplayUpdate.POP, None)

    def _replace(self, display: Display) -> None:
        self.stack[-1].detach()
        self.stack[-1] = display
        if self._update_parent is not None:
            display.attach(self.state, self._on_child_update)
            self._refresh()

    def _peek(self) -> Display:
        """
        Returns the topmost display from the stack of displays for this module.

        :return: The topmost display.
        :rtype: Display
        """
        assert len(self.stack) > 0
        return self.stack[-1]

    def on_client_state(self, state: bool) -> None:
        for disp in self.stack:
            disp.on_client_state(state)

    def on_input(self, action: EncoderAction) -> None:
        """
        Handles input from the rotary encoder and sends it to the topmost display in the stack.

        :param action: The input action (either increase or decrease).
        :type action: EncoderAction
        """
        self._peek().on_input(action)

    def render(self) -> Content:
        """
        Returns the rendered content of the topmost display in the stack.

        :return: The rendered content.
        :rtype: Content
        """
        return self._peek().render()

    def attach(
        self,
        state: Any,
        callback: Callable[["Display", DisplayUpdate, Optional["Display"]], None],
    ) -> None:
        """
        Attaches the given display to this module and sets up event handling.

        :param state: The state of the display.
        :type state: Any
        :param callback: The callback function to call when an event occurs.
        :type callback: Callable[["Display", DisplayUpdate, Optional["Display"]], None]
        """
        _ = state
        self._update_parent = callback
        for child in self.stack:
            child.attach(self.state, self._on_child_update)

    def detach(self):
        """
        Detaches all displays from this module and stops event handling.
        """
        for child in self.stack:
            child.detach()
        self._update_parent = None

    def _refresh(self):
        """
        Refreshes the topmost display in the stack by sending it a new state update.
        """
        if self._update_parent is not None:
            self._update_parent(self, DisplayUpdate.UPDATE, None)

    def _on_child_update(
        self,
        sender: Display,
        op: DisplayUpdate,
        new_display: Display | None,
    ):
        """
        Handles update events from the topmost display in the stack.

        :param sender: The source of the update event.
        :type sender: Display
        :param op: The operation being performed (either push or pop).
        :type op: DisplayUpdate
        :param new_display: The new display to attach or detach, or None if there is no change.
        :type new_display: Display | None
        """
        current_display = self._peek()
        if op == DisplayUpdate.PUSH:
            assert current_display is sender
            assert new_display is not None
            self._push(new_display)
        elif op == DisplayUpdate.POP:
            if current_display is sender:
                self._pop()
        elif op == DisplayUpdate.UPDATE:
            if current_display is sender:
                self._refresh()
        elif op == DisplayUpdate.REPLACE:
            assert current_display is sender
            assert new_display is not None
            self._replace(new_display)

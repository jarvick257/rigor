from typing import TypeVar, Generic, Any, Optional, Callable

from rigor.encoder import EncoderAction
from rigor.content import Content
from rigor.display_update import DisplayUpdate
from rigor.display import Display

T = TypeVar("T")


class Screen(Generic[T], Display):
    """
    A generic screen class that displays content and handles encoder input.

    This class inherits from `Display` and provides a concrete implementation
    for displaying content and responding to encoder actions. It uses a generic
    type `T` to represent the screen's state.
    """

    def __init__(self):
        """
        Initializes a new `Screen` instance.
        """
        self._state: T | None
        self._update_parent: (
            Callable[["Display", DisplayUpdate, Optional["Display"]], None] | None
        )

    @property
    def state(self) -> T:
        """
        Returns the current state of the screen.

        Raises:
            AssertionError: If the screen is not attached to a stack.
        """
        assert (
            self._state is not None
        ), "Can't access state before being attached to stack"
        assert self._update_parent is not None
        return self._state

    def attach(
        self,
        state: Any,
        callback: Callable[["Display", DisplayUpdate, Optional["Display"]], None],
    ) -> None:
        """
        Attaches a state and callback to the screen.

        Args:
            state (Any): The state to attach to the screen.
            callback (Callable): The callback function to be called when the display updates.
        """
        self._state = state
        self._update_parent = callback
        self.on_attach()

    def refresh(self):
        """
        Refreshes the screen.
        """
        assert self._update_parent is not None
        self._update_parent(self, DisplayUpdate.UPDATE, None)

    def detach(self):
        """
        Detaches the screen from its parent.
        """
        self.on_detach()
        self._update_parent = None
        self._state = None

    def on_attach(self):
        """
        Called when the screen is attached.
        """
        pass

    def on_detach(self):
        """
        Called when the screen is detached.
        """
        pass

    def on_client_state(self, state: bool) -> None:
        if state:
            self.on_client_connected()
        else:
            self.on_client_disconnected()

    def on_input(self, action: EncoderAction) -> None:
        """
        Handles encoder input actions.

        Args:
            action (EncoderAction): The encoder action to handle.
        """
        if action == EncoderAction.NONE:
            self.on_nop()
        elif action == EncoderAction.ENTER:
            self.on_enter()
        elif action == EncoderAction.NEXT:
            self.on_next()
        elif action == EncoderAction.PREV:
            self.on_prev()

    def on_nop(self) -> None:
        """
        Handles the "No Operation" encoder action.
        """
        pass

    def on_client_connected(self) -> None:
        """
        Handles client connected event
        """
        pass

    def on_client_disconnected(self) -> None:
        """
        Handles client disconnected event
        """
        pass

    def on_enter(self) -> None:
        """
        Handles the "Enter" encoder action.
        """
        pass

    def on_next(self) -> None:
        """
        Handles the "Next" encoder action.
        """
        pass

    def on_prev(self) -> None:
        """
        Handles the "Previous" encoder action.
        """
        pass

    def render(self) -> Content:
        """
        Renders the screen content.

        Returns:
            Content: The content to be displayed.
        """
        raise NotImplementedError()

    def push(self, display: Display):
        """
        Pushes a display onto the stack.

        Args:
            display (Display): The display to push.
        """
        assert self._update_parent is not None
        self._update_parent(self, DisplayUpdate.PUSH, display)

    def pop(self):
        """
        Pops a display from the stack.
        """
        assert self._update_parent is not None
        self._update_parent(self, DisplayUpdate.POP, None)

    def replace(self, display: Display):
        """
        Pops a display from the stack.
        """
        assert self._update_parent is not None
        self._update_parent(self, DisplayUpdate.REPLACE, display)

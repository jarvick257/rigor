from typing import Callable, Any, Optional

from .content import Content
from .encoder import EncoderAction
from .display_update import DisplayUpdate


class Display:
    """
    Abstract base class for display components.

    This class defines the core interface for displaying content
    and responding to encoder actions. Subclasses should implement
    the `on_input` and `render` methods to provide specific display behavior.
    """

    def on_client_state(self, state: bool) -> None:
        _ = state
        raise NotImplementedError()

    def on_input(self, action: EncoderAction) -> None:
        """
        Handles encoder input actions.

        Args:
            action (EncoderAction): The encoder action to handle.
        """
        _ = action
        raise NotImplementedError()

    def render(self) -> Content:
        """
        Renders the display content.

        Returns:
            Content: The content to be displayed.
        """
        raise NotImplementedError()

    def attach(
        self,
        state: Any,
        callback: Callable[["Display", DisplayUpdate, Optional["Display"]], None],
    ) -> None:
        """
        Attaches a state and callback to the display.

        Args:
            state (Any): The state to attach.
            callback (Callable): The callback to be invoked when the display updates.
        """
        _ = callback, state
        raise NotImplementedError()

    def detach(self):
        """
        Detaches the display.
        """
        raise NotImplementedError()

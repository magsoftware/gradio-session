from abc import ABC, abstractmethod
from typing import Any

import gradio as gr


class BasePage(ABC):
    """Abstract base class for all pages."""

    def __init__(self, label: str, title: str) -> None:
        self.label = label
        self.title = title

    @abstractmethod
    def create_ui(self) -> None:
        """Creates UI for the page."""
        pass

    def render(self, visible: bool = False) -> None:
        with gr.Column(visible=visible) as self.container:
            self.create_ui()

    def show(self) -> dict[str, Any]:
        return gr.update(visible=True)

    def hide(self) -> dict[str, Any]:
        return gr.update(visible=False)

from abc import ABC, abstractmethod

import gradio as gr


class BaseTab(ABC):
    """Abstract base class for all tabs."""

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def create_ui(self, tab_component: gr.Tab) -> None:
        pass

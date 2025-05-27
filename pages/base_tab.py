from abc import ABC, abstractmethod

import gradio as gr


class BaseTab(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def create_ui(self, tab_component: gr.Tab) -> None:
        pass

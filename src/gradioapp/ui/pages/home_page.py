import gradio as gr
from loguru import logger

from ...domain.session.helpers import get_session_id
from ...domain.session.store import get_session_store
from .base import BasePage, BaseTab


class Tab1(BaseTab):
    def __init__(self) -> None:
        super().__init__("Tab1")

    def create_ui(self, tab_component: gr.Tab) -> None:
        show_btn = gr.Button("Show my session")
        show_btn.click(fn=self.show_session, inputs=[], outputs=gr.Textbox())

    def show_session(self, request: gr.Request) -> str:
        session_id = get_session_id(request)
        logger.debug(f"Showing session for session_id: {session_id}")
        return f"{get_session_store().dump_session(session_id)}"


class Tab2(BaseTab):
    def __init__(self) -> None:
        super().__init__("Tab2")

    def create_ui(self, tab_component: gr.Tab) -> None:
        show_btn = gr.Button("Dump session store")
        show_btn.click(fn=self.dump_sessions, outputs=gr.Textbox())

    def dump_sessions(self) -> str:
        return get_session_store().dump_store()


class HomePage(BasePage):
    def __init__(self) -> None:
        super().__init__(label="Home", title="Home Page")
        self.tabs = [
            Tab1(),
            Tab2(),
        ]
        logger.info(
            f"HomePage initialized with tabs: {[tab.name for tab in self.tabs]}"
        )

    def create_ui(self) -> None:
        with gr.Tabs():
            for tab in self.tabs:
                with gr.Tab(tab.name) as tab_component:
                    tab.create_ui(tab_component)

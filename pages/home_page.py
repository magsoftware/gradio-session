import gradio as gr

from session import get_session_store

from .base_page import BasePage
from .base_tab import BaseTab


class Tab1(BaseTab):
    def __init__(self) -> None:
        super().__init__("Tab1")

    def create_ui(self, tab_component: gr.Tab, session_id: gr.State) -> None:
        show_btn = gr.Button("Show my session")
        show_btn.click(fn=self.show_session, inputs=[session_id], outputs=gr.Textbox())

    def show_session(self, session_id: gr.State) -> str:
        return f"{get_session_store().dump_session(session_id)}"


class Tab2(BaseTab):
    def __init__(self) -> None:
        super().__init__("Tab2")

    def create_ui(self, tab_component: gr.Tab, session_id: gr.State) -> None:
        show_btn = gr.Button("Dump session store")
        show_btn.click(fn=self.dump_sessions, outputs=gr.Textbox())

    def dump_sessions(self) -> str:
        store = get_session_store()
        return store.dump_store()


class Tab3(BaseTab):
    def __init__(self) -> None:
        super().__init__("Tab3")

    def create_ui(self, tab_component: gr.Tab, session_id: gr.State) -> None:
        show_btn = gr.Button("Show session")
        show_btn.click(fn=self.show_session, inputs=[session_id], outputs=gr.Textbox())

    def show_session(self, session_id: gr.State) -> str:
        return f"{get_session_store().dump_session(session_id)}"


class HomePage(BasePage):
    def __init__(self, session_id: gr.State) -> None:
        super().__init__(label="Home", title="Home Page")
        self.session_id = session_id
        self.tabs = [
            Tab1(),
            Tab2(),
            Tab3(),
        ]

    def create_ui(self) -> None:
        with gr.Tabs():
            for tab in self.tabs:
                with gr.Tab(tab.name) as tab_component:
                    tab.create_ui(tab_component, self.session_id)

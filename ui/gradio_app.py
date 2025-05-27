import gradio as gr
from loguru import logger

from pages import HomePage
from ui.javascript import redirect_js
from ui.navbar import create_navbar


def create_gradio_app() -> gr.Blocks:
    logger.info("Creating Gradio app UI")

    with gr.Blocks(
        title="Gradio App", visible=True, fill_width=True, js=redirect_js
    ) as gradio_app:
        create_navbar()

        home_page = HomePage()
        home_page.render(visible=True)

    return gradio_app

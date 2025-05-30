import gradio as gr
from loguru import logger

from pages import HomePage
from ui.javascript import redirect_js
from ui.navbar import create_navbar


def create_gradio_app() -> gr.Blocks:
    """
    Creates and configures the Gradio application UI.

    This function initializes a Gradio Blocks interface, sets up the application title,
    visibility, and JavaScript redirection. It also adds a navigation bar and renders
    the home page component.

    Returns:
        gr.Blocks: The configured Gradio Blocks application instance.
    """
    logger.info("Creating Gradio app UI")

    with gr.Blocks(
        title="Gradio App", visible=True, fill_width=True, js=redirect_js
    ) as gradio_app:
        create_navbar()

        home_page = HomePage()
        home_page.render(visible=True)

    return gradio_app

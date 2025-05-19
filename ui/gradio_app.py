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
        session_id = gr.State()

        def load_session(request: gr.Request):
            session_id = getattr(request.state, "session_id", None)
            if not session_id:
                logger.error("Session ID not found in request state.")
            logger.info(f"Session ID {session_id}")
            return session_id

        # This sets the state on load ie. puts session_id to Gradio State
        gradio_app.load(fn=load_session, inputs=[], outputs=[session_id])

        create_navbar()

        home_page = HomePage(session_id)
        home_page.render(visible=True)

    return gradio_app

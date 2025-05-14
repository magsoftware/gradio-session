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
            from services import verify_token

            token = request.cookies.get("access_token")
            if not token:
                return None
            payload = verify_token(token)
            return payload.get("session_id")

        # This sets the state on load
        gradio_app.load(fn=load_session, inputs=[], outputs=[session_id])

        create_navbar()

        home_page = HomePage(session_id)
        home_page.render(visible=True)

    return gradio_app

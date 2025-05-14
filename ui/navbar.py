import gradio as gr


def create_navbar() -> None:
    with gr.Row(equal_height=True):
        gr.Button("Logout").click(
            fn=None,
            inputs=[],
            outputs=[],
            js="() => { window.location.href = '/logout'; }",
        )

import gradio as gr


def create_navbar() -> None:
    """
    Creates a navigation bar with a logout button in a Gradio interface.

    The logout button, when clicked, redirects the user to the '/logout' endpoint.
    This function is intended to be used within a Gradio UI layout.

    Returns:
        None
    """
    with gr.Row(equal_height=True):
        gr.Button("Logout").click(
            fn=None,
            inputs=[],
            outputs=[],
            js="() => { window.location.href = '/logout'; }",
        )

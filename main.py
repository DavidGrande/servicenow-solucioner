import gradio as gr
from chat_handler import chat

gr.ChatInterface(fn=chat).launch(server_port=7870)
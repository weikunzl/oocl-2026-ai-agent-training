
from IPython.display import Image, display
def draw_graph(short_app):
    return display(Image(short_app.get_graph().draw_mermaid_png()))

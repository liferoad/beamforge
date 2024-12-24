# third party libraries
import mesop as me


@me.page(path="/")
def app():
    with me.box(style=me.Style(display="grid", grid_template_columns="1fr 2fr 1fr", height="100%")):
        # Left Sidebar
        with me.box(style=me.Style(background="#f0f0f0", padding=me.Padding.all(24), overflow_y="auto")):
            me.text("Left Sidebar")

        # Main content
        with me.box(style=me.Style(padding=me.Padding.all(24), overflow_y="auto")):
            me.text("Main Content")

        # Right Sidebar
        with me.box(style=me.Style(background="#f0f0f0", padding=me.Padding.all(24), overflow_y="auto")):
            me.text("Right Sidebar")

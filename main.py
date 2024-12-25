# third party libraries
import mesop as me
import yaml


@me.stateclass
class State:
    file: me.UploadedFile
    yaml_content: dict = None


def handle_upload(event: me.UploadEvent):
    state = me.state(State)
    state.file = event.file
    # Parse YAML content
    yaml_content = yaml.safe_load(event.file.getvalue().decode())
    state.yaml_content = yaml_content


@me.page(path="/")
def app():
    s = me.state(State)

    with me.box(style=me.Style(display="grid", grid_template_columns="1fr 2fr 1fr", height="100%")):
        # Left Sidebar
        with me.box(style=me.Style(background="#f0f0f0", padding=me.Padding.all(24), overflow_y="auto")):
            me.text("Upload YAML")
            with me.content_uploader(
                accepted_file_types=["text/yaml"],
                on_upload=handle_upload,
                type="icon",
                style=me.Style(font_weight="bold"),
            ):
                me.icon("upload")
            me.divider()
            if s.yaml_content:
                # Display the parsed YAML content
                me.textarea(
                    value=yaml.dump(s.yaml_content, default_flow_style=False, sort_keys=False),
                    appearance="outline",
                    style=me.Style(width="100%"),
                    autosize=True,
                )
        # Main content
        with me.box(style=me.Style(padding=me.Padding.all(24), overflow_y="auto")):
            me.text("Pipeline Graph")

        # Right Sidebar
        with me.box(style=me.Style(background="#f0f0f0", padding=me.Padding.all(24), overflow_y="auto")):
            me.text("Right Sidebar")

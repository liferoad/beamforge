# third party libraries
import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from beamforge.callbacks.graph_callbacks import register_graph_callbacks
from beamforge.callbacks.node_callbacks import register_node_callbacks
from beamforge.callbacks.yaml_callbacks import register_yaml_callbacks
from beamforge.layouts.main_layout import create_layout

# Register the dagre layout
cyto.load_extra_layouts()
external_stylesheets = [dbc.themes.BOOTSTRAP]

# Initialize the Dash app
app = dash.Dash(
    __name__,
    title="BeamForge - Visual Builder with Beam YAML",
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets,
)

# Set the layout
app.layout = create_layout()

# Register callbacks
register_graph_callbacks(app)
register_node_callbacks(app)
register_yaml_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)

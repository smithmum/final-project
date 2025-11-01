# Import required libraries
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

import dash
from dash import dcc, html

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a dash application
app = dash.Dash(__name__)


# Create an app layout
# the launch sites are in the variable "Launch Site" in the spacex_df dataframe
# Build dropdown options from the dataframe (include an ALL option)
site_options = [{"label": "All Sites", "value": "ALL"}]
site_options += [
    {"label": site, "value": site}
    for site in sorted(spacex_df["Launch Site"].unique())
]

app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),
        # TASK 1: Dropdown to enable Launch Site selection (default: ALL)
        dcc.Dropdown(
            id="site-dropdown",
            options=site_options,
            value="ALL",
            placeholder="Select a Launch Site",
            searchable=True,
            clearable=False,
            style={"width": "80%", "margin": "0 auto"},
        ),
        html.Br(),
        # TASK 2: Pie chart area — will display total successful launches across sites
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),
        html.P("Payload range (Kg):", style={"textAlign": "center"}),
        # TASK 3: Payload RangeSlider
        dcc.RangeSlider(
            id="payload-slider",
            min=int(min_payload),
            max=int(max_payload),
            step=100,
            value=[int(min_payload), int(max_payload)],
            marks={
                int(min_payload): str(int(min_payload)),
                int(max_payload): str(int(max_payload)),
            },
            tooltip={"placement": "bottom", "always_visible": False},
            allowCross=False,
            updatemode="mouseup",
        ),
        html.Br(),
        # TASK 4: Scatter chart area — will show correlation between payload and launch success
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output("success-pie-chart", "figure"), Input("site-dropdown", "value")
)
def update_pie_chart(selected_site):
    """Return a pie chart. If ALL selected, show total successful launches by site.
    If a specific site is selected, show success vs failure counts for that site.
    """
    if selected_site == "ALL":
        # count successful launches (class == 1) per site
        success_df = spacex_df[spacex_df["class"] == 1]
        fig = px.pie(
            success_df,
            names="Launch Site",
            title="Total Successful Launches by Site",
        )
    else:
        # filter by site and show success vs failure
        filtered_df = spacex_df[spacex_df["Launch Site"] == selected_site]
        outcome_counts = filtered_df["class"].value_counts().reset_index()
        outcome_counts.columns = ["outcome", "count"]
        # map 1/0 to readable labels
        outcome_map = {1: "Success", 0: "Failure"}
        outcome_counts["outcome"] = outcome_counts["outcome"].map(outcome_map)
        fig = px.pie(
            outcome_counts,
            names="outcome",
            values="count",
            title=f"Launch Outcomes for {selected_site}",
        )

    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [Input("site-dropdown", "value"), Input("payload-slider", "value")],
)
def update_scatter_chart(selected_site, payload_range):
    """Return scatter chart filtered by payload range and (optionally) launch site.
    X axis: Payload Mass (kg); Y axis: class (0/1); color: Booster Version Category.
    """
    low, high = payload_range
    mask = spacex_df["Payload Mass (kg)"].between(low, high)
    filtered_df = spacex_df[mask]

    if selected_site != "ALL":
        filtered_df = filtered_df[filtered_df["Launch Site"] == selected_site]

    # Use Booster Version Category as color if available
    color_col = (
        "Booster Version Category"
        if "Booster Version Category" in spacex_df.columns
        else None
    )
    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color=color_col,
        title="Payload vs. Launch Outcome",
        hover_data=["Flight Number", "Launch Site"],
    )

    return fig


# Run the app
if __name__ == "__main__":
    app.run()

from datetime import date

import pandas as pd
import plotly.express as px
from dash import Input, Output, dash_table, dcc, html
from django_plotly_dash import DjangoDash

from .dash_data import DashData

df = DashData.get_combined_data_by_date()
df["created_at__date"] = pd.to_datetime(df["created_at__date"])

app = DjangoDash("GenericDash")
app.layout = html.Div(
    [
        html.Div(children="Daily reports"),
        html.Hr(),
        dcc.DatePickerRange(
            id="date-picker-range",
            min_date_allowed=df["created_at__date"].min(),
            max_date_allowed=date.today(),
            start_date=df["created_at__date"].min(),
            end_date=df["created_at__date"].max(),
            display_format="YYYY-MM-DD",
            clearable=True,
        ),
        dcc.RadioItems(
            options=[{"label": col, "value": col} for col in df.columns[1:]],
            value="order_count",
            id="controls-and-radio-item",
        ),
        dcc.Graph(
            id="controls-and-graph", style={"width": "100%", "display": "inline-block"}
        ),
        dash_table.DataTable(id="data-table", data=df.to_dict("records"), page_size=5),
    ]
)


@app.callback(
    Output(component_id="controls-and-graph", component_property="figure"),
    Output(component_id="data-table", component_property="data"),
    Input(component_id="controls-and-radio-item", component_property="value"),
    Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
)
def update_output(col_chosen, start_date, end_date):
    filtered_df = df[
        (df["created_at__date"] >= start_date) & (df["created_at__date"] <= end_date)
    ]
    fig = px.bar(filtered_df, x="created_at__date", y=col_chosen)

    table = filtered_df.to_dict("records")
    return fig, table

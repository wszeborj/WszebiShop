from datetime import date

import pandas as pd
import plotly.express as px
from dash import Input, Output, dash_table, dcc, html
from django_plotly_dash import DjangoDash

from shop.models import Category

from .dash_data import DashData

app = DjangoDash("GenericDash")

category_options = [{"label": "All", "value": ""}] + [
    {"label": cat.name, "value": cat.id} for cat in Category.objects.all()
]

app.layout = html.Div(
    [
        html.Div(children="Daily reports"),
        html.Hr(),
        dcc.DatePickerRange(
            id="date-picker-range",
            min_date_allowed=date(2024, 1, 1),
            max_date_allowed=date.today(),
            start_date=date(2024, 1, 1),
            end_date=date.today(),
            display_format="YYYY-MM-DD",
            clearable=True,
        ),
        dcc.RadioItems(
            id="controls-and-radio-item",
            options=[
                {"label": "Order Count", "value": "order_count"},
                {"label": "Total Payment", "value": "total_payment"},
                {"label": "Total Quantity", "value": "total_quantity"},
                {"label": "Average Order Value", "value": "avg_order_value"},
                {"label": "Avg Quantity Per Order", "value": "avg_quantity_per_order"},
            ],
            value="order_count",
        ),
        dcc.Graph(
            id="controls-and-graph", style={"width": "100%", "display": "inline-block"}
        ),
        dash_table.DataTable(id="data-table", page_size=5),
    ]
)


@app.callback(
    Output(component_id="controls-and-graph", component_property="figure"),
    Output(component_id="data-table", component_property="data"),
    Input(component_id="controls-and-radio-item", component_property="value"),
    Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
)
def update_output(col_chosen, start_date, end_date, **kwargs):
    user = kwargs["user"]
    df = DashData.get_combined_data_by_date(user=user)
    df["created_at__date"] = pd.to_datetime(df["created_at__date"])

    filtered_df = df[
        (df["created_at__date"] >= start_date) & (df["created_at__date"] <= end_date)
    ]

    fig = px.bar(filtered_df, x="created_at__date", y=col_chosen)

    table = filtered_df.to_dict("records")
    return fig, table

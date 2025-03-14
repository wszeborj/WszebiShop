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


def create_date_picker():
    return html.Div(
        id="date-picker-container",
        children=[
            dcc.DatePickerRange(
                id="date-picker-range",
                min_date_allowed=date(2024, 1, 1),
                max_date_allowed=date.today(),
                start_date=date(2024, 1, 1),
                end_date=date.today(),
                display_format="YYYY-MM-DD",
                clearable=True,
            ),
        ],
        style={"margin-bottom": "20px"},
    )


def create_category_dropdown():
    return html.Div(
        id="category-dropdown-container",
        children=[
            dcc.Dropdown(
                id="category-dropdown",
                options=category_options,
                value="",
                placeholder="Select category",
                clearable=True,
            ),
        ],
        style={"display": "none", "margin-bottom": "20px"},
    )


def create_order_report_layout():
    return html.Div(
        id="order-report-content",
        children=[
            dcc.RadioItems(
                id="order-radio-item",
                options=[
                    {"label": "Order Count", "value": "order_count"},
                    {"label": "Total Payment", "value": "total_payment"},
                    {"label": "Average Order Value", "value": "avg_order_value"},
                ],
                value="order_count",
            ),
            dcc.Graph(
                id="order-graph", style={"width": "100%", "display": "inline-block"}
            ),
            dash_table.DataTable(id="order-table", page_size=5),
        ],
        style={"display": "block"},
    )


def create_order_item_report_layout():
    return html.Div(
        id="order-item-report-content",
        children=[
            dcc.RadioItems(
                id="order-item-radio-item",
                options=[
                    {
                        "label": "Total Quantity",
                        "value": "total_quantity_order_items_in_day",
                    },
                    {
                        "label": "Total Order Item Payment",
                        "value": "total_order_item_payment",
                    },
                    {"label": "Avg Order Item Value", "value": "avg_order_item_value"},
                ],
                value="total_quantity_order_items_in_day",
            ),
            dcc.Graph(
                id="order-item-graph",
                style={"width": "100%", "display": "inline-block"},
            ),
            dash_table.DataTable(id="order-item-table", page_size=5),
        ],
        style={"display": "none"},
    )


app.layout = html.Div(
    [
        html.Div(children="Daily reports"),
        html.Hr(),
        dcc.Tabs(
            id="report-tabs",
            value="order-report",
            children=[
                dcc.Tab(label="Order Report", value="order-report"),
                dcc.Tab(label="Order Item Report", value="order-item-report"),
            ],
        ),
        create_date_picker(),
        create_category_dropdown(),
        create_order_report_layout(),
        create_order_item_report_layout(),
    ]
)


@app.callback(
    [
        Output("order-report-content", "style"),
        Output("order-item-report-content", "style"),
        Output("category-dropdown-container", "style"),
    ],
    [Input("report-tabs", "value")],
)
def toggle_report_tabs(selected_tab):
    if selected_tab == "order-report":
        return {"display": "block"}, {"display": "none"}, {"display": "none"}
    elif selected_tab == "order-item-report":
        return {"display": "none"}, {"display": "block"}, {"display": "block"}
    return {"display": "none"}, {"display": "none"}, {"display": "none"}


@app.callback(
    [Output("order-graph", "figure"), Output("order-table", "data")],
    [
        Input("order-radio-item", "value"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    ],
)
def update_order_report(col_chosen, start_date, end_date, **kwargs):
    user = kwargs["user"]
    df = DashData.get_combined_order_data(user=user)
    df["created_at__date"] = pd.to_datetime(df["created_at__date"])

    filtered_df = df[
        (df["created_at__date"] >= start_date) & (df["created_at__date"] <= end_date)
    ]

    fig = px.bar(filtered_df, x="created_at__date", y=col_chosen)

    table = filtered_df.to_dict("records")
    return fig, table


@app.callback(
    [Output("order-item-graph", "figure"), Output("order-item-table", "data")],
    [
        Input("order-item-radio-item", "value"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("category-dropdown", "value"),
    ],
)
def update_order_item_report(col_chosen, start_date, end_date, category, **kwargs):
    user = kwargs["user"]
    df = DashData.get_combined_order_item_data(user=user, category=category)
    df["created_at__date"] = pd.to_datetime(df["created_at__date"])

    filtered_df = df[
        (df["created_at__date"] >= start_date) & (df["created_at__date"] <= end_date)
    ]

    fig = px.bar(filtered_df, x="created_at__date", y=col_chosen)

    table = filtered_df.to_dict("records")
    return fig, table

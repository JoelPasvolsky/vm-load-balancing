# Copyright 2024 D-Wave
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This file stores the Dash HTML layout for the app."""
from __future__ import annotations

from dash import dcc, html

from demo_configs import (
    DESCRIPTION,
    HOSTS,
    MAIN_HEADER,
    SOLVER_TIME,
    THEME_COLOR_SECONDARY,
    THUMBNAIL,
    VMS,
)
from src.demo_enums import PriorityType


def slider(label: str, id: str, config: dict) -> html.Div:
    """Slider element for value selection.

    Args:
        label: The title that goes above the slider.
        id: A unique selector for this element.
        config: A dictionary of slider configerations, see dcc.Slider Dash docs.
    """
    return html.Div(
        className="slider-wrapper",
        children=[
            html.Label(label),
            dcc.Slider(
                id=id,
                className="slider",
                **config,
                marks={
                    config["min"]: str(config["min"]),
                    config["max"]: str(config["max"]),
                },
                tooltip={
                    "placement": "bottom",
                    "always_visible": True,
                },
            ),
        ],
    )


def radio(label: str, id: str, options: list, value: int, inline: bool = True) -> html.Div:
    """Radio element for option selection.

    Args:
        label: The title that goes above the radio.
        id: A unique selector for this element.
        options: A list of dictionaries of labels and values.
        value: The value of the radio that should be preselected.
        inline: Whether the options are displayed beside or below each other.
    """
    return html.Div(
        className="radio-wrapper",
        children=[
            html.Label(label),
            dcc.RadioItems(
                id=id,
                className=f"radio{' radio--inline' if inline else ''}",
                inline=inline,
                options=options,
                value=value,
            ),
        ],
    )


def generate_settings_form() -> html.Div:
    """This function generates settings for selecting the scenario.

    Returns:
        html.Div: A Div containing the settings for selecting the scenario.
    """
    priority_options = [
        {"label": priority.label, "value": priority.value} for priority in PriorityType
    ]

    return html.Div(
        className="settings",
        children=[
            slider(
                "Number of Virtual Machines",
                "vms",
                VMS,
            ),
            slider(
                "Number of Hosts",
                "hosts",
                HOSTS,
            ),
            radio(
                "Balance Priority",
                "priority",
                sorted(priority_options, key=lambda op: op["value"]),
                0,
            ),
            html.Label("Solver Time Limit (seconds)"),
            dcc.Input(
                id="solver-time-limit",
                type="number",
                **SOLVER_TIME,
            ),
        ],
    )


def generate_run_buttons() -> html.Div:
    """Run and cancel buttons to run the optimization."""
    return html.Div(
        id="button-group",
        children=[
            html.Button(id="run-button", children="Run Optimization", n_clicks=0, disabled=False),
            html.Button(
                id="cancel-button",
                children="Cancel Optimization",
                n_clicks=0,
                className="display-none",
            ),
        ],
    )


def generate_graph(index: int) -> html.Div:
    """Generates a graph with a zoom button.

    Args:
        index: A unit integer to identify the graph by.

    Returns:
        html.Div: A div containing a graph and magnifying button.
    """
    return html.Div(
        children=[
            html.Div(
                [
                    html.Div([html.Span("+"), html.Span("-")], className="magnifying-lens"),
                    html.Div(className="magnifying-handle"),
                ],
                className="magnifying",
                id={"type": "magnifying", "index": index},
            ),
            dcc.Graph(
                id={"type": "graph", "index": index},
                responsive=True,
                config={"displayModeBar": False},
                className="graph-element",
            ),
        ],
    )


def create_interface():
    """Set the application HTML."""
    return html.Div(
        id="app-container",
        children=[
            # Below are any temporary storage items, e.g., for sharing data between callbacks.
            dcc.Store(id="vms-store"),
            dcc.Store(id="hosts-store"),
            dcc.Store(id="cluster-balance-store"),
            # Header brand banner
            html.Div(className="banner", children=[html.Img(src=THUMBNAIL)]),
            # Settings and results columns
            html.Div(
                className="columns-main",
                children=[
                    # Left column
                    html.Div(
                        id={"type": "to-collapse-class", "index": 0},
                        className="left-column",
                        children=[
                            html.Div(
                                className="left-column-layer-1",  # Fixed width Div to collapse
                                children=[
                                    html.Div(
                                        className="left-column-layer-2",  # Padding and content wrapper
                                        children=[
                                            html.H1(MAIN_HEADER),
                                            html.P(DESCRIPTION),
                                            generate_settings_form(),
                                            generate_run_buttons(),
                                        ],
                                    )
                                ],
                            ),
                            # Left column collapse button
                            html.Div(
                                html.Button(
                                    id={"type": "collapse-trigger", "index": 0},
                                    className="left-column-collapse",
                                    children=[html.Div(className="collapse-arrow")],
                                ),
                            ),
                        ],
                    ),
                    # Right column
                    html.Div(
                        className="right-column",
                        children=[
                            dcc.Tabs(
                                id="tabs",
                                value="input-tab",
                                mobile_breakpoint=0,
                                children=[
                                    dcc.Tab(
                                        label="Current State",
                                        id="input-tab",
                                        value="input-tab",  # used for switching tabs programatically
                                        className="tab",
                                        children=[
                                            html.H5(id="cluster-balance-factor"),
                                            dcc.Loading(
                                                parent_className="input",
                                                type="circle",
                                                color=THEME_COLOR_SECONDARY,
                                                children=[
                                                    html.Div(
                                                        [
                                                            generate_graph(0),
                                                            generate_graph(1),
                                                        ],
                                                        className="graph-wrapper",
                                                    ),
                                                    html.Div(
                                                        [
                                                            generate_graph(2),
                                                            generate_graph(3),
                                                        ],
                                                        className="graph-wrapper",
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    dcc.Tab(
                                        label="Results",
                                        id="results-tab",
                                        className="tab",
                                        disabled=True,
                                        children=[
                                            html.H5(id="cluster-balance-factor-results"),
                                            dcc.Loading(
                                                parent_className="results",
                                                type="circle",
                                                color=THEME_COLOR_SECONDARY,
                                                children=[
                                                    html.Div(
                                                        [
                                                            generate_graph(4),
                                                            generate_graph(5),
                                                        ],
                                                        className="graph-wrapper",
                                                    ),
                                                    html.Div(
                                                        [
                                                            generate_graph(6),
                                                            generate_graph(7),
                                                        ],
                                                        className="graph-wrapper",
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            )
                        ],
                    ),
                ],
            ),
        ],
    )

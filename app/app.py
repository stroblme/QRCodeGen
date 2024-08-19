import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, callback, State
import dash
from dash import (
    html,
    Input,
    State,
    Output,
    callback,
    clientside_callback,
    DiskcacheManager,
)
import dash_bootstrap_components as dbc
import qrcode

# libraries for rounded corners
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import (
    RoundedModuleDrawer,
    SquareModuleDrawer,
)
from qrcode.image.styles.colormasks import RadialGradiantColorMask, SolidFillColorMask

import diskcache

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)


app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    background_callback_manager=background_callback_manager,
)


sidebar = html.Div(
    [
        html.Div(
            [
                html.H1(
                    f"QR Code Generator",
                ),
            ],
            className="infoBox",
        ),
        html.Hr(),
        html.Div(
            [
                html.Span(
                    [
                        dbc.Label(className="fa fa-moon", html_for="switch"),
                        dbc.Switch(
                            id="switch",
                            value=True,
                            className="d-inline-block ms-1",
                            persistence=True,
                        ),
                        dbc.Label(className="fa fa-sun", html_for="switch"),
                    ],
                    style={"float": "left"},
                ),
            ]
        ),
    ],
    className="sidebar",
    id="page-sidebar",
)

content = html.Div(
    [
        dcc.Store(id="qrcode-storage-main", storage_type="session"),
        html.Div(
            [
                html.Div(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            type="text",
                                            placeholder="QR Code Text",
                                            id="text-input",
                                        ),
                                        dbc.Tooltip(
                                            "Text that will be encoded in the QR Code.",
                                            target="text-input",
                                        ),
                                        html.Br(),
                                        dbc.Spinner(
                                            html.Div("", id="loading-state"),
                                            type="grow",
                                            size="sm",
                                            id="loading-output",
                                        ),
                                    ],
                                ),
                                dbc.Col(
                                    [
                                        dbc.Checklist(
                                            options=[
                                                {
                                                    "label": "Error Corrected",
                                                    "value": 1,
                                                },
                                                {"label": "Rounded", "value": 2},
                                                {
                                                    "label": "Color Gradient",
                                                    "value": 3,
                                                },
                                            ],
                                            value=[1, 2],
                                            id="options-checklist",
                                        ),
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            type="color",
                                            value="#000000",
                                            id="base-color-input",
                                            style={"width": 75, "height": 40},
                                        ),
                                        dbc.Tooltip(
                                            "Color that will be used in the QR Code. Hint: black ist blazing fast!",
                                            target="base-color-input",
                                        ),
                                        dbc.Input(
                                            type="color",
                                            value="#404040",
                                            id="gradient-color-input",
                                            style={"width": 75, "height": 40},
                                            disabled=True,
                                        ),
                                        dbc.Tooltip(
                                            "Color that will be used to draw a radial gradient.",
                                            target="gradient-color-input",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                    style={"display": "inline-block"},
                ),
            ],
            style={"padding": "15px", "padding-bottom": "40px", "padding-top": "40px"},
        ),
        html.Div(
            [],
            id="qrcode-output",
        ),
    ],
    className="content",
)


app.layout = html.Div([sidebar, content])

clientside_callback(
    """
    (switchOn) => {
       switchOn
         ? document.documentElement.setAttribute('data-bs-theme', 'light')
         : document.documentElement.setAttribute('data-bs-theme', 'dark')
       return window.dash_clientside.no_update
    }
    """,
    Output("switch", "id"),
    Input("switch", "value"),
)


@callback(
    [
        Output("qrcode-storage-main", "data", allow_duplicate=True),
        Output("gradient-color-input", "disabled"),
    ],
    [
        Input("options-checklist", "value"),
    ],
    [
        State("qrcode-storage-main", "data"),
    ],
    prevent_initial_call=True,
)
def on_options_changed(
    options_checklist_value,
    storage_main_data,
):
    storage_main_data = storage_main_data or {}

    storage_main_data["error-corrected"] = (
        True if 1 in options_checklist_value else False
    )
    storage_main_data["rounded"] = True if 2 in options_checklist_value else False
    storage_main_data["gradient-color-enabled"] = (
        True if 3 in options_checklist_value else False
    )

    return [storage_main_data, not storage_main_data["gradient-color-enabled"]]


@callback(
    [
        Output("qrcode-storage-main", "data", allow_duplicate=True),
    ],
    [
        Input("gradient-color-input", "value"),
    ],
    [
        State("qrcode-storage-main", "data"),
    ],
    prevent_initial_call=True,
)
def on_gradient_color_changed(
    gradient_color_input_value,
    storage_main_data,
):
    storage_main_data = storage_main_data or {}
    gradient_color_input_value = gradient_color_input_value.replace("#", "")
    if storage_main_data["gradient-color-enabled"]:
        storage_main_data["gradient-color"] = tuple(
            int(gradient_color_input_value[i : i + 2], 16) for i in (0, 2, 4)
        )

    return [storage_main_data]


@callback(
    [
        Output("qrcode-storage-main", "data", allow_duplicate=True),
    ],
    [
        Input("base-color-input", "value"),
    ],
    [
        State("qrcode-storage-main", "data"),
    ],
    prevent_initial_call=True,
)
def on_base_color_changed(
    base_color_input_value,
    storage_main_data,
):
    base_color_input_value = base_color_input_value.replace("#", "")
    storage_main_data = storage_main_data or {}

    storage_main_data["base-color"] = tuple(
        int(base_color_input_value[i : i + 2], 16) for i in (0, 2, 4)
    )

    return [storage_main_data]


@callback(
    Output("qrcode-storage-main", "data", allow_duplicate=True),
    [
        Input("text-input", "value"),
    ],
    [
        State("qrcode-storage-main", "data"),
    ],
    prevent_initial_call=True,
)
def on_submit_input_button_n_clicks(
    text_input_value,
    storage_main_data,
):
    if text_input_value is None:
        return dash.no_update

    storage_main_data = storage_main_data or {}

    storage_main_data["text-input"] = text_input_value

    return storage_main_data


@callback(
    [
        Output("loading-output", "children"),
        Output("qrcode-output", "children"),
        Output("qrcode-storage-main", "data"),
    ],
    [
        Input("qrcode-storage-main", "data"),
    ],
    background=True,
    prevent_initial_call=True,
    cancel=[Input("text-input", "value")],
)
def update_qrcode(
    storage_main_data,
):
    if storage_main_data is None:
        return dash.no_update
    if (
        "error-corrected" not in storage_main_data
        or "rounded" not in storage_main_data
        or "gradient-color-enabled" not in storage_main_data
        or "base-color" not in storage_main_data
        or "gradient-color" not in storage_main_data
    ):
        storage_main_data["error-corrected"] = True
        storage_main_data["rounded"] = True
        storage_main_data["gradient-color-enabled"] = False
        storage_main_data["base-color"] = (0, 0, 0)
        storage_main_data["gradient-color"] = (40, 40, 40)

    QR = qrcode.QRCode(
        error_correction=(
            qrcode.constants.ERROR_CORRECT_H
            if storage_main_data["error-corrected"]
            else qrcode.constants.ERROR_CORRECT_L
        ),
        box_size=20,
        border=1,
    )

    # add data to qr code
    QR.add_data(storage_main_data["text-input"])

    # generate qr code
    QR.make(fit=True)

    # transfer the array into an actual image
    if storage_main_data["gradient-color-enabled"]:
        qrcode_output = QR.make_image(
            image_factory=StyledPilImage,
            module_drawer=(
                RoundedModuleDrawer()
                if storage_main_data["rounded"]
                else SquareModuleDrawer()
            ),
            color_mask=(
                RadialGradiantColorMask(
                    center_color=storage_main_data["base-color"],
                    edge_color=storage_main_data["gradient-color"],
                )
            ),
        )
    else:
        if storage_main_data["base-color"] == [0, 0, 0]:
            qrcode_output = QR.make_image(
                image_factory=StyledPilImage,
                module_drawer=(
                    RoundedModuleDrawer()
                    if storage_main_data["rounded"]
                    else SquareModuleDrawer()
                ),
            )
        else:
            qrcode_output = QR.make_image(
                image_factory=StyledPilImage,
                module_drawer=(
                    RoundedModuleDrawer()
                    if storage_main_data["rounded"]
                    else SquareModuleDrawer()
                ),
                color_mask=(
                    SolidFillColorMask(
                        front_color=storage_main_data["base-color"],
                    )
                ),
            )

    # # set size of QR code
    # pos = ((img.size[0] - logo.size[0]) // 2,
    #        (img.size[1] - logo.size[1]) // 2)

    # paste logo in QR code
    # img.paste(logo, pos)
    # save img to a file

    return [
        html.Div("", id="loading-state"),
        html.Img(src=qrcode_output.get_image()),
        storage_main_data,
    ]


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

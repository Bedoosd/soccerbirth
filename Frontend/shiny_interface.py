from shiny import App, ui, render
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.graph_objects as go

# Dummy data
df = pd.DataFrame({
    "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "births": [1200, 1100, 1300, 1250, 1400, 1350, 1500, 1480, 1420, 1380, 1300, 1250]})
tournaments = ["World Championship", "European Championship"]
years = ["2024", "2020", "2016"]
countries = ["Belgium", "France", "Germany"]

# adjusted size to have both championships on 1 line: 300px or 2lines 200px
custom_style = ui.tags.style("""
    aside.sidebar {
        width: 200px !important;
        min-width: 200px !important;
    }
""")

# UI layout
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons("tournament_selection", "Select a tournament:", tournaments),
        ui.input_select("year_selection", "Select a year:", years),
        ui.input_radio_buttons("country_selection", "Select a country:", countries),
        bg="#f8f8f8"
    ),
    ui.output_ui("selection_summary"),
    output_widget("birth_chart"),
    # output_widget("birth_chart_mean"),# <- Plotly widget
    custom_style
)

# Server logic
def server(inputs, outputs, session):
    @outputs
    # @render.ui
    # def selection_summary():
    #     return (
    #         f"You selected: {inputs.tournament_selection()}, "
    #         f"{inputs.year_selection()}, "
    #         f"{inputs.country_selection()}"
    #     )

    # @render_widget
    # def birth_chart_mean():
    #     average = df["births"].mean()
    #
    #     fig = go.Figure()
    #     fig.add_trace(go.Scatter(
    #         x=df["month"],
    #         y=df["births"],
    #         mode="lines+markers",
    #         name="Births"
    #     ))
    #     fig.add_trace(go.Scatter(
    #         x=df["month"],
    #         y=[average] * len(df),
    #         mode="lines",
    #         name=f"Average ({int(average)})",
    #         line=dict(dash="dash", color="red")
    #     ))
    #     fig.update_layout(
    #         title="Monthly Birth Statistics",
    #         xaxis_title="Month",
    #         yaxis_title="Number of Births"
    #     )
    #     return fig

    @render_widget
    def birth_chart():
        average = df["births"].mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["month"],
            y=df["births"],
            mode="lines+markers",
            name="Births"
        ))
        fig.add_trace(go.Scatter(
            x=df["month"],
            y=[average] * len(df),
            mode="lines",
            name=f"Average ({int(average)})",
            line=dict(dash="dash", color="red")
        ))
        fig.update_layout(
            title=f"Monthly Birth Statistics for {inputs['country_selection']()} following {inputs['tournament_selection']()} {inputs['year_selection']()}",
            xaxis_title="Month",
            yaxis_title="Number of Births"
        )
        return fig

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()

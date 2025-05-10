from shiny import App, ui, render
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.graph_objects as go
#from ??? import Tournament

wc = Tournament("World Championship")
ec = Tournament("European Championship")

tournaments = {"World Championship": wc, "European Championship": ec}
#makes x an instance of Tournament as in x = tournaments[input.tournament_selection()]

# adjusted size to have both championships on 1 line: 300px or 2lines 200px
custom_style = ui.tags.style(
    """aside.sidebar {width: 200px !important; min-width: 200px !important;}""")

# UI layout
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons("tournament_selection", "Select a tournament:", tournaments ),
        ui.input_select("available_years_selection"),
        ui.input_radio_buttons("available_countries_selection"),
        bg="#f8f8f8"
    ),
    ui.output_ui("selection_summary"),
    output_widget("birth_chart"),
    custom_style
)

# Server logic
def server(inputs, outputs, session):
    @outputs
    @render.ui
    def available_years_selection():
        tournament = tournaments[inputs["tournament_selection"]()]
        available_years = tournament.get_available_years()
        return ui.input_select("available_years_selection", "Select year:", available_years)

    def available_countries_selection():
        tournament = tournaments[inputs["tournament_selection"]()]
        available_countries = tournament.get_available_countries(inputs["available_years_selection"]())
        return ui.input_radio_buttons("available_countries_selection", "Select countries:", available_countries)

    def birth_chart_selection():
        tournament = tournaments[inputs["tournament_selection"]()]
        has_monthly_data = tournament.get_has_monthly_data(
            inputs["available_years_selection"], inputs["available_countries_selection"])
        has_yearly_data = tournament.get_has_yearly_data(
            inputs["available_years_selection"], inputs["available_countries_selection"])

        if has_monthly_data:
            monthly_data = tournament.get_monthly_data(inputs["available_years_selection"], inputs["available_countries_selection"])
            return monthly_chart(monthly_data)

        elif has_yearly_data:
            yearly_data = tournament.get_yearly_data(inputs["available_years_selection"], inputs["available_countries_selection"])
            return yearly_chart(yearly_data)

        else: return no_data_chart()


    @render_widget
    def monthly_chart(monthly_data):

        average = monthly_data["births"].mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_data["month"],
            y=monthly_data["births"],
            mode="lines+markers",
            name="Births"
        ))
        fig.add_trace(go.Scatter(
            x=monthly_data["month"],
            y=[average] * len(monthly_data),
            mode="lines",
            name=f"Average ({int(average)})",
            line=dict(dash="dash", color="red")
        ))
        fig.update_layout(
            title=(
                f"Monthly Birth Statistics for {inputs['available_countries_selection']()},"
                f"following {inputs['tournament_selection']()} {inputs['available_years_selection']()}"
            ),
            xaxis_title="Month",
            yaxis_title="Number of Births"
        )
        return fig

    @render_widget
    def yearly_chart(yearly_data):
        average = yearly_data["births"].mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly_data["month"],
            y=yearly_data["births"],
            mode="lines+markers",
            name="Births"
        ))
        fig.add_trace(go.Scatter(
            x=yearly_data["month"],
            y=[average] * len(yearly_data),
            mode="lines",
            name=f"Average ({int(average)})",
            line=dict(dash="dash", color="red")
        ))
        fig.update_layout(
            title=(
            f"No monthly data available<br>"
            f"Yearly Birth Statistics for {inputs['available_countries_selection']()},"
            f"following {inputs['tournament_selection']()} {inputs['available_years_selection']()}"
            ),
            xaxis_title="Years",
            yaxis_title="Number of Births"
        )

        return fig

    @render_widget
    def no_data_chart():
        fig = go.Figure()

        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(
                    text=f"No data available for folowing selection:<br>"
                         f"{inputs['available_countries_selection']()} at "
                         f"{inputs['tournament_selection']()}, {inputs['available_years_selection']()}",
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=20)
                    )
                ]
            )

        return fig

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()

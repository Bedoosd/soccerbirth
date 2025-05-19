from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.graph_objects as go

from Backend.country import Country
from Backend.tournament import Tournament


tournaments = ["World Championship","European Championship"]

custom_style = ui.tags.style(
    """aside.sidebar {width: 200px !important; min-width: 200px !important;}""")

# UI layout
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons("tournament_selection", "Select a tournament:", tournaments),
        ui.output_ui("available_years_selection"),
        ui.output_ui("available_countries_selection"),

        bg="#f8f8f8"
    ),
ui.input_action_button("generate_chart", "Show graph from selection"),
    output_widget("birth_chart"),
    custom_style
)

# Server logic
def server(inputs, outputs, session):
    @reactive.Calc
    def selected_tournament():
        return Tournament(inputs["tournament_selection"]())

    @outputs
    @render.ui
    def available_years_selection():
        tournament = selected_tournament()
        available_years_df = tournament.get_available_years()
        available_years = sorted(available_years_df["year"].tolist())

        if not available_years:
            return ui.div("No available years")

        return ui.input_select("available_years_selection", "Select year:", available_years)


    @render.ui
    def available_countries_selection():
        tournament = selected_tournament()
        selected_year = inputs["available_years_selection"]()
        if not selected_year:
            return ui.div("Select a year first")
        tournament.tournament_year = selected_year
        available_countries_df = tournament.get_available_countries()
        available_countries = available_countries_df["country"].tolist()

        if not available_countries:
            return ui.div("No countries available")

        return ui.input_radio_buttons("available_countries_selection", "Select countries:", available_countries)


    @render_widget
    @reactive.event(inputs.generate_chart)
    def birth_chart():
        country_selected = inputs["available_countries_selection"]()
        year = inputs["available_years_selection"]()
        country_name = inputs["available_countries_selection"]()

        if not year or not country_name:
            return go.Figure()

        tournament = selected_tournament()
        tournament.tournament_year = year
        country = Country(country_selected, tournament)

        if country.has_monthly_data():
            monthly_data, tournament_marker, target_marker = country.get_monthly_data()
            return draw_chart(monthly_data, "Monthly", "Month","month_year", tournament_marker, target_marker)

        elif country.has_yearly_data():
            yearly_data, tournament_marker, target_marker = country.get_yearly_data()
            return draw_chart(yearly_data, "Yearly", "Year",
                              "year",tournament_marker, target_marker, show_warning_text=True)

        else:
            return no_data_chart()

    def draw_chart(data, title_prefix, x_title, x_col,tournament_marker, target_marker, show_warning_text=False):
        print (data)
        average = data["births"].mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data["births"],
            mode="lines+markers",
            name="Births"
        ))
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=[average] * len(data),
            mode="lines",
            name=f"Average ({int(average)})",
            line=dict(dash="dash", color="red")

        ))
        #tournament zelf komt eigenlijk niet voor op de grafiek, start +/- 3 maanden erna pas

        # fig.add_vline(
        #     x=tournament_marker,
        #     line_dash="dot",
        #     line_color="green",
        #     annotation_text="Tournament",
        #     annotation_position="top right",
        #     annotation_font=dict(size=12, color="green")
        # )
        if target_marker is not None:
            fig.add_vline(
                x=target_marker,
                line_dash="dot",
                line_color="green",
                annotation_text="Target",
                annotation_position="top right",
                annotation_font=dict(size=12, color="green")
            )

        if show_warning_text:
            fig.add_annotation(
                text="No monthly data available — showing yearly data instead",
                xref="paper", yref="paper",
                x=0.5, y=1.15, showarrow=False,
                font=dict(size=14, color="black"),
                xanchor="center"
            )
        #follwing is because the yearly graph wasnt displayed in the right format
        if pd.api.types.is_numeric_dtype(data[x_col]):
            fig.update_layout(
                xaxis=dict(
                    range=[(data[x_col].min())-1, (data[x_col].max()) + 1]
                )
            )
        fig.update_layout(
            title=dict(
                text=(
                    f"{title_prefix} Birth Statistics for {inputs['available_countries_selection']()}, "
                    f"following {inputs['tournament_selection']()} {inputs['available_years_selection']()}"
                ),
                x=0.5,
                xanchor="center"
            ),
            xaxis_title=x_title,
            yaxis_title="Number of Births",
            margin=dict(t=90),
        )

        return fig

    def no_data_chart():
        fig = go.Figure()

        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(
                    text=f"No birth rates available for following selection:<br>"
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

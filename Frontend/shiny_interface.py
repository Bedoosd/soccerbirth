
from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.graph_objects as go

from Backend.country import Country
from Backend.tournament import Tournament

tournaments = ["World Championship", "European Championship"]

custom_style = ui.tags.style(
    """aside.sidebar {width: 200px !important; min-width: 200px !important;}"""
)

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

    ui.tags.div(
        ui.output_ui("statistics_box"),
        style="""
            border: 1px solid #ccc;
            background-color: #f9f9f9;
            padding: 12px;
            margin-top: 20px;
            border-radius: 6px;
            text-align: left;
            color: #444;
        """
    ),

    custom_style
)

def server(inputs, outputs, session):
    reactive_data = reactive.Value(None)

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

    @outputs
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

    @outputs
    @render_widget
    @reactive.event(inputs.generate_chart)
    def birth_chart():
        country_selected = inputs["available_countries_selection"]()
        year = inputs["available_years_selection"]()
        if not year or not country_selected:
            reactive_data.set(None)
            return go.Figure()

        tournament = selected_tournament()
        tournament.tournament_year = year
        country = Country(country_selected, tournament)

        if country.has_monthly_data():
            monthly_data, tournament_marker, target_marker = country.get_monthly_data()
            reactive_data.set((monthly_data, tournament_marker, target_marker, False)) #to send to statistics_box, tuple (dubbele haakjes)
            return draw_chart(monthly_data, "Monthly", "Month", "month_year", tournament_marker, target_marker, False)

        elif country.has_yearly_data():
            yearly_data, tournament_marker, target_marker = country.get_yearly_data()
            reactive_data.set((yearly_data, tournament_marker, target_marker, True))
            return draw_chart(yearly_data, "Yearly", "Year", "year", tournament_marker, target_marker, True)

        else:
            reactive_data.set(None)
            return no_data_chart()

    def draw_chart(data, title_prefix, x_title, x_col, tournament_marker, target_marker, show_warning_text=False):
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

        if tournament_marker is not None:
            fig.add_vline(
                x=tournament_marker,
                line_dash="dot",
                line_color="green",
                annotation_text="Tournament",
                annotation_position="top right",
                annotation_font=dict(size=12, color="green")
            )

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
        #yearly graph doesnt automatically display in the right scale
        if pd.api.types.is_numeric_dtype(data[x_col]):
            fig.update_layout(
                xaxis=dict(range=[data[x_col].min() - 1, data[x_col].max() + 1])
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
                    text=f"No birth rates available for the selection:<br>"
                         f"{inputs['available_countries_selection']()} at "
                         f"{inputs['tournament_selection']()}, {inputs['available_years_selection']()}",
                    xref="paper", yref="paper", showarrow=False, font=dict(size=20)
                )
            ]
        )
        return fig

    @outputs
    @render.ui
    def statistics_box():
        value = reactive_data.get()
        if not value:
            return ui.HTML("No data to display.")

        data, tournament_marker, target_marker, show_warning_text = value
        average = data["births"].mean()
        avg_text = f"{average:.0f}"
        if target_marker is not None:
            target_average = data["births"][int(target_marker) - 2: int(target_marker) + 2].mean()
            target_avg_text = f"{target_average:.0f}"
        else:
            target_avg_text = "N/A"

        if show_warning_text:
            return ui.HTML(f"The average birth numbers over the displayed years = {avg_text}")
        else:
            return ui.HTML(f"""
                The average birth number over the displayed months = {avg_text}<br>
                The average birth number 4 months around the target = {target_avg_text}
            """)

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()

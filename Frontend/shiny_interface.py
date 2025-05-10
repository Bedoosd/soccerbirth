from shiny import App, ui, render
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.graph_objects as go

#generated some dummy data to be able to test the app without backend
class MockTournament:
    def __init__(self, name):
        self.name = name

    def get_available_years(self):
        if self.name == "European Championship":
            return ["2021", "2022", "2023"]
        else: return ["2017","2018", "2019", "2020"]

    def get_available_countries(self, year):
        if self.name == "European Championship":
            if year == "2021": return ["Belgium", "Bulgaria", "Croatia"]
            if year == "2022": return ["Czech Republic", "Denmark", "Finland"]
            if year == "2023": return ["France", "Belgium", "Italy"]
        else:
            if year == "2017": return ["Japan", "Germany", "France"]
            if year == "2018": return ["Czech Republic", "Argentina", "Finland"]
            if year == "2019": return ["France", "Germany", "China"]
            if year == "2020": return ["Morocco", "Tunisia", "Poland"]

    def get_has_monthly_data(self, year, country):
        if self.name == "European Championship":
            if year == "2021" and (country == "Belgium" or country == "Bulgaria"): return False
            else: return True
        else:
            if year == "2017" and country == "France": return False
            else: return True


    def get_has_yearly_data(self, year, country):
        if self.name == "European Championship":
            if year == "2021" and country == "Belgium": return False
            else: return True

    def get_monthly_data(self, year, country):
        return pd.DataFrame({
            "month": ["Jan", "Feb", "Mar", "Apr"],
            "births": [100, 120, 90, 110]
            })

    def get_yearly_data(self, year, country):
        return pd.DataFrame({
            "years": ["2020", "2021", "2022"],
            "births": [1200, 1300, 1250]
            })


wc = MockTournament("World Championship")
ec = MockTournament("European Championship")

tournaments = {"World Championship": wc, "European Championship": ec}

custom_style = ui.tags.style(
    """aside.sidebar {width: 200px !important; min-width: 200px !important;}""")

# UI layout
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons("tournament_selection", "Select a tournament:", list(tournaments.keys())),
        ui.output_ui("available_years_selection"),
        ui.output_ui("available_countries_selection"),
        bg="#f8f8f8"
    ),
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


    @render.ui
    def available_countries_selection():
        tournament = tournaments[inputs["tournament_selection"]()]
        available_countries = tournament.get_available_countries(inputs["available_years_selection"]())
        return ui.input_radio_buttons("available_countries_selection", "Select countries:", available_countries)


    @render_widget
    def birth_chart():
        tournament = tournaments[inputs["tournament_selection"]()]
        year = inputs["available_years_selection"]()
        country = inputs["available_countries_selection"]()

        if tournament.get_has_monthly_data(year, country):
            monthly_data = tournament.get_monthly_data(year, country)
            return draw_chart(monthly_data, "Monthly", "Month", "month")

        elif tournament.get_has_yearly_data(year, country):
            yearly_data = tournament.get_yearly_data(year, country)
            return draw_chart(yearly_data, "No monthly data available<br>Yearly", "Year", "years")

        else:
            return no_data_chart()

    def draw_chart(data, title_prefix, x_title, x_col):
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
        fig.update_layout(
            title=(
                f"{title_prefix} Birth Statistics for {inputs['available_countries_selection']()}, "
                f"following {inputs['tournament_selection']()} {inputs['available_years_selection']()}"
            ),
            xaxis_title=x_title,
            yaxis_title="Number of Births"
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

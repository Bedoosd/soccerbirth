import math
from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.graph_objects as go

from Backend.country import Country
from Backend.get_binomial import get_binomial
from Backend.get_chi2 import get_chi2
from Backend.tournament import Tournament

tournaments = ["World Championship", "European Championship"]
compare_methods = {
    "Same month in previous/next year": "same months",
    "Average of surrounding two years": "full year"}

rounds = ["Final_P1", "Final", "Semi_final", "Quarter_final", "Round_of_16", "Group_phase"]
custom_style = ui.tags.style(
     """aside.sidebar {width: 200px !important; min-width: 200px !important;}""")

app_ui = ui.page_fluid(
    ui.output_ui("page_content")
)

def server(inputs, outputs, session):
    current_page = reactive.Value("main")
    reactive_data = reactive.Value()
    target_avg_months = reactive.Value()
    reactive_chi2 = reactive.Value()
    show_conclusion_flag = reactive.Value(False)

    @outputs
    @render.ui
    def page_content():
        if current_page.get() == "main":
            return ui.page_sidebar(
            ui.sidebar(
                ui.input_radio_buttons("tournament_selection", "Select a tournament:", tournaments),
                ui.output_ui("available_years_ui"),
                ui.output_ui("available_countries_ui"),
                bg="#f8f8f8"
            ),
            ui.input_action_button("generate_chart", "Show graph from selection"),
            ui.input_action_button("open_stats", "Go to statistic page"),
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
        else:
            return ui.page_sidebar(
                ui.sidebar(
                    ui.input_radio_buttons("method_selection", "Select a comparison method:",
                                           list(compare_methods.keys())),
                    ui.input_radio_buttons("round_reached", "Compare countries that reached:", rounds),
                    bg="#f8f8f8"
                ),
                ui.input_action_button("generate_result", "Show the result from selection"),
                ui.input_action_button("conclusion", "Show conclusion"),
                ui.input_action_button("go_back", "Back to graph page"),

                output_widget("show_result_chart"),
                ui.tags.div(
                    ui.output_ui("statistics_box_chi2"),
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

    @reactive.Calc
    def selected_tournament():
        return Tournament(inputs["tournament_selection"]())

    @outputs
    @render.ui
    def available_years_ui():
        tournament = selected_tournament()
        available_years_df = tournament.get_available_years()
        available_years = sorted(available_years_df["year"].tolist())
        if not available_years:
            return ui.div("No available years")
        return ui.input_select("available_years_selection", "Select year:", available_years)

    @outputs
    @render.ui
    def available_countries_ui():
        tournament = selected_tournament()
        selected_year = inputs["available_years_selection"]()
        if not selected_year:
            return ui.div("Select a year first")
        tournament.tournament_year = selected_year
        available_countries_df = tournament.get_available_countries()
        available_countries = available_countries_df["country_name"].tolist()
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
            monthly_data, tournament_marker, target_marker = country.get_monthly_data(months_margin=14)
            if len (monthly_data) > 10:
                reactive_data.set((monthly_data, tournament_marker, target_marker, False))
                target_avg_months.set([monthly_data["year_month_txt"][int(target_marker) -1],
                                       monthly_data["year_month_txt"][int(target_marker) + 1]])
                return draw_chart(monthly_data, "Monthly", "Month", "year_month_txt",
                                  tournament_marker, target_marker, False)

        if country.has_yearly_data():
            yearly_data, tournament_marker, target_marker = country.get_yearly_data(years_margin=4)
            if len (yearly_data) > 3:
                reactive_data.set((yearly_data, tournament_marker, target_marker, True))
                return draw_chart(yearly_data, "Yearly", "Year", "year",
                                  tournament_marker, target_marker, True)
            else:
                reactive_data.set(None)
                return no_data_chart()

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
                annotation_position="top left",
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
        target_average = None
        births_compared = 0
        if target_marker is not None:
            target_average = data["births"][int(target_marker) - 1: int(target_marker) + 1].mean()
            target_avg_text = f"{target_average:.0f}"
            births_compared = ((target_average / average) - 1) * 100
        else:
            target_avg_text = "N/A"
        if births_compared < 0:
            births_compared_text = f"There are {abs(births_compared):.2f}% less births around this target."
        else:
            births_compared_text = f"There are {births_compared:.2f}% more births around this target."
        if show_warning_text:
            return ui.HTML(f"The average birth number over the displayed years is: {int(average)} births.")

        elif math.isnan(target_average):
            return ui.HTML(f"""The average birth number over the displayed years is: {int(average)} births.<br>
                            Not enough data to calculate the average around the target.""")

        else:
            dates_to_display = target_avg_months.get()
            return ui.HTML(f"""
                The average birth number over the displayed months is: {int(average)} births.<br>
                The average number of births from {dates_to_display[0]} until {dates_to_display[1]} is : {target_avg_text} births.<br>
                {births_compared_text} 
            """)

    @reactive.Calc
    @reactive.event(inputs.generate_result)
    def result_figure():
        selected_method = compare_methods.get(inputs["method_selection"]())
        selected_round = inputs["round_reached"]()
        chi2, probability, significant, df_graph, count_yes, count_no = get_chi2(selected_method, selected_round)
        reactive_chi2.set((chi2, probability, significant, df_graph, count_yes, count_no))

        #following was to get to display Final instead of Final_P2 without changing a lot of code
        selected_round = "Final_P2" if selected_round == "Final" else selected_round
        displayed_round = "Final" if selected_round == "Final_P2" else selected_round

        x_labels = df_graph["did reach " + selected_round + "?"]
        x_labels_with_counts = x_labels.map(lambda x: f"{x} ({count_yes} cases)" if x == "yes" else f"{x} ({count_no} cases)")
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=x_labels_with_counts,
            y=df_graph["less births"],
            name="Less births",
            marker_color="indianred",
            text=df_graph["less births"].round(1).astype(str) + "%",
            textposition="outside"
        ))

        fig.add_trace(go.Bar(
            x=x_labels_with_counts,
            y=df_graph["more births"],
            name="More births",
            marker_color="lightblue",
            text=df_graph["more births"].round(1).astype(str) + "%",
            textposition="outside"
        ))

        fig.update_layout(
            barmode="group",
            title=dict(
                text=f"Birth deviation by reaching {displayed_round}",
                x=0.5,
                xanchor="center",
                font=dict(size=24)
            ),
            xaxis_title= f"Reached {displayed_round}",
            yaxis_title="Percentage",
            legend_title="Birth Deviation",
            yaxis=dict(range=[0, 110]),
            xaxis = dict(tickfont=dict(size=15)),
            margin=dict(t=90),
        )

        return fig

    @reactive.Effect
    @reactive.event(inputs.conclusion)
    def handle_conclusion():
        show_conclusion_flag.set(True)

    @reactive.Effect
    @reactive.event(inputs.generate_result)
    def reset_conclusion():
        show_conclusion_flag.set(False)

    @outputs
    @render_widget
    def show_result_chart():
        if show_conclusion_flag.get():
            return None
        fig = result_figure()
        return fig

    @outputs
    @render.ui
    def statistics_box_chi2():
        if show_conclusion_flag():
            binomial_result, p_value = get_binomial()

            return ui.HTML(
                f"The study investigated the popular myth that there is an increase in births <br>"
                f"approximately nine months after a country performs well in a European or World Cup football tournament.<br><br>"
                f"However, the visual data already suggests a different story.<br>"
                f"Using the collected data, a chi-squared test was performed, which supports the conclusion that the myth is false.<br><br>"
                f"In fact, the analysis shows a <strong>67.1% decrease</strong> in births nine months after the tournaments, <br>"
                f"based on data from the same month one year before and one year after the event.<br><br>"
                f"To test the significance of this result, a binomial test was conducted.<br>"
                f"The p-value obtained from this test is: <strong>{p_value:.10f}</strong>.<br>"
                f"Since a p-value below 0.05 indicates statistical significance, <br>"
                f"this study finds that there is <strong>{'a' if binomial_result else 'no'}</strong> significant decline in births <br>"
                f"nine months after a major football tournament across the observed countries."
            )
        results = reactive_chi2.get()
        if not results:
            return ui.HTML("Make a selection and generate to get your results.")
        chi2, probability, significant, df_graph, count_yes, count_no = results

        return ui.HTML(
            f"For the selected method and the reached round:<br>"
            f"The chi² value is: <strong>{chi2}</strong>.<br>"
            f"The probability is: <strong>{probability}</strong>, which is "
            f"{'less' if significant else 'greater'} than 0.05.<br>"
            f"Therefore, the reached round has "
            f"{'a' if significant else 'no'} statistically significant influence on birth numbers."
        )

    @reactive.Effect
    @reactive.event(inputs.open_stats)
    def go_to_stats():
        reactive_chi2.set(None) #was needed to clear chi2_box
        current_page.set("stats")

    @reactive.Effect
    @reactive.event(inputs.go_back)
    def go_back():
        reactive_data.set(None) #else it keeps showing the previous data in the statistics_box on return
        current_page.set("main")


app = App(app_ui, server)

if __name__ == "__main__":
    app.run()

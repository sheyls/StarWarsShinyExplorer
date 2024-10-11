import plotly.express as px
import pandas as pd
from shiny import App, reactive, render, ui
import tempfile

# Load Star Wars characters dataset
characters_df = pd.read_csv("star-wars.csv")

# Variables for controls
species_choices = characters_df['species'].dropna().unique().tolist()
gender_choices = characters_df['sex'].dropna().unique().tolist()


# Define the UI
app_ui = ui.page_sidebar(
    
    ui.sidebar(
        ui.input_checkbox_group("species", "Select Species", species_choices, selected=species_choices),
        ui.input_checkbox_group("gender", "Select Genders", gender_choices, selected=gender_choices),
        ui.input_action_button("reset", "Reset Filters")
    ),

    # Add the table in a row that spans the full width
    ui.layout_columns(
        ui.column(
            12,
            ui.output_data_frame("table")
        )
    ),
    # Place the plot below the statistics in the same column
    ui.layout_columns(
        ui.column(
            4,
            ui.output_ui("total_characters"),
            ui.output_ui("average_height"),
            ui.output_ui("average_mass"),
            ui.output_image("species_gender_plot")  # Move the plot here
        )
    ),
    title="Star Wars Characters Analysis"
)


# Server logic
def server(input, output, session):
    @reactive.Calc
    def filtered_data():
        selected_species = input.species()
        selected_gender = input.gender()
        return characters_df[
            (characters_df['species'].isin(selected_species)) & 
            (characters_df['sex'].isin(selected_gender))
        ]

    @render.ui
    def total_characters():
        return f"Total Characters: {filtered_data().shape[0]}"

    @render.ui
    def average_height():
        data = filtered_data()
        if data.shape[0] > 0:
            return f"Average Height: {data['height'].mean():.2f} cm"
        return "Average Height: N/A"

    @render.ui
    def average_mass():
        data = filtered_data()
        if data.shape[0] > 0:
            return f"Average Mass: {data['mass'].mean():.2f} kg"
        return "Average Mass: N/A"

    @render.data_frame
    def table():
        return filtered_data()[['name', 'species', 'height', 'mass', 'homeworld', 'sex']]

    @render.image
    def species_gender_plot():
        data = filtered_data()
        fig = px.bar(data, x='species', color='sex', barmode='group', title="Species Distribution by Gender")
        # Save the plot as a PNG image
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        fig.write_image(temp_file.name)
        
        # Return a dictionary with 'src' and 'alt' for the image
        return {"src": temp_file.name, "alt": "Species Distribution by Gender"}


    @reactive.effect
    @reactive.event(input.reset)
    def _():
        ui.update_checkbox_group("species", selected=species_choices)
        ui.update_checkbox_group("gender", selected=gender_choices)


# Create the app
app = App(app_ui, server)

# Run the application
if __name__ == "__main__":
    app.run()

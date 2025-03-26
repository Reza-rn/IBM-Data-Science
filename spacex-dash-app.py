# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Extract unique launch sites
launch_sites = spacex_df['Launch Site'].unique()
launch_site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=launch_site_options,
                                    value='ALL',  # Default to all sites
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # For ALL sites, count success and failure for each site separately
        success_counts = spacex_df.groupby(['Launch Site', 'class']).size().reset_index(name='count')

        # Generate the pie chart with different colors for each launch site
        fig = px.pie(success_counts, values='count', names='Launch Site', color='Launch Site', 
                     title='Launch Success vs Failed for All Sites',
                     color_discrete_map={site: px.colors.qualitative.Set1[i] for i, site in enumerate(spacex_df['Launch Site'].unique())})
        return fig
    else:
        # For a specific site, show success vs failure in blue and red
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']

        # Color map: success (1) will be blue, failure (0) will be red
        color_map = {0: 'red', 1: 'blue'}
        
        fig = px.pie(success_counts, values='count', names='class',
                     title=f'Launch Success vs Failed for {entered_site}',
                     color='class', 
                     color_discrete_map=color_map)
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id="payload-slider", component_property="value")
    ]
)
def get_scatter_plot(entered_site, selected_payload_range):
    # Filter the data based on the selected payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
                            (spacex_df['Payload Mass (kg)'] <= selected_payload_range[1])]

    if entered_site == 'ALL':
        # For ALL sites, plot all payload vs success data, colored by booster version category
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', 
                         color='Booster Version Category', 
                         title='Payload vs Success for All Sites',
                         labels={'Payload Mass (kg)': 'Payload Mass (kg)', 'class': 'Mission Outcome'})
        return fig
    else:
        # For specific launch site, filter by launch site and payload range
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        # Plot scatter chart for selected launch site, colored by booster version category
        fig = px.scatter(site_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category', 
                         title=f'Payload vs Success for {entered_site}',
                         labels={'Payload Mass (kg)': 'Payload Mass (kg)', 'class': 'Mission Outcome'})
        return fig


# Run the app
if __name__ == '__main__':
    app.run(port=8051)

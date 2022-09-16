import pandas as pd, numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from ast import literal_eval

import plotly.graph_objects as go
from plotly.subplots import make_subplots

""""
This app is for educational purposes, to analyze the steam data based on the sales period as of 13/09/2022.
The features are represented as Publisher, Category, and Release year.
"""

# Initiate the app for dash
app = Dash(__name__)
app.name = "Steam EDA"

# This is for hosting it with heroku
server = app.server 

# Main dataframe
df = pd.read_csv('https://raw.githubusercontent.com/zackfair1/steam_eda/main/steam_data.csv')
df['categories'] = df.categories.apply(literal_eval)

# Main app HTML layout
app.layout = html.Div([
    html.H3('Choose a feature', style={"text-align":"center"}),
    dcc.Dropdown(['publisher','categories', 'release_year'], 'publisher', id='demo-dropdown', style={"width":"45%","margin":"10px auto"}),
    dcc.Graph(id="graph"),
])

# This is where the interaction magic happens. Making calls to the dashboard (HTML layout), based on the dropdown menu chosen (our input -- ddc.Dropdown), whereas the output is the graph (ddc.Graph)
@app.callback(
    Output("graph", "figure"), 
    Input("demo-dropdown", "value"))
def update_line_chart(feature):
    # Dataframe
    df1 = df.copy()
    
    if feature == 'categories':
        df1 = df1.explode('categories')
        df1 = df1.groupby([feature]).agg({'name':'count','rating_before':'mean','rating_after':'mean','positive_ratings':'mean','negative_ratings':'mean'}).sort_values('name', ascending=False).reset_index().head(20).round(2)
    elif feature == 'release_year':
        df1 = df1.groupby([feature]).agg({'name':'count','rating_before':'mean','rating_after':'mean','positive_ratings':'mean','negative_ratings':'mean'}).sort_values([feature,'name'], ascending=False).reset_index().head(20).round(2)
    else:
        df1 = df1.groupby([feature]).agg({'name':'count','rating_before':'mean','rating_after':'mean','positive_ratings':'mean','negative_ratings':'mean'}).sort_values('name', ascending=False).reset_index().head(20).round(2)
    
    # Custom data for the hovertemplate
    customdata = np.stack((df1['name'], df1['rating_before'], df1['rating_after'],df1['positive_ratings'], df1['negative_ratings']), axis=-1)

    # Main subplot
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(x=df1[feature],
            y=df1.name,
            text=df1.name,
            hovertemplate='Number of games: %{customdata[0]}<extra></extra>',
            name='N° of games',
            ),)

    fig.add_trace(
        go.Bar(
            x=df1[feature],
            y=df1.rating_before,
            text=df1.rating_before,
            hovertemplate='Rating before discount: %{customdata[1]}%<extra></extra>',
            name='Rating beforedf1 discount',
            # mode='lines+markers', # line=dict(color="#FC8D62")
            # marker_size=5
        ),)

    fig.add_trace(
        go.Bar(
            x=df1[feature],
            y=df1.rating_after,
            text=df1.rating_after,
            hovertemplate='Rating after discount: %{customdata[2]}%<extra></extra>',
            name='Rating after discount',
            # mode='lines+markers',
            ))

    fig.add_trace(
        go.Scatter(
            x=df1[feature],
            y=df1.positive_ratings,
            hovertemplate='Positive ratings: %{customdata[3]}<extra></extra>',
            name='Positive ratings',
            mode='lines+markers',
            line_color='#9467BD',
        ))

    fig.add_trace(
        go.Scatter(
            x=df1[feature],
            y=df1.negative_ratings,
            hovertemplate='Negative ratings: %{customdata[4]}<extra></extra>',
            name='Negative ratings',
            mode='lines+markers',
            line_color='#D62728',
        ))

    fig.update_yaxes(type="log")

    fig.update_layout(
        autosize=True,
        width=1800,
        height=850,
        hovermode="x unified",
        title={
            'text': f"Top {len(df1)} by {feature} - Game Releases & Ratings",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        template='simple_white'
    )
    fig.update_yaxes(title_text="<b>Total/Percentage</b> ratings", )
    fig.update_xaxes(title_text="Publisher")

    fig.update_traces(customdata=customdata)
    return fig


if __name__ == '__main__':
    app.run_server(debug=False)

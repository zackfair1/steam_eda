import pandas as pd, numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from ast import literal_eval

import plotly.graph_objects as go
from plotly.subplots import make_subplots

app = Dash(__name__)
server = app.server
app.title = "Steam EDA"

# Main df
df = pd.read_csv('https://raw.githubusercontent.com/zackfair1/steam_eda/main/steam_data.csv')
df['categories'] = df.categories.apply(literal_eval)

# Secondary df
df2 = pd.read_csv(r'C:\Users\zacke\OneDrive - vgytk\Desktop\Steam Data Analysis\steam_sentiments.csv')
df2['review_score'] = df2['review_score'].astype(str)
df2['review_score'] = np.where(df2.review_score == '1', 'Recommended', 'Not Recommended')
df2['categories'] = df2.categories.apply(literal_eval)
df2['label'] = df2['label'].str.replace(r'[a-zA-Z ]', '', regex=True).astype(int)
df2['review'] = df2.label - 3

app.layout = html.Div([
    html.H3('Choose a feature', style={"text-align":"center"}),
    dcc.Dropdown(['Publisher by recommendations', 'Publisher by review sentiment','Publisher by N° Games', 'Game', 'Game by review sentiment','Categories by recommendations','Categories by review sentiment', 'release_year', 'release_year by review sentiment'], 'Publisher by recommendations', id='demo-dropdown', style={"width":"45%","margin":"10px auto"}), # 'Categories by N° Games', 
    dcc.Graph(id="graph"),
])


@app.callback(
    Output("graph", "figure"), 
    Input("demo-dropdown", "value"))
def update_line_chart(feature):
    # Dataframe
    df1 = df.copy()
    if feature == 'Publisher by recommendations':
        feature = 'publisher'
        df1 = df2.copy()
        df1 = df1.groupby([feature, 'review_score']).agg({'text':'count'}).reset_index().sort_values('text', ascending=False).head(100).round(2)
        customdata = np.stack((df1[feature], df1['review_score']), axis=-1)
        
    elif feature == 'Categories by recommendations':
        feature = 'categories'
        df1 = df2.copy()
        df1 = df1.explode('categories')
        df1 = df1.groupby([feature, 'review_score']).agg({'text':'count'}).reset_index().sort_values('text', ascending=False).head(100).round(2)
        customdata = np.stack((df1[feature], df1['review_score']), axis=-1)
        
    elif feature == 'Publisher by review sentiment':
        feature = 'publisher'
        df1 = df2.copy()
        df1 = df1.groupby([feature, 'review']).agg({'text':'count'}).reset_index().sort_values(['text','review'], ascending=False).head(50).round(2)
        df1['weight'] = df1.review * df1.text
        df1['color'] = np.where(df1.weight > 0, 'Pos', 'Neg')
        customdata = np.stack((df1[feature], df1['review']), axis=-1)
        
    elif feature == 'Categories by N° Games':
        feature = 'categories'
        df1 = df1.explode('categories')
        df1 = df1.groupby([feature]).agg({'name':'count','rating_before':'mean','rating_after':'mean','positive_ratings':'mean','negative_ratings':'mean'}).sort_values('name', ascending=False).reset_index().head(50).round(2)
        customdata = np.stack((df1['name'], df1['positive_ratings'], df1['negative_ratings']), axis=-1) # df1['rating_before'], df1['rating_after'],
        
    elif feature == 'Categories by review sentiment':
        feature = 'categories'
        df1 = df2.copy()
        df1 = df1.explode('categories')
        df1 = df1.groupby([feature, 'review']).agg({'text':'count'}).reset_index().sort_values(['text','review'], ascending=False).head(50).round(2)
        df1['weight'] = df1.review * df1.text
        df1['color'] = np.where(df1.weight > 0, 'Pos', 'Neg')
        customdata = np.stack((df1[feature], df1['review']), axis=-1)
        
    elif feature == 'release_year':
        df1 = df1.groupby([feature]).agg({'name':'count','rating_before':'mean','rating_after':'mean','positive_ratings':'mean','negative_ratings':'mean'}).sort_values([feature,'name'], ascending=False).reset_index().head(20).round(2)
        customdata = np.stack((df1['name'], df1['positive_ratings'], df1['negative_ratings']), axis=-1) # df1['rating_before'], df1['rating_after'],
    
    elif feature == 'release_year by review sentiment':
        feature = 'release_year'
        df1 = df2.copy()
        df1 = df1.groupby([feature, 'review']).agg({'text':'count'}).reset_index().sort_values(['text','review'], ascending=False).head(50).round(2)
        df1['weight'] = df1.review * df1.text
        df1['color'] = np.where(df1.weight > 0, 'Pos', 'Neg')
        customdata = np.stack((df1[feature], df1['review']), axis=-1)
    
    elif feature == 'Game':
        feature = 'name'
        df1 = df2.copy()
        df1 = df1.groupby([feature, 'review_score']).agg({'text':'count'}).reset_index().sort_values('text', ascending=False).head(100).round(2)
        customdata = np.stack((df1[feature], df1['review_score']), axis=-1)
    elif feature == 'Game by review sentiment':
        feature = 'name'
        df1 = df2.copy()
        df1 = df1.groupby([feature, 'review']).agg({'text':'count'}).reset_index().sort_values(['text','review'], ascending=False).head(50).round(2)
        df1['weight'] = df1.review * df1.text
        df1['color'] = np.where(df1.weight > 0, 'Pos', 'Neg')
        customdata = np.stack((df1[feature], df1['review']), axis=-1)
        
    elif feature == 'Publisher by N° Games':
        feature = 'publisher'
        df1 = df1.groupby([feature]).agg({'name':'count','rating_before':'mean','rating_after':'mean','positive_ratings':'mean','negative_ratings':'mean'}).sort_values('name', ascending=False).reset_index().head(20).round(2)
        customdata = np.stack((df1['name'], df1['positive_ratings'], df1['negative_ratings']), axis=-1) # df1['rating_before'], df1['rating_after'],
    else:
        df1 = df1.groupby([feature]).agg({'name':'count','rating_before':'mean','rating_after':'mean','positive_ratings':'mean','negative_ratings':'mean'}).sort_values('name', ascending=False).reset_index().head(20).round(2)
        customdata = np.stack((df1['name'], df1['positive_ratings'], df1['negative_ratings']), axis=-1) # df1['rating_before'], df1['rating_after'],
    
    # Custom data for the hovertemplate

    # Main subplot
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if 'rating_before' in df1.columns or  'rating_after' in df1.columns:
        fig.add_trace(
            go.Bar(x=df1[feature],
                y=df1.name,
                text=df1.name,
                hovertemplate='Number of games: %{customdata[0]}<extra></extra>',
                name='N° of games',
                ),)

        # fig.add_trace(
        #     go.Bar(
        #         x=df1[feature],
        #         y=df1.rating_before,
        #         text=df1.rating_before,
        #         hovertemplate='Rating before discount: %{customdata[1]}%<extra></extra>',
        #         name='Rating beforedf1 discount',
        #         # mode='lines+markers', # line=dict(color="#FC8D62")
        #         # marker_size=5
        #     ),)

        # fig.add_trace(
        #     go.Bar(
        #         x=df1[feature],
        #         y=df1.rating_after,
        #         text=df1.rating_after,
        #         hovertemplate='Rating after discount: %{customdata[2]}%<extra></extra>',
        #         name='Rating after discount',
        #         # mode='lines+markers',
        #         ))

        fig.add_trace(
            go.Bar(
                x=df1[feature],
                y=df1.positive_ratings,
                hovertemplate='Positive ratings: %{customdata[1]}<extra></extra>',
                name='Positive ratings',
                marker_color='#8AB148',
                text=df1.positive_ratings.unique(),
                # mode='lines+markers',
                # line_color='#9467BD',
            ))

        fig.add_trace(
            go.Bar(
                x=df1[feature],
                y=df1.negative_ratings,
                hovertemplate='Negative ratings: %{customdata[2]}<extra></extra>',
                text=df1.negative_ratings.unique(),
                name='Negative ratings',
                marker_color='#CD6AB1'
                # mode='lines+markers',
                # line_color='#D62728',
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
    
    elif 'weight' in df1.columns:
        fig = px.bar(data_frame=df1, x=feature, y='weight', color='color', hover_data={feature:False,'text':True},hover_name=feature, text='text', barmode='group')
        fig.update_layout(
            autosize=True,
            width=1800,
            height=850,
            title={
                'text': f'Top {len(df1[feature].unique())} based on the {feature} and the sentiment analysis',
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        )

    else:
        fig = px.bar(data_frame=df1, x=feature, y='text', color='review_score', color_discrete_sequence=["#8AB148", "#CD6AB1"], hover_data={'review_score':False,'text':True, feature:False},hover_name=feature, text='text')
        fig.update_layout(
            autosize=True,
            width=1800,
            height=850,
            title={
                'text': f'Top {len(df1[feature].unique())} based on the {feature} and review recommendations',
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            template='simple_white'
        )

    fig.update_traces(customdata=customdata)
    return fig


if __name__ == '__main__':
    app.run_server(debug=False)

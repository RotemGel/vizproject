import pandas as pd
import geopandas as gpd
import streamlit as st
import plotly.express as px

df = pd.read_csv("C:/Users/rotem/Downloads/vizudata/Global_Earthquake_Data.csv")

# get cotinent from 'longtitude' and 'latitude' columns
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))


df_with_continents = gpd.sjoin(gdf, world, how="left", op='intersects')
df_with_continents['geometry'] = df_with_continents.geometry.where(df_with_continents.geometry.notnull(), gdf.geometry)
world['centroid'] = world.geometry.centroid
continents = world.dissolve(by='continent')['centroid']


def closest_continent(point):
    distances = continents.distance(point)
    return distances.idxmin()


df_with_continents.loc[df_with_continents['continent'].isnull(), 'continent'] = df_with_continents[df_with_continents['continent'].isnull()]['geometry'].apply(closest_continent)
df_with_continents['continent'] = df_with_continents['continent'].replace('Oceania', 'Australia')

# drop rows with null values in 'depth' column
df_with_continents = df_with_continents.dropna(subset=['depth'])

# get decade from 'time' column
df_with_continents['time'] = pd.to_datetime(df_with_continents['time'])
df_with_continents['year'] = df_with_continents['time'].dt.year
df_with_continents['decade'] = (df_with_continents['year'] // 10) * 10
df_with_continents['country'] = df_with_continents['name']

# drop irrelevent columns
cols = ['id', 'year', 'decade', 'depth', 'mag','longitude','latitude', 'continent', 'country']
df = df_with_continents[cols]
df = df.rename(columns={'mag': 'magnitude'})


def main():
    st.title('Visualization of Data - Final Project')

    # Box plot
    st.header('Box plot: Magnitude by Decade')
    fig_box = px.box(df, x="decade", y="magnitude",
                     labels={
                         "decade": "Decade",
                         "magnitude": "Magnitude",
                     },
                     title="Magnitude by Decade",
                     template="simple_white")
    st.plotly_chart(fig_box)

    # Scatter Geo plot with slider for year
    st.header('Scatter Geo plot: Earthquake-prone areas over time')
    df1 = df
    df1 = df1.sort_values('year')

    # Define the color scale with low values as light and high values as dark
    color_scale = px.colors.sequential.Reds

    fig_geo = px.scatter_geo(df1, lat='latitude', lon='longitude',
                             color="magnitude",
                             hover_name="id",
                             animation_frame="year",
                             projection="natural earth",
                             labels={
                                 "latitude": "Latitude",
                                 "longitude": "Longitude",
                                 "magnitude": "Magnitude"
                             },
                             title="Earthquake-prone areas over time",
                             template="simple_white",
                             color_continuous_scale=color_scale)

    fig_geo.update_traces(marker=dict(line=dict(width=0)))  # Remove marker borders

    fig_geo.update_layout(
        coloraxis_colorbar=dict(
            title="Magnitude",
            dtick=1
        ),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(label="Play",
                         method="animate",
                         args=[None]),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[None]
                    )
                ]
            )
        ]
    )

    st.plotly_chart(fig_geo, width=800, height=600)

    # Histogram plot: Frequency of Earthquake Events in Different Countries
    st.header('Histogram: Frequency of Earthquake Events in Different Countries')

    # Get a list of unique continents
    continents = df['continent'].unique().tolist()

    # Create a select box for the continents
    selected_continent = st.selectbox('Select a continent', continents)

    # Filter the dataframe based on the selected continent
    df2 = df[df['continent'] == selected_continent]

    fig_hist = px.histogram(df2, x="country",
                            labels={"country": "Country"},
                            title="Frequency of Earthquake Events in Different Countries in " + selected_continent,
                            template="simple_white")
    st.plotly_chart(fig_hist)

    # Scatter plot
    st.header('Scatter plot: Depth vs Magnitude')

    # Get a list of unique continents
    continents = df['continent'].unique().tolist()

    # Create a select box for the continents
    selected_continent = st.selectbox('Select a continent', ['All'] + continents)

    # Filter the dataframe based on the selected continent
    if selected_continent != 'All':
        df3 = df[df['continent'] == selected_continent]
    else:
        df3 = df

    fig_scatter = px.scatter(df3, x="magnitude", y="depth", color="continent",
                             labels={
                                 "magnitude": "Magnitude",
                                 "depth": "Depth",
                                 "continent": "Continent"
                             },
                             title="Depth vs Magnitude colored by Continent",
                             template="simple_white")
    fig_scatter.update_traces(marker=dict(size=4, opacity=0.6,
                                          line=dict(width=1,
                                                    color='DarkSlateGrey')),
                              selector=dict(mode='markers'))
    st.plotly_chart(fig_scatter)


if __name__ == "__main__":
    main()

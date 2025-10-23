import streamlit as st
import pandas as pd
import networkx as nx
import pydeck as pdk
import matplotlib.pyplot as plt

st.title("📍 Панель моніторингу логістичних даних")

# 1. Завантаження CSV
uploaded_file = st.file_uploader("Завантажте CSV-файл з маршрутами", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Дані маршруту")
    st.dataframe(df)

    # Очікувана структура CSV:
    # from,to,cost,time,lat_from,lon_from,lat_to,lon_to

    # 2. Побудова графу
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['from'], row['to'], weight=row['cost'], time=row['time'])

    # 3. Вибір початкової та кінцевої точки
    nodes = list(set(df['from']).union(set(df['to'])))
    start = st.selectbox("🚚 Початкова точка", nodes)
    end = st.selectbox("🏁 Кінцева точка", nodes)

    if st.button("🔍 Знайти оптимальний маршрут"):
        try:
            path = nx.dijkstra_path(G, start, end, weight='weight')
            cost = nx.dijkstra_path_length(G, start, end, weight='weight')
            st.success(f"Оптимальний маршрут: {' → '.join(path)} (Витрати: {cost})")
        except nx.NetworkXNoPath:
            st.error("Немає шляху між обраними пунктами.")

    # 4. Візуалізація пунктів доставки на карті
    st.subheader("🗺️ Пункти доставки")
    locations = []
    for _, row in df.iterrows():
        locations.append({'name': row['from'], 'lat': row['lat_from'], 'lon': row['lon_from']})
        locations.append({'name': row['to'], 'lat': row['lat_to'], 'lon': row['lon_to']})
    locations_df = pd.DataFrame(locations).drop_duplicates()

    st.map(locations_df[['lat', 'lon']])

    # Альтернатива з pydeck
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=locations_df['lat'].mean(),
            longitude=locations_df['lon'].mean(),
            zoom=4,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=locations_df,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=5000,
            ),
        ],
    ))

    # 5. Графіки часу та витрат
    st.subheader("📊 Графіки часу та витрат")
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    df.groupby('from')['cost'].sum().plot(kind='bar', ax=ax[0], title='Витрати по точках відправлення')
    df.groupby('from')['time'].sum().plot(kind='bar', ax=ax[1], title='Час по точках відправлення')
    st.pyplot(fig)

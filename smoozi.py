import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Логістична панель", layout="wide")
st.title("📦 Панель моніторингу логістичних даних")

# Завантаження CSV
uploaded_file = st.file_uploader("Завантажте CSV-файл з маршрутами", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Дані маршруту")
    st.dataframe(df)

    # Побудова графу
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['from'], row['to'], weight=row['cost'], time=row['time'])

    # Вибір точок
    nodes = sorted(set(df['from']).union(set(df['to'])))
    col1, col2 = st.columns(2)
    with col1:
        start = st.selectbox("🚚 Початкова точка", nodes)
    with col2:
        end = st.selectbox("🏁 Кінцева точка", nodes)

    if st.button("🔍 Знайти оптимальний маршрут"):
        try:
            path = nx.dijkstra_path(G, start, end, weight='weight')
            cost = nx.dijkstra_path_length(G, start, end, weight='weight')
            st.success(f"Оптимальний маршрут: {' → '.join(path)} (Витрати: {cost})")
        except nx.NetworkXNoPath:
            st.error("Немає шляху між обраними пунктами.")

    # Візуалізація на карті
    st.subheader("🗺️ Пункти доставки")
    locations = []
    for _, row in df.iterrows():
        locations.append({'name': row['from'], 'lat': row['lat_from'], 'lon': row['lon_from']})
        locations.append({'name': row['to'], 'lat': row['lat_to'], 'lon': row['lon_to']})
    locations_df = pd.DataFrame(locations).drop_duplicates()

    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=locations_df['lat'].mean(),
            longitude=locations_df['lon'].mean(),
            zoom=5,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=locations_df,
                get_position='[lon, lat]',
                get_color='[0, 100, 200, 160]',
                get_radius=5000,
            ),
        ],
    ))

    # Графіки витрат і часу
    st.subheader("📊 Графіки витрат і часу")
    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    df.groupby('from')['cost'].sum().plot(kind='bar', ax=ax[0], title='Витрати по точках відправлення', color='skyblue')
    df.groupby('from')['time'].sum().plot(kind='bar', ax=ax[1], title='Час по точках відправлення', color='lightgreen')
    st.pyplot(fig)
else:
    st.info("⬆️ Завантажте CSV-файл для початку роботи.")

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Логістика: автоматичне завантаження", layout="wide")
st.title("🚚 Панель логістичних маршрутів")

# Автоматичне завантаження CSV
try:
    df = pd.read_csv("routes.csv")
    st.subheader("📄 Дані маршрутів")
    st.dataframe(df)

    # Побудова матриці витрат
    points = sorted(set(df['from']).union(set(df['to'])))
    matrix = pd.DataFrame(np.inf, index=points, columns=points)

    for _, row in df.iterrows():
        matrix.loc[row['from'], row['to']] = row['cost']

    st.subheader("📊 Матриця витрат")
    st.dataframe(matrix)

    # Вибір маршруту
    col1, col2 = st.columns(2)
    with col1:
        start = st.selectbox("Початкова точка", points)
    with col2:
        end = st.selectbox("Кінцева точка", points)

    # Простий пошук маршруту (жадібний)
    visited = set()
    current = start
    total_cost = 0
    path = [current]

    while current != end:
        visited.add(current)
        next_hops = matrix.loc[current]
        next_hops = next_hops[~next_hops.index.isin(visited)]
        if next_hops.empty or np.isinf(next_hops.min()):
            st.error("Немає шляху до кінцевої точки.")
            break
        next_node = next_hops.idxmin()
        total_cost += next_hops.min()
        path.append(next_node)
        current = next_node

    if current == end:
        st.success(f"Маршрут: {' → '.join(path)} (Витрати: {total_cost})")

    # Статистика
    st.subheader("📈 Зведена статистика")
    st.metric("Середні витрати", round(df['cost'].mean(), 2))
    st.metric("Середній час", round(df['time'].mean(), 2))

except FileNotFoundError:
    st.error("❌ Файл routes.csv не знайдено. Переконайтесь, що він знаходиться поруч з app.py.")

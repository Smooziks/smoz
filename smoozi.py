import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO

st.set_page_config(page_title="Логістика: автоматичне завантаження", layout="wide")
st.title("🚚 Панель логістичних маршрутів")

# Вбудовані CSV-дані
csv_data = """
from,to,cost,time
Київ,Житомир,1200,2.5
Житомир,Рівне,900,2.0
Рівне,Луцьк,700,1.5
Київ,Черкаси,1100,2.2
Черкаси,Кропивницький,1300,2.8
Кропивницький,Одеса,1600,3.5
"""

# Завантаження CSV з рядка
df = pd.read_csv(StringIO(csv_data.strip()))
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

# Жадібний пошук найкоротшого шляху
visited = set()
current = start
total_cost = 0
path = [current]

while current != end:
    visited.add(current)
    next_hops = matrix.loc[current]
    next_hops = next_hops[~next_hops.index.isin(visited)]
    if next_hops.empty or np.isinf(next_hops.min()):
        st.error("❌ Немає шляху до кінцевої точки.")
        break
    next_node = next_hops.idxmin()
    total_cost += next_hops.min()
    path.append(next_node)
    current = next_node

if current == end:
    st.success(f"✅ Маршрут: {' → '.join(path)} (Витрати: {total_cost})")

# Статистика
st.subheader("📈 Зведена статистика")
st.metric("Середні витрати", round(df['cost'].mean(), 2))
st.metric("Середній час", round(df['time'].mean(), 2))

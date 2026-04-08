import streamlit as st
import pandas as pd

st.set_page_config(page_title="7AM BETS AI", layout="wide")

st.title("🔥 7AM BETS AI")
st.subheader("Props Inteligentes NBA")

data = [
    {"Jugador": "Luka Doncic", "Prop": "PTS", "Linea": 28.5, "Prob": 65, "Cuota": 1.85},
    {"Jugador": "Nikola Jokic", "Prop": "AST", "Linea": 8.5, "Prob": 68, "Cuota": 1.80},
    {"Jugador": "Stephen Curry", "Prop": "3PT", "Linea": 4.5, "Prob": 62, "Cuota": 1.90},
    {"Jugador": "LeBron James", "Prop": "PTS", "Linea": 25.5, "Prob": 61, "Cuota": 1.85},
]

df = pd.DataFrame(data)

df["Value"] = df["Prob"]/100 - (1/df["Cuota"])

st.sidebar.header("Filtros")
min_prob = st.sidebar.slider("Probabilidad mínima", 50, 80, 60)
only_value = st.sidebar.checkbox("Solo Value Bets", True)

filtered_df = df[df["Prob"] >= min_prob]

if only_value:
    filtered_df = filtered_df[filtered_df["Value"] > 0]

st.markdown("## 📊 Mejores Picks del Día")

for i, row in filtered_df.iterrows():
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.write(f"**{row['Jugador']}**")
    col2.write(row["Prop"])
    col3.write(row["Linea"])
    col4.write(f"{row['Prob']}%")
    col5.write(row["Cuota"])

    if row["Value"] > 0:
        col6.success("VALUE")
    else:
        col6.error("NO")

    st.button(f"Apostar Over {row['Linea']}", key=i)
    st.divider()
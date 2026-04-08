import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

st.set_page_config(page_title="7AM BETS AI", layout="wide")

st.title("🔥 7AM BETS AI")
st.subheader("Props Inteligentes NBA")

# ------------------------
# FUNCION DATOS REALES
# ------------------------
@st.cache_data
def get_player_games(player_name):
    player = players.find_players_by_full_name(player_name)[0]
    player_id = player['id']
    
    df = playergamelog.PlayerGameLog(player_id=player_id).get_data_frames()[0]
    df = df.sort_values("GAME_DATE", ascending=False).head(10)
    
    return df

# ------------------------
# DATA BASE
# ------------------------
data = [
    {"Jugador": "Nikola Jokic", "Prop": "AST", "Linea": 8.5},
    {"Jugador": "Luka Doncic", "Prop": "PTS", "Linea": 28.5},
    {"Jugador": "Stephen Curry", "Prop": "FG3M", "Linea": 4.5},
]

df = pd.DataFrame(data)

# ------------------------
# UI
# ------------------------
st.markdown("## 📊 Mejores Picks del Día")

for i, row in df.iterrows():
    
    jugador = row["Jugador"]
    linea = row["Linea"]
    stat = row["Prop"]
    
    st.markdown(f"### {jugador} - {stat} ({linea})")
    
    try:
        games = get_player_games(jugador)
        
        valores = games[stat].values
        
        # HIT RATE
        hits = np.sum(valores > linea)
        total = len(valores)
        porcentaje = round((hits/total)*100, 1)
        
        st.write(f"🔥 Hit Rate últimos 10: {hits}/{total} ({porcentaje}%)")
        
        # ------------------------
        # GRAFICO PRO
        # ------------------------
        fig, ax = plt.subplots(figsize=(6,3))

        colores = ["#00ff88" if v > linea else "#ff4d4d" for v in valores]

        ax.bar(range(len(valores)), valores, color=colores, edgecolor='white', linewidth=1)

        # Línea de la apuesta
        ax.axhline(linea, linestyle='--', linewidth=2)

        # Estilo limpio
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Fondo oscuro
        ax.set_facecolor('#0e1117')
        fig.patch.set_facecolor('#0e1117')

        # Texto blanco
        ax.tick_params(colors='white')
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.title.set_color('white')

        ax.set_title("Últimos 10 partidos", fontsize=10)
        ax.set_ylabel(stat, fontsize=9)

        st.pyplot(fig)
        
    except:
        st.error("Error cargando datos")
    
    st.divider()

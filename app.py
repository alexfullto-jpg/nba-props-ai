import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from nba_api.stats.endpoints import scoreboardv2, commonteamroster, playergamelog

st.set_page_config(page_title="7AM BETS AI", layout="wide")

st.title("🔥 7AM BETS AI")
st.subheader("Selector inteligente NBA")

# ------------------------
# OBTENER PARTIDOS HOY
# ------------------------
@st.cache_data
def get_games_today():
    games = scoreboardv2.ScoreboardV2()
    df = games.get_data_frames()[0]
    return df[['GAME_ID','HOME_TEAM_ID','VISITOR_TEAM_ID','GAME_STATUS_TEXT']]

games = get_games_today()

# ------------------------
# MAPA EQUIPOS
# ------------------------
team_dict = {
    1610612747: "Lakers",
    1610612744: "Warriors",
    1610612743: "Nuggets",
    1610612742: "Mavericks",
    1610612738: "Celtics"
}

# ------------------------
# SELECT PARTIDO
# ------------------------
st.markdown("## 📅 Partidos de Hoy")

games_list = []

for _, g in games.iterrows():
    home = team_dict.get(g['HOME_TEAM_ID'], str(g['HOME_TEAM_ID']))
    away = team_dict.get(g['VISITOR_TEAM_ID'], str(g['VISITOR_TEAM_ID']))
    
    games_list.append(f"{away} vs {home}")

selected_game = st.selectbox("Selecciona partido", games_list)

# ------------------------
# SELECCION EQUIPO
# ------------------------
selected_team = st.selectbox("Selecciona equipo", ["Local", "Visitante"])

# Obtener team_id
game_index = games_list.index(selected_game)
game_data = games.iloc[game_index]

team_id = game_data['HOME_TEAM_ID'] if selected_team == "Local" else game_data['VISITOR_TEAM_ID']

# ------------------------
# ROSTER
# ------------------------
@st.cache_data
def get_roster(team_id):
    roster = commonteamroster.CommonTeamRoster(team_id=team_id)
    return roster.get_data_frames()[0]

roster = get_roster(team_id)

player_name = st.selectbox("Selecciona jugador", roster['PLAYER'].values)

# ------------------------
# STAT
# ------------------------
stat_map = {
    "Puntos": "PTS",
    "Asistencias": "AST",
    "Rebotes": "REB",
    "Triples": "FG3M"
}

stat_label = st.selectbox("Selecciona stat", list(stat_map.keys()))
stat = stat_map[stat_label]

# ------------------------
# LINEA
# ------------------------
linea = st.number_input("Ingresa línea", value=10.0)

# ------------------------
# ANALIZAR
# ------------------------
if st.button("Analizar"):

    try:
        from nba_api.stats.static import players
        
        player_id = None
        for p in players.get_players():
            if p['full_name'] == player_name:
                player_id = p['id']
        
        df = playergamelog.PlayerGameLog(player_id=player_id).get_data_frames()[0]
        df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
        df = df.sort_values("GAME_DATE", ascending=False).head(10)

        valores = df[stat].values
        fechas = df['GAME_DATE'].dt.strftime('%m-%d').values

        hits = np.sum(valores > linea)
        prob = hits / len(valores)

        st.write(f"🔥 Probabilidad: {round(prob*100,1)}%")

        # GRAFICO
        fig, ax = plt.subplots(figsize=(4,2))

        colores = ["#00ff88" if v > linea else "#ff4d4d" for v in valores]

        bars = ax.bar(range(len(valores)), valores, color=colores)

        ax.axhline(linea, linestyle='--')

        ax.set_xticks(range(len(fechas)))
        ax.set_xticklabels(fechas, fontsize=6)

        ax.set_facecolor('#0e1117')
        fig.patch.set_facecolor('#0e1117')

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.tick_params(colors='white', labelsize=6)

        st.pyplot(fig, use_container_width=False)

    except:
        st.error("Error analizando jugador")

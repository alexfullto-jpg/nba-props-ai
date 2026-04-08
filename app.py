import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

st.set_page_config(page_title="7AM BETS AI", layout="wide")

st.title("🔥 7AM BETS AI")
st.subheader("Props con Líneas Reales")

# ------------------------
# FUNCION DATOS
# ------------------------
@st.cache_data
def get_player_games(player_name):
    player = players.find_players_by_full_name(player_name)[0]
    player_id = player['id']
    
    df = playergamelog.PlayerGameLog(player_id=player_id).get_data_frames()[0]
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    
    df = df.sort_values("GAME_DATE", ascending=False).head(10)
    
    return df

# ------------------------
# INPUT MANUAL (AQUI PEGAS)
# ------------------------
st.markdown("## ✍️ Pega tus líneas aquí")

input_text = st.text_area("""
Formato:
Jugador,Stat,Linea,Cuota

Ejemplo:
Nikola Jokic,AST,9.5,1.80
Luka Doncic,PTS,30.5,1.90
Stephen Curry,FG3M,4.5,1.85
""")

# ------------------------
# PROCESAR INPUT
# ------------------------
if input_text:

    filas = input_text.strip().split("\n")
    data = []

    for f in filas:
        try:
            j, stat, linea, cuota = f.split(",")
            data.append({
                "Jugador": j.strip(),
                "Stat": stat.strip(),
                "Linea": float(linea),
                "Cuota": float(cuota)
            })
        except:
            continue

    df = pd.DataFrame(data)

    st.markdown("## 📊 Resultados")

    for i, row in df.iterrows():
        
        jugador = row["Jugador"]
        linea = row["Linea"]
        stat = row["Stat"]
        cuota = row["Cuota"]

        st.markdown(f"### {jugador} - {stat} ({linea})")

        try:
            games = get_player_games(jugador)

            valores = games[stat].values
            fechas = games['GAME_DATE'].dt.strftime('%m-%d').values

            # HIT RATE
            hits = np.sum(valores > linea)
            total = len(valores)
            prob = hits / total

            # VALUE
            implied = 1 / cuota
            value = prob - implied

            st.write(f"🔥 Probabilidad IA: {round(prob*100,1)}%")
            st.write(f"💰 Value: {round(value,3)}")

            # ------------------------
            # GRAFICO
            # ------------------------
            fig, ax = plt.subplots(figsize=(4,2))

            colores = ["#00ff88" if v > linea else "#ff4d4d" for v in valores]

            bars = ax.bar(range(len(valores)), valores, color=colores, width=0.6)

            ax.axhline(linea, linestyle='--', linewidth=1.5)

            # NUMEROS
            for bar, val in zip(bars, valores):
                ax.text(bar.get_x() + bar.get_width()/2, val - 0.5,
                        str(int(val)),
                        ha='center', va='top',
                        fontsize=6, color='black')

            ax.set_xticks(range(len(fechas)))
            ax.set_xticklabels(fechas, fontsize=6, color='white')

            for spine in ax.spines.values():
                spine.set_visible(False)

            ax.set_facecolor('#0e1117')
            fig.patch.set_facecolor('#0e1117')

            ax.tick_params(colors='white', labelsize=6)
            ax.set_title("Últimos 10", fontsize=7, color='white')
            ax.set_ylabel(stat, fontsize=6, color='white')

            st.pyplot(fig, use_container_width=False)

            # SEMAFORO
            if value > 0.05:
                st.success("🟢 APUESTA (VALUE)")
            elif value > 0:
                st.warning("🟡 MARGINAL")
            else:
                st.error("🔴 EVITAR")

        except:
            st.error("Error con jugador")

        st.divider()

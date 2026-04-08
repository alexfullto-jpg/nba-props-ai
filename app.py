import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

st.set_page_config(page_title="7AM BETS AI", layout="wide")

st.title("🔥 7AM BETS AI")
st.subheader("Props fáciles (escribe como quieras)")

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
# TRADUCIR STAT
# ------------------------
def traducir_stat(texto):
    texto = texto.lower()
    
    if "pts" in texto or "puntos" in texto:
        return "PTS"
    if "ast" in texto or "asist" in texto:
        return "AST"
    if "reb" in texto:
        return "REB"
    if "triples" in texto or "3pt" in texto:
        return "FG3M"
    
    return None

# ------------------------
# BUSCAR JUGADOR
# ------------------------
def buscar_jugador(nombre):
    lista = players.get_players()
    
    for p in lista:
        if nombre.lower() in p['full_name'].lower():
            return p['full_name']
    
    return None

# ------------------------
# INPUT LIBRE
# ------------------------
st.markdown("## ✍️ Escribe así (sin comas)")
st.write("Ej: jokic ast 9.5 1.80")

input_text = st.text_area("")

# ------------------------
# PROCESAR
# ------------------------
if input_text:
    
    lineas = input_text.strip().split("\n")
    
    st.markdown("## 📊 Resultados")
    
    for linea_texto in lineas:
        try:
            partes = linea_texto.split()
            
            nombre = partes[0]
            stat_texto = partes[1]
            linea = float(partes[2])
            
            cuota = float(partes[3]) if len(partes) > 3 else 1.85
            
            jugador_real = buscar_jugador(nombre)
            stat = traducir_stat(stat_texto)
            
            if jugador_real is None or stat is None:
                st.error(f"No se reconoce: {linea_texto}")
                continue
            
            st.markdown(f"### {jugador_real} - {stat} ({linea})")
            
            games = get_player_games(jugador_real)
            
            valores = games[stat].values
            fechas = games['GAME_DATE'].dt.strftime('%m-%d').values
            
            # HIT RATE
            hits = np.sum(valores > linea)
            total = len(valores)
            prob = hits / total
            
            # VALUE
            implied = 1 / cuota
            value = prob - implied
            
            st.write(f"🔥 Probabilidad: {round(prob*100,1)}%")
            st.write(f"💰 Value: {round(value,3)}")
            
            # ------------------------
            # GRAFICO
            # ------------------------
            fig, ax = plt.subplots(figsize=(4,2))

            colores = ["#00ff88" if v > linea else "#ff4d4d" for v in valores]

            bars = ax.bar(range(len(valores)), valores, color=colores, width=0.6)

            ax.axhline(linea, linestyle='--', linewidth=1.5)

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
                st.success("🟢 APUESTA")
            elif value > 0:
                st.warning("🟡 MARGINAL")
            else:
                st.error("🔴 EVITAR")

        except:
            st.error(f"Error en: {linea_texto}")
        
        st.divider()

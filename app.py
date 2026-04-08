import streamlit as st
import pandas as pd
import numpy as np
import re
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

st.set_page_config(page_title="7AM BETS AI", layout="wide")

st.title("🔥 7AM BETS AI")
st.subheader("Extractor automático (copia TODA la página)")

# ------------------------
# FUNCIONES
# ------------------------
@st.cache_data
def get_player_games(player_name):
    player = players.find_players_by_full_name(player_name)[0]
    player_id = player['id']
    
    df = playergamelog.PlayerGameLog(player_id=player_id).get_data_frames()[0]
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    
    df = df.sort_values("GAME_DATE", ascending=False).head(10)
    
    return df

def detectar_stat(texto):
    texto = texto.lower()
    
    if "ast" in texto:
        return "AST"
    if "reb" in texto:
        return "REB"
    if "pts" in texto or "puntos" in texto:
        return "PTS"
    if "3" in texto or "triple" in texto:
        return "FG3M"
    
    return None

def buscar_jugador(texto):
    lista = players.get_players()
    
    for p in lista:
        if p['full_name'].lower() in texto.lower():
            return p['full_name']
    
    return None

# ------------------------
# INPUT
# ------------------------
st.markdown("## ✍️ Pega TODA la página aquí")

input_text = st.text_area("", height=300)

# ------------------------
# ANALISIS
# ------------------------
if input_text:
    
    resultados = []
    
    lineas = input_text.split("\n")
    
    for linea in lineas:
        try:
            jugador = buscar_jugador(linea)
            stat = detectar_stat(linea)
            
            numeros = re.findall(r"\d+\.\d+", linea)
            
            if jugador and stat and len(numeros) >= 2:
                
                linea_apuesta = float(numeros[0])
                cuota = float(numeros[1])
                
                df = get_player_games(jugador)
                valores = df[stat].values
                
                hits = np.sum(valores > linea_apuesta)
                prob = hits / len(valores)
                
                implied = 1 / cuota
                value = prob - implied
                
                resultados.append({
                    "Jugador": jugador,
                    "Stat": stat,
                    "Linea": linea_apuesta,
                    "Prob %": round(prob*100,1),
                    "Cuota": cuota,
                    "Value": round(value,3)
                })
                
        except:
            continue
    
    if resultados:
        df_final = pd.DataFrame(resultados)
        df_final = df_final.sort_values(by="Value", ascending=False)
        
        st.markdown("## 🏆 Mejores Picks")
        st.dataframe(df_final, use_container_width=True)
        
        st.markdown("## 🔥 TOP 5")
        
        for _, row in df_final.head(5).iterrows():
            st.success(
                f"{row['Jugador']} | {row['Stat']} {row['Linea']} | Prob: {row['Prob %']}% | Value: {row['Value']}"
            )
    else:
        st.error("No se detectaron props automáticamente")

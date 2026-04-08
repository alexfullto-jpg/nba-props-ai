import streamlit as st
import pandas as pd
import numpy as np
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

st.set_page_config(page_title="7AM BETS AI", layout="wide")

st.title("🔥 7AM BETS AI")
st.subheader("Scanner de Props (encuentra el mejor pick automático)")

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

def traducir_stat(texto):
    texto = texto.lower()
    
    if "pts" in texto:
        return "PTS"
    if "ast" in texto:
        return "AST"
    if "reb" in texto:
        return "REB"
    if "triples" in texto or "3pt" in texto:
        return "FG3M"
    
    return None

def buscar_jugador(nombre):
    lista = players.get_players()
    
    for p in lista:
        if nombre.lower() in p['full_name'].lower():
            return p['full_name']
    
    return None

# ------------------------
# INPUT MASIVO
# ------------------------
st.markdown("## ✍️ Pega TODOS los props")

input_text = st.text_area("""
Ejemplo:
garland pts 6.5 1.67
kawhi triples 3.5 1.97
dunn ast 3.5 1.67
marshall pts 3.5 2.00
""")

# ------------------------
# ANALISIS
# ------------------------
if input_text:
    
    resultados = []
    
    lineas = input_text.strip().split("\n")
    
    for linea_texto in lineas:
        try:
            partes = linea_texto.split()
            
            nombre = partes[0]
            stat_texto = partes[1]
            linea = float(partes[2])
            cuota = float(partes[3])
            
            jugador = buscar_jugador(nombre)
            stat = traducir_stat(stat_texto)
            
            if jugador is None or stat is None:
                continue
            
            df = get_player_games(jugador)
            valores = df[stat].values
            
            hits = np.sum(valores > linea)
            prob = hits / len(valores)
            
            implied = 1 / cuota
            value = prob - implied
            
            resultados.append({
                "Jugador": jugador,
                "Stat": stat,
                "Linea": linea,
                "Prob": round(prob*100,1),
                "Cuota": cuota,
                "Value": round(value,3)
            })
            
        except:
            continue
    
    if len(resultados) > 0:
        
        df_final = pd.DataFrame(resultados)
        
        # 🔥 ORDENAR POR MEJOR VALUE
        df_final = df_final.sort_values(by="Value", ascending=False)
        
        st.markdown("## 🏆 Mejores Picks")
        st.dataframe(df_final, use_container_width=True)
        
        # TOP 3
        st.markdown("## 🔥 TOP 3 DEL DÍA")
        
        top = df_final.head(3)
        
        for _, row in top.iterrows():
            st.success(
                f"{row['Jugador']} | {row['Stat']} {row['Linea']} | Prob: {row['Prob']}% | Value: {row['Value']}"
            )
    
    else:
        st.error("No se pudieron analizar los datos")

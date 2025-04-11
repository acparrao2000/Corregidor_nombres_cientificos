import pandas as pd
import requests
import streamlit as st
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Corregidor de Nombres Científicos", layout="centered")

st.title("🔬 Corregidor de Nombres Científicos con GBIF")
st.markdown("Sube un archivo Excel, selecciona la columna con los nombres científicos y descarga el archivo corregido.")

def corregir_nombres_gbif(lista_nombres):
    url_base = "https://api.gbif.org/v1/species/match"
    nombres_corregidos = []

    for nombre in lista_nombres:
        params = {"name": nombre}
        respuesta = requests.get(url_base, params=params)

        if respuesta.status_code == 200:
            datos = respuesta.json()
            if datos.get("matchType") != "NONE":
                nombres_corregidos.append({
                    "nombre_corregido": datos.get("scientificName"),
                    "genero": datos.get("genus"),
                    "familia": datos.get("family"),
                    "estatus": datos.get("status")
                })
            else:
                nombres_corregidos.append({
                    "nombre_corregido": None,
                    "genero": None,
                    "familia": None,
                    "estatus": "No encontrado"
                })
        else:
            nombres_corregidos.append({
                "nombre_corregido": None,
                "genero": None,
                "familia": None,
                "estatus": f"Error {respuesta.status_code}"
            })

    return nombres_corregidos

# Subir archivo
archivo_excel = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if archivo_excel is not None:
    try:
        df = pd.read_excel(archivo_excel)
        columnas = df.columns.tolist()
        columna_seleccionada = st.selectbox("📌 Selecciona la columna con los nombres científicos:", columnas)

        if st.button("🔍 Corregir nombres"):
            st.info("Procesando, esto puede tardar unos segundos...")

            resultados = corregir_nombres_gbif(df[columna_seleccionada].tolist())
            df_resultados = pd.DataFrame(resultados)
            df_final = pd.concat([df.reset_index(drop=True), df_resultados], axis=1)

            st.success("✅ Corrección completada")
            st.dataframe(df_final)

            # Guardar a un archivo en memoria
            buffer = BytesIO()
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"nombres_corregidos_{fecha}.xlsx"
            df_final.to_excel(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                label="📥 Descargar archivo corregido",
                data=buffer,
                file_name=nombre_archivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

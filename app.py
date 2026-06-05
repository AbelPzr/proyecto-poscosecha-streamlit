import streamlit as st
import pandas as pd
import io
import zipfile
import matplotlib.pyplot as plt

import analisis


from analisis import (
    anova_test,
    calcular_estadisticas,
    tukey_hsd_test
)

from graficos import (
    mostrar_barplot,
    mostrar_boxplot,
    generar_barplot_png,
    generar_boxplot_png
)

# =====================================================
# CONFIGURACIÓN
# =====================================================
st.cache_data.clear()

st.markdown("""
    <style>
        text { fill: black !important; color: black !important; }
        .gtitle { fill: black !important; }
        .xtitle { fill: black !important; }
        .ytitle { fill: black !important; }
        .xtick text { fill: black !important; }
        .ytick text { fill: black !important; }
    </style>
""", unsafe_allow_html=True)


st.set_page_config(
    page_title="Análisis de Poscosecha",
    page_icon="🍌",
    layout="wide"
)

st.title("🍌 Análisis de Poscosecha")
st.markdown(
    "Suba un archivo Excel para generar ANOVA, Tukey HSD y gráficos."
)

# =====================================================
# CARGA DE ARCHIVO
# =====================================================

uploaded_file = st.file_uploader(
    "📂 Subir archivo Excel",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Suba un archivo para comenzar.")
    st.stop()

# =====================================================
# LECTURA EXCEL
# =====================================================

try:

    df = pd.read_excel(
        uploaded_file,
        sheet_name=0
    )

except Exception as e:

    st.error(f"Error leyendo archivo: {e}")
    st.stop()

# =====================================================
# VALIDACIONES
# =====================================================

COLUMNAS_REQUERIDAS = ["Trat", "Tratamiento", "Replica", "Crown Mold DI", "Crown Rot DI"]
COLUMNAS_NUMERICAS = ["Trat", "Replica", "Crown Mold DI", "Crown Rot DI"]

columnas_faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]

if columnas_faltantes:
    st.error(
        f"El archivo no contiene las siguientes columnas requeridas: "
        f"{', '.join(columnas_faltantes)}"
    )
    st.stop()

errores_tipo = []

for col in COLUMNAS_NUMERICAS:
    if not pd.api.types.is_numeric_dtype(df[col]):
        no_numericos = df[col].dropna()
        no_numericos = no_numericos[pd.to_numeric(no_numericos, errors='coerce').isna()]
        if len(no_numericos) > 0:
            errores_tipo.append(
                f"'{col}' debe ser numérica (valores inválidos: {no_numericos.unique()[:3].tolist()})"
            )
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce')

if errores_tipo:
    for msg in errores_tipo:
        st.error(msg)
    st.stop()

# =====================================================
# VARIABLES A ANALIZAR
# =====================================================

variables = [

    c

    for c in df.columns

    if c != "Tratamiento" and c != "Replica" and c != "Trat"
]

if len(variables) == 0:

    st.error(
        "No se encontraron variables para analizar."
    )

    st.stop()

# =====================================================
# PROCESAMIENTO
# =====================================================

resultados = {}

with st.spinner("Procesando análisis..."):

    for variable in variables:

        try:

            resultados[variable] = {

                "anova": analisis.anova_test(
                    df,
                    "Tratamiento",
                    variable
                ),

                "tukey": analisis.tukey_hsd_test(
                    df,
                    "Tratamiento",
                    variable
                ),

                "stats": analisis.calcular_estadisticas(
                    df,
                    "Tratamiento",
                    variable
                )
            }

        except Exception as e:

            st.error(
                f"Error procesando {variable}: {e}"
            )

# =====================================================
# VARIABLES A ANALIZAR
# =====================================================

VARIABLES_ANALISIS = [
    "Crown Rot DI",
    "Crown Mold DI"
]

variables = []

for col in VARIABLES_ANALISIS:

    if col in df.columns:
        variables.append(col)

if len(variables) == 0:

    st.error(
        "No se encontraron las columnas "
        "'Crown Rot DI' y/o 'Crown Mold DI' en el archivo."
    )

    st.stop()

# =====================================================
# TABS DINÁMICOS
# =====================================================

tab_names = []

for variable in variables:

    if variable == "Crown Rot DI":
        tab_names.append("👑 Crown Rot DI")

    elif variable == "Crown Mold DI":
        tab_names.append("🍄 Crown Mold DI")

    else:
        tab_names.append(variable)

tabs = st.tabs(tab_names)

for tab, variable in zip(tabs, variables):

    with tab:

        resultado = resultados[variable]

        st.header(variable)

        # =============================================
        # ESTADÍSTICAS DESCRIPTIVAS
        # =============================================

        st.markdown(
            "### 📋 Estadísticas Descriptivas"
        )

        st.dataframe(
            resultado["stats"],
            use_container_width=True
        )

        st.divider()

        # =============================================
        # ANOVA
        # =============================================

        st.markdown(
            "### 📊 ANOVA"
        )

        anova = resultado["anova"]

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "F Statistic",
                f"{anova['f_statistic']:.4f}"
            )

        with c2:

            st.metric(
                "P Value",
                f"{anova['p_value']:.6f}"
            )

        with c3:

            st.metric(
                "Significativo",
                "✅ Sí"
                if anova["significativo"]
                else "❌ No"
            )

        st.divider()

        # =============================================
        # TUKEY
        # =============================================

        st.markdown(
            "### Tukey HSD"
        )

        st.dataframe(
            resultado["tukey"]["resultado"],
            use_container_width=True
        )

        # =============================================
        # DEBUG TUKEY (desactivado)
        # =============================================

        # with st.expander("🔍 Debug Tukey"):
        #     from statsmodels.stats.multicomp import pairwise_tukeyhsd
        #
        #     data_debug = df[
        #         ["Tratamiento", variable]
        #     ].dropna()
        #
        #     # ============================
        #     # MEDIAS
        #     # ============================
        #
        #     means = (
        #         data_debug
        #         .groupby("Tratamiento")[variable]
        #         .mean()
        #         .sort_values(ascending=False)
        #     )
        #
        #     st.write("### Medias")
        #
        #     st.dataframe(
        #         means.reset_index(),
        #         use_container_width=True
        #     )
        #
        #     # ============================
        #     # TUKEY RAW
        #     # ============================
        #
        #     tukey = pairwise_tukeyhsd(
        #         endog=data_debug[variable],
        #         groups=data_debug["Tratamiento"],
        #         alpha=0.05
        #     )
        #
        #     tukey_df = pd.DataFrame(
        #         tukey._results_table.data[1:],
        #         columns=tukey._results_table.data[0]
        #     )
        #
        #     st.write("### Tukey Raw")
        #
        #     st.dataframe(
        #         tukey_df,
        #         use_container_width=True
        #     )
        #
        #     # ============================
        #     # REJECT MATRIX
        #     # ============================
        #
        #     ordered_groups = means.index.tolist()
        #
        #     reject_matrix = pd.DataFrame(
        #         False,
        #         index=ordered_groups,
        #         columns=ordered_groups
        #     )
        #
        #     for _, row in tukey_df.iterrows():
        #         g1 = row["group1"]
        #         g2 = row["group2"]
        #
        #         reject_matrix.loc[g1, g2] = row["reject"]
        #         reject_matrix.loc[g2, g1] = row["reject"]
        #
        #     st.write("### Reject Matrix")
        #
        #     st.dataframe(
        #         reject_matrix,
        #         use_container_width=True
        #     )

            
        # =============================================
        # BARPLOT
        # =============================================

        st.markdown(
            "### 📈 Medias por Tratamiento"
        )

        mostrar_barplot(
            resultado["tukey"]["resultado"],
            variable
        )

        st.divider()

        # =============================================
        # BOXPLOT
        # =============================================

        st.markdown(
            "### 📦 Distribución por Tratamiento"
        )

        mostrar_boxplot(
            df,
            variable
        )

# =====================================================
# GENERACIÓN ZIP
# =====================================================

st.markdown("---")
st.subheader("📦 Descargar análisis completo")

try:

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zf:

        excel_buffer = io.BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
        ) as writer:

            for variable in variables:

                resultado = resultados[variable]

                # ANOVA

                anova_df = pd.DataFrame(
                    [resultado["anova"]]
                )

                anova_df.to_excel(
                    writer,
                    sheet_name=f"{variable[:20]} ANOVA",
                    index=False
                )

                # TUKEY

                resultado["tukey"]["resultado"].to_excel(
                    writer,
                    sheet_name=f"{variable[:20]} Tukey",
                    index=False
                )

                # DESCRIPTIVAS

                resultado["stats"].to_excel(
                    writer,
                    sheet_name=f"{variable[:20]} Desc",
                    index=False
                )

        excel_buffer.seek(0)

        zf.writestr(
            "Resumen_Analisis.xlsx",
            excel_buffer.getvalue()
        )

        # PNG

        for variable in variables:

            nombre_archivo = (
                variable
                .replace(" ", "_")
                .replace("/", "_")
            )

            # Barplot

            fig_bar = generar_barplot_png(
                resultados[variable]["tukey"]["resultado"],
                variable
            )

            buf_bar = io.BytesIO()
            fig_bar.write_image(buf_bar, format="png", scale=2)
            buf_bar.seek(0)
            zf.writestr(f"{nombre_archivo}_barplot.png", buf_bar.getvalue())

            # Boxplot

            fig_box = generar_boxplot_png(df, variable)

            buf_box = io.BytesIO()
            fig_box.savefig(buf_box, format="png", dpi=300, bbox_inches="tight")
            buf_box.seek(0)
            zf.writestr(f"{nombre_archivo}_boxplot.png", buf_box.getvalue())
            plt.close(fig_box)

    zip_buffer.seek(0)

    st.download_button(
        label="⬇ Descargar ZIP",
        data=zip_buffer,
        file_name="Analisis_Poscosecha.zip",
        mime="application/zip"
    )

except Exception as e:

    st.error(
        f"Error generando ZIP: {e}"
    )
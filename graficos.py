import io
import textwrap
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import streamlit as st


def wrap_labels(labels, width=10, sep="<br>"):
    return [sep.join(textwrap.wrap(str(label), width=width)) for label in labels]



def mostrar_barplot(tukey_df, variable):

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=wrap_labels(tukey_df["Tratamiento"]),
            y=tukey_df["Media"],
            text=[f"<b>{g}</b>" for g in tukey_df["Grupos"]],
            textposition="outside",
            textfont=dict(size=10, color="black") 
        )
    )

    fig.update_layout(
    template="none",  
    font=dict(color="black", family="Arial"),
    title={
        "text": f"Medias de {variable}",
        "font": {"size": 20, "color": "black"}
    },
    xaxis={
        "title": {
            "text": "Tratamiento",
            "font": {"size": 18, "color": "black"}
        },
        "tickfont": {"size": 10, "color": "black"},
        "linecolor": "black",
        "tickcolor": "black",
        "tickangle": 0
    },
    yaxis={
        "title": {
            "text": "Media",
            "font": {"size": 18, "color": "black"}
        },
        "tickfont": {"size": 10, "color": "black"},
        "linecolor": "black",
        "tickcolor": "black"
    },
    height=500,
    width=1100,
    paper_bgcolor="white",
    plot_bgcolor="white"
)
    st.plotly_chart(
        fig,
        use_container_width=True
    )


def mostrar_boxplot(df, variable):

    tratamientos = df["Tratamiento"].unique()
    data_by_treatment = [
        df[df["Tratamiento"] == t][variable].values
        for t in tratamientos
    ]
    labels_wrapped = wrap_labels(tratamientos, sep="\n")

    fig, ax = plt.subplots(figsize=(25, 10))

    bp = ax.boxplot(
        data_by_treatment,
        tick_labels=labels_wrapped,
        patch_artist=True,
        widths=0.6,
        meanline=True,
        showmeans=True
    )

    colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
               '#9467bd', '#8c564b', '#7f7f7f', '#bcbd22',
               '#17becf', '#0d4a8a', '#e67e22', '#1a7a4a',
               '#8b0000', '#4a0080', '#006666']

    for i, patch in enumerate(bp['boxes']):
        patch.set_facecolor(colores[i % len(colores)])
        patch.set_alpha(0.5)

    ax.set_title(f"Distribución de {variable}", fontsize=20, fontweight='bold', pad=15, color='black')
    ax.set_xlabel("Tratamiento", fontsize=18, fontweight='bold', color='black')
    ax.set_ylabel(variable, fontsize=18, fontweight='bold', color='black')
    ax.tick_params(axis='x', labelsize=15, colors='black')
    ax.tick_params(axis='y', labelsize=15, colors='black')
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color('black')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    st.image(buf, use_container_width=True)


def generar_boxplot_png(df, variable):

    tratamientos = df["Tratamiento"].unique()
    data_by_treatment = [
        df[df["Tratamiento"] == t][variable].values
        for t in tratamientos
    ]
    labels_wrapped = wrap_labels(tratamientos, sep="\n")

    fig, ax = plt.subplots(figsize=(25, 10))

    bp = ax.boxplot(
        data_by_treatment,
        tick_labels=labels_wrapped,
        patch_artist=True,
        widths=0.6,
        meanline=True,
        showmeans=True
    )

    colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
               '#9467bd', '#8c564b', '#7f7f7f', '#bcbd22',
               '#17becf', '#0d4a8a', '#e67e22', '#1a7a4a',
               '#8b0000', '#4a0080', '#006666']

    for i, patch in enumerate(bp['boxes']):
        patch.set_facecolor(colores[i % len(colores)])
        patch.set_alpha(0.5)

    ax.set_title(f"Distribución de {variable}", fontsize=20, fontweight='bold', pad=15, color='black')
    ax.set_xlabel("Tratamiento", fontsize=18, fontweight='bold', color='black')
    ax.set_ylabel(variable, fontsize=18, fontweight='bold', color='black')
    ax.tick_params(axis='x', labelsize=15, colors='black')
    ax.tick_params(axis='y', labelsize=15, colors='black')
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color('black')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()

    return fig


def generar_barplot_png(tukey_df, variable):

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=wrap_labels(tukey_df["Tratamiento"]),
            y=tukey_df["Media"],
            text=[f"<b>{g}</b>" for g in tukey_df["Grupos"]],
            textposition="outside",
            textfont=dict(size=10, color="black")
        )
    )

    fig.update_layout(
        template="none",
        font=dict(color="black", family="Arial"),
        title={
            "text": f"Medias de {variable}",
            "font": {"size": 20, "color": "black"}
        },
        xaxis={
            "title": {
                "text": "Tratamiento",
                "font": {"size": 18, "color": "black"}
            },
            "tickfont": {"size": 10, "color": "black"},
            "linecolor": "black",
            "tickcolor": "black",
            "tickangle": 0
        },
        yaxis={
            "title": {
                "text": "Media",
                "font": {"size": 18, "color": "black"}
            },
            "tickfont": {"size": 10, "color": "black"},
            "linecolor": "black",
            "tickcolor": "black"
        },
        height=500,
        width=1100,
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return fig
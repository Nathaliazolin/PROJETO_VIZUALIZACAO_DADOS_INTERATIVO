import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

# ======================================
# 1. CARREGAR E PREPARAR OS DADOS
# ======================================
df = pd.read_csv("ecommerce_estatistica.csv")

# Remoção de colunas irrelevantes
df.drop(["Review1", "Review2", "Review3"], axis=1, inplace=True)

# Ajuste da coluna de temporada
df["Temporada_Ajuste"] = df["Temporada"].apply(lambda x: "Não/Definido" if x == "não definido" else x)
df["Temporada_Ajuste"] = df["Temporada_Ajuste"].apply(lambda x: "primavera/verão/outono/inverno" if x == "primavera-verão outono-inverno" else x)
df["Temporada_Ajuste"] = df["Temporada_Ajuste"].str.replace(" ", "")
df["Temporada_Ajuste"] = df["Temporada_Ajuste"].str.replace("-", "/")

# ======================================
# 2. CRIAR O APP DASH
# ======================================
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard E-commerce", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Selecione a Temporada:"),
        dcc.Dropdown(
            id="filtro_temporada",
            options=[{"label": t, "value": t} for t in sorted(df["Temporada_Ajuste"].unique())],
            value=df["Temporada_Ajuste"].unique().tolist(),
            multi=True
        )
    ], style={'width': '50%', 'margin': 'auto'}),

    html.Br(),

    dcc.Graph(id="grafico_histograma"),
    dcc.Graph(id="grafico_disp"),
    dcc.Graph(id="grafico_calor"),
    dcc.Graph(id="grafico_barra"),
    dcc.Graph(id="grafico_pizza")
])

# ======================================
# 3. CALLBACKS INTERATIVOS
# ======================================

@app.callback(
    Output("grafico_histograma", "figure"),
    Output("grafico_disp", "figure"),
    Output("grafico_calor", "figure"),
    Output("grafico_barra", "figure"),
    Output("grafico_pizza", "figure"),
    Input("filtro_temporada", "value")
)
def atualizar_graficos(temporadas):
    df_filtrado = df[df["Temporada_Ajuste"].isin(temporadas)]

    # HISTOGRAMA
    fig_hist = px.histogram(df_filtrado, x="Nota", nbins=100, color_discrete_sequence=["green"])
    fig_hist.update_layout(title="Distribuição das Notas", xaxis_title="Nota", yaxis_title="Frequência")

    # DISPERSÃO (hexbin -> scatter 2D interativo)
    fig_disp = px.scatter(df_filtrado, x="Desconto", y="Qtd_Vendidos_Cod", color="Nota",
                          title="Relação entre Desconto e Quantidade Vendida")

    # MAPA DE CALOR
    corr = df_filtrado[["N_Avaliações", "Qtd_Vendidos_Cod"]].corr()
    fig_calor = ff.create_annotated_heatmap(
        z=corr.values,
        x=list(corr.columns),
        y=list(corr.index),
        colorscale="RdBu",
        showscale=True
    )
    fig_calor.update_layout(title="Mapa de Calor da Correlação")

    # GRÁFICO DE BARRAS
    contagem = df_filtrado["Temporada_Ajuste"].value_counts()
    fig_barra = px.bar(
        x=contagem.index,
        y=contagem.values,
        color=contagem.index,
        title="Distribuição de Peças por Temporada",
        labels={"x": "Temporada", "y": "Quantidade"}
    )

    # GRÁFICO DE PIZZA
    fig_pizza = px.pie(
        values=contagem.values,
        names=contagem.index,
        title="Proporção de Roupas por Temporada",
        hole=0.3
    )

    return fig_hist, fig_disp, fig_calor, fig_barra, fig_pizza

# ======================================
# 4. EXECUTAR
# ======================================
if __name__ == "__main__":
    app.run(debug=True)
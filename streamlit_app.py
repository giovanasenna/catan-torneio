"""
Torneio das 4 Estações de Catan - Aplicação Streamlit
======================================================
Este script fornece uma aplicação completa em Python utilizando Streamlit,
Pandas e Plotly para gerenciamento do Torneio das 4 Estações de Catan.

Suporta:
- Salvamento e carregamento via CSV local ('catan_torneio_dados.csv')
- Conexão nativa e colaborativa com Google Sheets via st.connection('gsheets', type=GSheetsConnection)
- Registro completo de partidas (Jogo Base, Navegantes Cenários 1 a 9, Expansão 5-6 jogadores)
- Cálculos estatísticos de justiça: PV Normalizado, VP% Balanceado
- Leaderboard da Estação com critérios oficiais de desempate
- Ranking Anual (10, 6, 3, 1 pontos por estação)
- Gráficos interativos com Plotly

Instalação de Dependências:
    pip install streamlit pandas plotly st-gsheets-connection

Execução Local:
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import os

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Torneio das 4 Estações de Catan",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# CONSTANTES E REGRAS DO TORNEIO
# -----------------------------------------------------------------------------
ESTACOES = ["Inverno", "Primavera", "Verão", "Outono"]
ESTACAO_PADRAO = "Primavera"

JOGADORES_OFICIAIS = {
    "Jhonata": {"cor_nome": "Branco", "cor_hex": "#F8FAFC", "texto": "#000000"},
    "Rodrigo": {"cor_nome": "Azul", "cor_hex": "#2563EB", "texto": "#FFFFFF"},
    "Giovana": {"cor_nome": "Vermelho", "cor_hex": "#DC2626", "texto": "#FFFFFF"},
    "Zhang": {"cor_nome": "Amarelo", "cor_hex": "#EAB308", "texto": "#000000"}
}

CENARIOS_CATAN = {
    "Catan Jogo Base": {"categoria": "Base", "meta_pv": 10},
    "Cenário 1: Rumo a Novas Margens": {"categoria": "Navegantes", "meta_pv": 14},
    "Cenário 2: As Quatro Ilhas": {"categoria": "Navegantes", "meta_pv": 13},
    "Cenário 3: Oceania": {"categoria": "Navegantes", "meta_pv": 12},
    "Cenário 4: Através do Deserto": {"categoria": "Navegantes", "meta_pv": 14},
    "Cenário 5: O Povo Perdido": {"categoria": "Navegantes", "meta_pv": 13},
    "Cenário 6: Mercadorias para Catan": {"categoria": "Navegantes", "meta_pv": 14},
    "Cenário 7: As Ilhas dos Piratas": {"categoria": "Navegantes", "meta_pv": 10},
    "Cenário 8: As Maravilhas de Catan": {"categoria": "Navegantes", "meta_pv": 10},
    "Cenário 9: Um Novo Mundo": {"categoria": "Navegantes", "meta_pv": 12},
    "Personalizado": {"categoria": "Custom", "meta_pv": 10}
}

PONTOS_ANUAIS = {1: 10, 2: 6, 3: 3, 4: 1}
ARQUIVO_CSV_LOCAL = "catan_torneio_dados.csv"

# -----------------------------------------------------------------------------
# CARREGAMENTO E PERSISTÊNCIA DE DADOS
# -----------------------------------------------------------------------------
def get_initial_dataframe():
    """Retorna dados de exemplo pré-carregados se o arquivo for novo."""
    data = [
        {"Partida_ID": "M01", "Data": "2026-07-15", "Estacao": "Inverno", "Cenario": "Catan Jogo Base", "Meta_PV": 10, "Expansao_5_6": False, "Vencedor": "Rodrigo", "Jogador": "Rodrigo", "Oficial": True, "PV": 10, "PV_Normalizado": 1.0, "VP_Percent_Balanceado": 33.33, "Venceu": True, "Notas": "Abertura Inverno"},
        {"Partida_ID": "M01", "Data": "2026-07-15", "Estacao": "Inverno", "Cenario": "Catan Jogo Base", "Meta_PV": 10, "Expansao_5_6": False, "Vencedor": "Rodrigo", "Jogador": "Giovana", "Oficial": True, "PV": 8, "PV_Normalizado": 0.8, "VP_Percent_Balanceado": 26.67, "Venceu": False, "Notas": "Abertura Inverno"},
        {"Partida_ID": "M01", "Data": "2026-07-15", "Estacao": "Inverno", "Cenario": "Catan Jogo Base", "Meta_PV": 10, "Expansao_5_6": False, "Vencedor": "Rodrigo", "Jogador": "Jhonata", "Oficial": True, "PV": 7, "PV_Normalizado": 0.7, "VP_Percent_Balanceado": 23.33, "Venceu": False, "Notas": "Abertura Inverno"},
        {"Partida_ID": "M01", "Data": "2026-07-15", "Estacao": "Inverno", "Cenario": "Catan Jogo Base", "Meta_PV": 10, "Expansao_5_6": False, "Vencedor": "Rodrigo", "Jogador": "Zhang", "Oficial": True, "PV": 5, "PV_Normalizado": 0.5, "VP_Percent_Balanceado": 16.67, "Venceu": False, "Notas": "Abertura Inverno"},
        
        {"Partida_ID": "M02", "Data": "2026-09-20", "Estacao": "Primavera", "Cenario": "Catan Jogo Base", "Meta_PV": 10, "Expansao_5_6": False, "Vencedor": "Zhang", "Jogador": "Zhang", "Oficial": True, "PV": 10, "PV_Normalizado": 1.0, "VP_Percent_Balanceado": 31.25, "Venceu": True, "Notas": "Abertura Primavera"},
        {"Partida_ID": "M02", "Data": "2026-09-20", "Estacao": "Primavera", "Cenario": "Catan Jogo Base", "Meta_PV": 10, "Expansao_5_6": False, "Vencedor": "Zhang", "Jogador": "Giovana", "Oficial": True, "PV": 9, "PV_Normalizado": 0.9, "VP_Percent_Balanceado": 28.13, "Venceu": False, "Notas": "Abertura Primavera"},
        {"Partida_ID": "M02", "Data": "2026-09-20", "Estacao": "Primavera", "Cenario": "Catan Jogo Base", "Meta_PV": 10, "Expansao_5_6": False, "Vencedor": "Zhang", "Jogador": "Rodrigo", "Oficial": True, "PV": 7, "PV_Normalizado": 0.7, "VP_Percent_Balanceado": 21.88, "Venceu": False, "Notas": "Abertura Primavera"},
        {"Partida_ID": "M02", "Data": "2026-09-20", "Estacao": "Primavera", "Cenario": "Catan Jogo Base", "Meta_PV": 10, "Expansao_5_6": False, "Vencedor": "Zhang", "Jogador": "Jhonata", "Oficial": True, "PV": 6, "PV_Normalizado": 0.6, "VP_Percent_Balanceado": 18.75, "Venceu": False, "Notas": "Abertura Primavera"},

        {"Partida_ID": "M03", "Data": "2026-10-10", "Estacao": "Primavera", "Cenario": "Cenário 4: Através do Deserto", "Meta_PV": 14, "Expansao_5_6": False, "Vencedor": "Rodrigo", "Jogador": "Rodrigo", "Oficial": True, "PV": 14, "PV_Normalizado": 1.0, "VP_Percent_Balanceado": 31.82, "Venceu": True, "Notas": "Caravanas do Deserto"},
        {"Partida_ID": "M03", "Data": "2026-10-10", "Estacao": "Primavera", "Cenario": "Cenário 4: Através do Deserto", "Meta_PV": 14, "Expansao_5_6": False, "Vencedor": "Rodrigo", "Jogador": "Jhonata", "Oficial": True, "PV": 12, "PV_Normalizado": 0.857, "VP_Percent_Balanceado": 27.27, "Venceu": False, "Notas": "Caravanas do Deserto"},
        {"Partida_ID": "M03", "Data": "2026-10-10", "Estacao": "Primavera", "Cenario": "Cenário 4: Através do Deserto", "Meta_PV": 14, "Expansao_5_6": False, "Vencedor": "Rodrigo", "Jogador": "Giovana", "Oficial": True, "PV": 10, "PV_Normalizado": 0.714, "VP_Percent_Balanceado": 22.73, "Venceu": False, "Notas": "Caravanas do Deserto"},
        {"Partida_ID": "M03", "Data": "2026-10-10", "Estacao": "Primavera", "Cenario": "Cenário 4: Através do Deserto", "Meta_PV": 14, "Expansao_5_6": False, "Vencedor": "Rodrigo", "Jogador": "Zhang", "Oficial": True, "PV": 8, "PV_Normalizado": 0.571, "VP_Percent_Balanceado": 18.18, "Venceu": False, "Notas": "Caravanas do Deserto"},
    ]
    return pd.DataFrame(data)

def load_data():
    """Carrega os dados via Google Sheets se configurado, ou via CSV local."""
    # Tentativa de conexão via Google Sheets st.connection se configurada no secrets.toml
    if "gsheets" in st.secrets:
        try:
            from streamlit_gsheets import GSheetsConnection
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read(ttl="10m")
            if df is not None and not df.empty:
                return df
        except Exception:
            pass

    if os.path.exists(ARQUIVO_CSV_LOCAL):
        try:
            return pd.read_csv(ARQUIVO_CSV_LOCAL)
        except Exception:
            pass

    df = get_initial_dataframe()
    df.to_csv(ARQUIVO_CSV_LOCAL, index=False)
    return df

def save_data(df):
    """Persiste dados no arquivo local e no Google Sheets (se configurado)."""
    df.to_csv(ARQUIVO_CSV_LOCAL, index=False)
    if "gsheets" in st.secrets:
        try:
            from streamlit_gsheets import GSheetsConnection
            conn = st.connection("gsheets", type=GSheetsConnection)
            conn.update(data=df)
        except Exception:
            pass

# -----------------------------------------------------------------------------
# CÁLCULOS ESTATÍSTICOS E REGRAS DO TORNEIO
# -----------------------------------------------------------------------------
def calculate_leaderboard(df, estacao="Primavera", apenas_oficiais=True):
    """
    Calcula classificação da estação:
    1º Critério: Vitórias (V)
    2º Critério: Soma dos PVs Totais
    3º Critério: Média do VP% Balanceado
    """
    if df.empty:
        return pd.DataFrame()

    sub = df[df["Estacao"] == estacao] if estacao != "Geral" else df
    if apenas_oficiais:
        sub = sub[sub["Oficial"] == True]

    if sub.empty:
        return pd.DataFrame()

    grouped = sub.groupby("Jogador").agg(
        Partidas=("Partida_ID", "nunique"),
        Vitorias=("Venceu", lambda x: int(x.sum())),
        PV_Total=("PV", "sum"),
        PV_Medio=("PV", lambda x: round(x.mean(), 2)),
        Media_VP_Balanceado=("VP_Percent_Balanceado", lambda x: round(x.mean(), 2)),
        Maior_PV=("PV", "max")
    ).reset_index()

    grouped["Taxa_Vitoria_Pct"] = round((grouped["Vitorias"] / grouped["Partidas"]) * 100, 1)

    # Ordenação estrita pelos critérios de justiça estatística
    grouped = grouped.sort_values(
        by=["Vitorias", "PV_Total", "Media_VP_Balanceado"],
        ascending=[False, False, False]
    ).reset_index(drop=True)

    grouped.index = grouped.index + 1
    grouped.index.name = "Posição"
    return grouped

def calculate_annual_circuit(df):
    """Calcula pontuação do Circuito Anual (10, 6, 3, 1 pts por estação)."""
    pontos_anuais = {j: {e: 0 for e in ESTACOES} for j in JOGADORES_OFICIAIS.keys()}

    for est in ESTACOES:
        sub = df[(df["Estacao"] == est) & (df["Oficial"] == True)]
        if sub.empty:
            continue
        lb = calculate_leaderboard(df, estacao=est, apenas_oficiais=True)
        for pos, row in enumerate(lb.itertuples(), start=1):
            pts = PONTOS_ANUAIS.get(pos, 0)
            if row.Jogador in pontos_anuais:
                pontos_anuais[row.Jogador][est] = pts

    rows = []
    for jog, est_pts in pontos_anuais.items():
        total = sum(est_pts.values())
        rows.append({
            "Jogador": jog,
            "Cor": JOGADORES_OFICIAIS[jog]["cor_nome"],
            "Inverno": est_pts["Inverno"],
            "Primavera": est_pts["Primavera"],
            "Verão": est_pts["Verão"],
            "Outono": est_pts["Outono"],
            "Pontos_Anuais": total
        })

    an_df = pd.DataFrame(rows).sort_values(by="Pontos_Anuais", ascending=False).reset_index(drop=True)
    an_df.index = an_df.index + 1
    an_df.index.name = "Posição"
    return an_df

# -----------------------------------------------------------------------------
# INTERFACE PRINCIPAL
# -----------------------------------------------------------------------------
df = load_data()

st.title("🎲 Torneio das 4 Estações de Catan")
st.markdown("Circuito Anual Oficial • Edição **Primavera** • Gestão Estatística e Colaborativa")

# Abas do Aplicativo
tab_leaderboard, tab_registro, tab_anual, tab_graficos, tab_historico = st.tabs([
    "🏆 Classificação",
    "📝 Registrar Partida",
    "🌍 Ranking Anual",
    "📈 Gráficos & Estatísticas",
    "📜 Histórico de Partidas"
])

# -----------------------------------------------------------------------------
# ABA 1: CLASSIFICAÇÃO DA ESTAÇÃO
# -----------------------------------------------------------------------------
with tab_leaderboard:
    col_est, col_filter = st.columns([2, 1])
    with col_est:
        estacao_selecionada = st.selectbox("Selecione a Estação:", ESTACOES + ["Geral"], index=1)
    with col_filter:
        incluir_convidados = st.checkbox("Incluir Visitantes no Placar", value=False)

    lb = calculate_leaderboard(df, estacao=estacao_selecionada, apenas_oficiais=not incluir_convidados)

    if not lb.empty:
        # Pódio Top 3
        top_cols = st.columns(min(len(lb), 3))
        for idx, col in enumerate(top_cols):
            if idx < len(lb):
                player_row = lb.iloc[idx]
                medal = "🥇" if idx == 0 else ("🥈" if idx == 1 else "🥉")
                with col:
                    st.metric(
                        label=f"{medal} {idx+1}º Lugar • {player_row['Jogador']}",
                        value=f"{int(player_row['Vitorias'])} Vitórias",
                        delta=f"{int(player_row['PV_Total'])} PV Totais"
                    )

        st.subheader("Tabela de Classificação Oficial")
        st.dataframe(
            lb.style.format({
                "Taxa_Vitoria_Pct": "{:.1f}%",
                "Media_VP_Balanceado": "{:.2f}%",
                "PV_Medio": "{:.2f}"
            }),
            use_container_width=True
        )
        st.caption("Critérios de Desempate: 1º Vitórias (V) → 2º PV Total Acumulado → 3º Média do VP% Balanceado.")
    else:
        st.info("Nenhuma partida registrada nesta estação ainda.")

# -----------------------------------------------------------------------------
# ABA 2: REGISTRO DE PARTIDA
# -----------------------------------------------------------------------------
with tab_registro:
    st.subheader("Registrar Nova Partida")
    with st.form("form_partida", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            data_partida = st.date_input("Data da Partida", value=date.today())
        with c2:
            estacao_partida = st.selectbox("Estação do Torneio", ESTACOES, index=1)
        with c3:
            cenario_nome = st.selectbox("Modo de Jogo / Cenário", list(CENARIOS_CATAN.keys()), index=0)

        meta_padrao = CENARIOS_CATAN[cenario_nome]["meta_pv"]
        c4, c5 = st.columns(2)
        with c4:
            meta_pv = st.number_input("Meta de PV do Cenário", min_value=8, max_value=25, value=meta_padrao)
        with c5:
            expansao_5_6 = st.checkbox("Mesa com Expansão 5-6 Jogadores", value=False)

        st.markdown("---")
        st.markdown("**Selecione os Jogadores Presentes (3 a 6 participantes):**")

        jogadores_selecionados = []
        chk_cols = st.columns(4)
        for i, (nome, info) in enumerate(JOGADORES_OFICIAIS.items()):
            with chk_cols[i]:
                if st.checkbox(f"{nome} ({info['cor_nome']})", value=True, key=f"chk_{nome}"):
                    jogadores_selecionados.append({"nome": nome, "oficial": True})

        # Adicionar Visitantes
        novos_visitantes = st.text_input("Nomes de Visitantes (separados por vírgula, ex: Lucas, Marcos):")
        if novos_visitantes.strip():
            for v in novos_visitantes.split(","):
                v_clean = v.strip()
                if v_clean:
                    jogadores_selecionados.append({"nome": f"{v_clean} (Visitante)", "oficial": False})

        st.markdown("---")
        st.markdown("**Pontos de Vitória (PV) Obtidos por Cada Jogador:**")

        pontuacoes = {}
        if len(jogadores_selecionados) >= 2:
            pv_cols = st.columns(len(jogadores_selecionados))
            for i, jog in enumerate(jogadores_selecionados):
                with pv_cols[i]:
                    pontuacoes[jog["nome"]] = st.number_input(
                        f"PV {jog['nome']}",
                        min_value=0,
                        max_value=30,
                        value=8 if jog["oficial"] else 6,
                        key=f"pv_{jog['nome']}"
                    )

        notas_obs = st.text_area("Observações da Partida (Ex: Destaque de desenvolvimento, Maior Estrada, etc):")
        submitted = st.form_submit_button("💾 Salvar Partida no Torneio", use_container_width=True)

        if submitted:
            num_jogs = len(jogadores_selecionados)
            if num_jogs < 3 or num_jogs > 6:
                st.error("A partida de Catan deve conter entre 3 e 6 jogadores.")
            else:
                total_mesa_pv = sum(pontuacoes.values())
                max_pv = max(pontuacoes.values())
                vencedor = [j for j, p in pontuacoes.items() if p == max_pv][0]

                novo_id = f"M{len(df['Partida_ID'].unique()) + 1:03d}"
                novas_linhas = []

                for jog in jogadores_selecionados:
                    j_nome = jog["nome"]
                    pv = pontuacoes[j_nome]
                    pv_norm = round(pv / meta_pv, 3)
                    vp_balanceado = round((pv / total_mesa_pv) * (num_jogs / 4) * 100, 2) if total_mesa_pv > 0 else 0
                    venceu = (pv == max_pv)

                    novas_linhas.append({
                        "Partida_ID": novo_id,
                        "Data": str(data_partida),
                        "Estacao": estacao_partida,
                        "Cenario": cenario_nome,
                        "Meta_PV": int(meta_pv),
                        "Expansao_5_6": expansao_5_6,
                        "Vencedor": vencedor,
                        "Jogador": j_nome,
                        "Oficial": jog["oficial"],
                        "PV": int(pv),
                        "PV_Normalizado": pv_norm,
                        "VP_Percent_Balanceado": vp_balanceado,
                        "Venceu": venceu,
                        "Notas": notas_obs
                    })

                df = pd.concat([df, pd.DataFrame(novas_linhas)], ignore_index=True)
                save_data(df)
                st.success(f"Partida {novo_id} registrada com sucesso! Vencedor: {vencedor}")
                st.rerun()

# -----------------------------------------------------------------------------
# ABA 3: RANKING ANUAL
# -----------------------------------------------------------------------------
with tab_anual:
    st.subheader("🏆 Ranking do Circuito Anual (4 Estações)")
    st.markdown("Pontuação atribuída por estação fechada: **1º: 10 pts • 2º: 6 pts • 3º: 3 pts • 4º: 1 pt**")
    an_df = calculate_annual_circuit(df)
    st.dataframe(an_df, use_container_width=True)

# -----------------------------------------------------------------------------
# ABA 4: GRÁFICOS & ESTATÍSTICAS
# -----------------------------------------------------------------------------
with tab_graficos:
    st.subheader("Análise Estatística do Torneio")
    c_g1, c_g2 = st.columns(2)

    with c_g1:
        st.markdown("**Taxa de Vitórias (%) por Jogador Oficial**")
        lb_geral = calculate_leaderboard(df, estacao="Geral", apenas_oficiais=True)
        if not lb_geral.empty:
            fig_bar = px.bar(
                lb_geral,
                x="Jogador",
                y="Taxa_Vitoria_Pct",
                color="Jogador",
                color_discrete_map={k: v["cor_hex"] for k, v in JOGADORES_OFICIAIS.items()},
                labels={"Taxa_Vitoria_Pct": "Taxa de Vitória (%)"}
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

    with c_g2:
        st.markdown("**Distribuição de Cenários Disputados**")
        cen_counts = df.drop_duplicates(subset=["Partida_ID"])["Cenario"].value_counts().reset_index()
        cen_counts.columns = ["Cenário", "Partidas"]
        fig_pie = px.pie(cen_counts, names="Cenário", values="Partidas", hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------------------------------------------------
# ABA 5: HISTÓRICO DE PARTIDAS
# -----------------------------------------------------------------------------
with tab_historico:
    st.subheader("Histórico Completo de Partidas")
    st.dataframe(df, use_container_width=True)
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Dados em CSV (compatível com Google Sheets)",
        data=csv_bytes,
        file_name="catan_torneio_dados.csv",
        mime="text/csv",
        use_container_width=True
    )

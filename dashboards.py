
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import mplcursors  # Para exibir as informações ao passar o mouse

st.set_page_config(layout="wide")

# Função para exibir as métricas no topo da página
def exibir_metricas():
    # Criando 4 colunas para exibir as métricas horizontalmente
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Returning Clients", value="5.653", delta="22.45%")
        
    with col2:
        st.metric(label="New Clients", value="1.650", delta="15.34%")
        
    with col3:
        st.metric(label="Total Parking Spaces", value="9.504")
        
    with col4:
        st.metric(label="Occupied Parking Spaces", value="5.423")

# Função para exibir o gráfico de visitas ao longo do tempo
def exibir_visitas():
    # Título do gráfico
    st.subheader("Visits Over Time")

    # Seleção do período
    periodo = st.selectbox(
        'Escolha o período para análise:',
        ('Últimas 24 horas', 'Últimos 7 dias', 'Últimos 30 dias')  # Excluindo a opção "Último ano"
    )

    # Gerando dados fictícios com base na seleção do período
    if periodo == 'Últimas 24 horas':
        time = pd.date_range("2024-01-01", periods=24, freq="H")
        time_labels = time.strftime('%H:%M')  # Mostrar horas no formato HH:MM
        time_labels = time_labels[::3]  # Exibir a cada 3 horas (00:00, 03:00, 06:00, etc.)
        time_ticks = time[::3]  # Ajustando os ticks para cada 3 horas
    elif periodo == 'Últimos 7 dias':
        time = pd.date_range("2024-01-01", periods=7, freq="D")
        time_labels = time.strftime('%d-%m')
        time_ticks = time
    elif periodo == 'Últimos 30 dias':
        time = pd.date_range("2024-01-01", periods=30, freq="D")
        # Exibindo apenas 10 rótulos, com intervalo de 3 dias
        time_labels = time[::3].strftime('%d-%m')  # Exibir de 3 em 3 dias
        time_ticks = time[::3]  # Ajustando os ticks para 10 pontos

    # Criando dados fictícios para New Clients e Returning Clients
    new_clients = np.random.randint(500, 1500, size=len(time))
    returning_clients = np.random.randint(500, 1500, size=len(time))
    
    # Criando o gráfico
    fig, ax = plt.subplots(figsize=(10, 6))  # Aumentando o tamanho do gráfico
    ax.plot(time, new_clients, label='New Clients', color='green', marker='o')
    ax.plot(time, returning_clients, label='Returning Clients', color='blue', marker='o')
    
    # Adicionando detalhes ao gráfico
    ax.set_xlabel('Hora/Dia')
    ax.set_ylabel('Número de Visitas')
    ax.set_title('Visitas ao Longo do Tempo')
    ax.set_xticks(time_ticks)  # Ajustando os ticks para o intervalo correto
    ax.set_xticklabels(time_labels)  # Ajustando os rótulos de acordo com o período selecionado
    
    # Fixando a legenda no canto superior esquerdo
    ax.legend(loc='upper left')

    # Exibindo o gráfico de visitas
    mplcursors.cursor(hover=True)  # Exibe as informações ao passar o mouse sobre o gráfico

    # Exibindo o gráfico
    st.pyplot(fig, use_container_width=False)



# Função para exibir a tabela "Recent Entries"
def exibir_recent_entries():
    # Dados fictícios para a tabela de Recent Entries
    data = {
        "Plate": ["ABC1D23", "DEF4Q56", "GHI7J89", "JKL0M12", "NOP3Q45"],
        "Time": ["05:58 PM", "05:46 PM", "05:32 PM", "05:22 PM", "05:04 PM"],
        "Amount": ["$5.97", "$9.90", "$9.90", "$14.94", "$14.94"],
        "Status": ["Out", "Out", "In", "Out", "In"]  # Status inicial
    }

    df = pd.DataFrame(data)
    
    st.write("**Recent Entries**")
    st.write("---")
    
    # Cabeçalho
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        st.write("**Plate**")
    with col2:
        st.write("**Time**")
    with col3:
        st.write("**Amount**")
    with col4:
        st.write("**Status**")

    # Linhas da tabela
    for index, row in df.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        with col1:
            st.write(row["Plate"])
        with col2:
            st.write(row["Time"])
        with col3:
            st.write(row["Amount"])
        with col4:
            # Botão horizontal para alternar o status entre "IN" e "OUT"
            # Aqui apenas exibindo o status sem funcionalidade (ajuste conforme necessário)
            if row["Status"] == "In":
                st.markdown("<div style='background-color:#a7f3d0; border-radius:4px; padding:4px; text-align:center; width:40px;'>In</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='background-color:#d1d5db; border-radius:4px; padding:4px; text-align:center; width:40px;'>Out</div>", unsafe_allow_html=True)


def exibir_distribution_by_month():
    # Dados fictícios para a tabela de distribuição por mês
    data = {
        "Month": ["November", "May", "July", "December", "January"],
        "Percentage": [55, 20, 15, 6, 4]
    }
    
    # Criando o DataFrame para exibição
    df = pd.DataFrame(data)

    st.write("**Distribution by Month**")
    st.write("---")

    # Exibindo o "título" das colunas
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("**Month**")
    with col2:
        st.write("**Percentage**")
    
    # Exibindo dados linha a linha
    for _, row in df.iterrows():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write(row['Month'])
        with col2:
            # Exibindo valor numérico e barra de progresso
            st.write(f"{row['Percentage']}%")
            st.progress(row['Percentage'])

# Barra lateral com opções de navegação
with st.sidebar:
    # Título da barra lateral
    st.header("Dashboard")
    
    # Menu de navegação para "Dashboard", "Data", "Visits", "Reports"
    menu_selecionado = st.radio(
        "Escolha uma opção",
        ("Dashboard", "Data", "Visits", "Reports"),
        index=0  # Define o Dashboard como o item selecionado por padrão
    )
    
    # Seções com as opções "Other Information" e "Settings"
    st.markdown("### Other Information", unsafe_allow_html=True)  # Título em cinza
    knowledge_base = st.checkbox("Knowledge Base")
    product_updates = st.checkbox("Product Updates")
    
    st.markdown("### Settings", unsafe_allow_html=True)  # Título em cinza
    global_settings = st.checkbox("Global Settings")

        # Uploader de CSV
    st.markdown("### Upload CSV")
    uploaded_file = st.file_uploader("Selecione um arquivo CSV", type="csv")
    if uploaded_file is not None:
        # Carregando o DataFrame a partir do CSV
        st.session_state.recent_entries_df = pd.read_csv(uploaded_file)

# Exibindo o conteúdo baseado na escolha do usuário
if menu_selecionado == "Dashboard":
    st.header("Dashboard")
    st.subheader("Visão Geral")
    exibir_metricas()  # Exibe as métricas no topo da página
    
    # Chama a função de gráficos logo abaixo das métricas
    exibir_visitas()  # Exibe o gráfico de visitas
    
    # Organizando as tabelas em duas colunas
    col1, col2 = st.columns([2, 3])  # Aumentando a largura da segunda coluna para o gráfico
    with col1:
        exibir_recent_entries()  # Exibe a tabela de Recent Entries
    with col2:
        exibir_distribution_by_month()  # Exibe a tabela de Distribution by Month

elif menu_selecionado == "Data":
    st.header("Data")
    st.write("Aqui você pode adicionar o conteúdo relacionado a 'Data'.")
    
    # Exemplo de tabela com dados fictícios
    data = pd.DataFrame({
        'ID': [1, 2, 3],
        'Nome': ['João', 'Maria', 'José'],
        'Idade': [28, 34, 25],
        'Cidade': ['São Paulo', 'Rio de Janeiro', 'Curitiba']
    })
    st.table(data)  # Exibe a tabela de dados

elif menu_selecionado == "Visits":
    st.header("Visits")
    st.write("Aqui você pode adicionar o conteúdo relacionado a 'Visits'.")
    
    # Exemplo de gráfico de visitas
    time = pd.date_range("2024-01-01", periods=12, freq="H")
    visits = np.random.randint(500, 1500, size=12)
    
    plt.plot(time, visits, label='Visitas', color='blue')
    plt.xlabel('Hora')
    plt.ylabel('Número de Visitas')
    plt.title('Visitas ao Longo do Tempo')
    plt.legend()
    
    st.pyplot(plt, use_container_width=False)  # Exibe o gráfico


# Exemplo de gráfico de relatórios
elif menu_selecionado == "Reports":
    st.header("Reports")
    st.write("Aqui você pode adicionar o conteúdo relacionado a 'Reports'.")
    
    # Exemplo de gráfico de relatórios
    categories = ['Category A', 'Category B', 'Category C']
    values = [100, 200, 300]
    
    plt.figure(figsize=(6, 4))  # Garante uma nova figura
    plt.bar(categories, values, color='green')
    plt.xlabel('Categorias')
    plt.ylabel('Valores')
    plt.title('Relatório de Categorias')
    
    st.pyplot(plt, use_container_width=False)  # Exibe o gráfico


# Exibindo as informações de "Other Information" e "Settings" com base na seleção do usuário
if knowledge_base:
    st.write("Aqui estão as informações sobre a Knowledge Base.")

if product_updates:
    st.write("Aqui estão as informações sobre Product Updates.")

if global_settings:
    st.write("Aqui você pode modificar as configurações globais.")


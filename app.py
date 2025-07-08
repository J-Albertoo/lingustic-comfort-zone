# app.py - Linguistic Comfort Zone Mapper Interface

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from src.data_loader import EnronDataLoader
from src.analyzer import LinguisticAnalyzer
import io
import base64

# Configuração da página
st.set_page_config(
    page_title="Linguistic Comfort Zone Mapper",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #e0e2e6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("🔍 Linguistic Comfort Zone Mapper")
st.markdown("### Descubra os padrões linguísticos únicos em comunicações corporativas")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Opções de análise
    analysis_mode = st.radio(
        "Modo de Análise",
        ["📧 Dataset Enron", "📝 Texto Personalizado"]
    )
    
    if analysis_mode == "📧 Dataset Enron":
        # Configurações do Enron
        st.subheader("Configurações Enron")
        
        num_emails = st.slider(
            "Número de emails para carregar",
            min_value=1000,
            max_value=10000,
            value=5000,
            step=1000
        )
        
        min_emails_person = st.slider(
            "Mínimo de emails por pessoa",
            min_value=10,
            max_value=100,
            value=30,
            step=10
        )

# Cache para dados
@st.cache_data
def load_enron_data(limit):
    loader = EnronDataLoader('data/raw/')
    df = loader.load_emails_from_csv(limit=limit)
    return loader, df

@st.cache_data
def get_person_emails(_loader, min_emails):
    return _loader.get_emails_by_person(min_emails=min_emails)

@st.cache_resource
def get_analyzer():
    return LinguisticAnalyzer()

# Função para criar visualizações com Plotly
def create_plotly_wordcloud(word_freq, title):
    # Preparar dados
    words = [item[0] for item in word_freq[:30]]
    frequencies = [item[1] for item in word_freq[:30]]
    
    # Criar gráfico de bolhas
    fig = go.Figure(data=[go.Scatter(
        x=[i % 6 for i in range(len(words))],
        y=[i // 6 for i in range(len(words))],
        mode='text',
        text=words,
        textfont=dict(
            size=[freq/10 for freq in frequencies],
            color=px.colors.qualitative.Set3[:len(words)]
        ),
        hovertext=[f'{word}: {freq} vezes' for word, freq in zip(words, frequencies)],
        hoverinfo='text'
    )])
    
    fig.update_layout(
        title=title,
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        height=400,
        plot_bgcolor='white'
    )
    
    return fig

def create_style_radar(style_data, diversity_data):
    # Preparar dados
    categories = ['Facilidade\nLeitura', 'Uso de\nExclamações', 'Uso de\nPerguntas', 
                  'Diversidade\nLexical', 'Tamanho\nFrases']
    
    values = [
        style_data['reading_ease'],
        style_data['exclamation_usage'] * 100,
        style_data['question_usage'] * 100,
        diversity_data['lexical_diversity'] * 100,
        min(style_data['avg_sentence_length'] / 30 * 100, 100)
    ]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Perfil de Estilo'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="Perfil de Estilo de Escrita"
    )
    
    return fig

# Interface principal
if analysis_mode == "📧 Dataset Enron":
    
    # Botão para iniciar análise
    if st.button("🚀 Iniciar Análise", type="primary"):
        
        with st.spinner("Carregando dados..."):
            # Carregar dados
            loader, df = load_enron_data(num_emails)
            person_emails = get_person_emails(loader, min_emails_person)
            analyzer = get_analyzer()
        
        st.success(f"✅ {len(df)} emails carregados! Encontradas {len(person_emails)} pessoas.")
        
        # Seletor de pessoa
        selected_person = st.selectbox(
            "Selecione uma pessoa para análise detalhada:",
            options=list(person_emails.keys()),
            format_func=lambda x: f"{x} ({len(person_emails[x])} emails)"
        )
        
        if selected_person:
            # Analisar pessoa selecionada
            with st.spinner(f"Analisando {selected_person}..."):
                emails = person_emails[selected_person]
                results = analyzer.analyze_person(emails, selected_person)
            
            # Layout em colunas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📧 Total de Emails", results['total_emails'])
            
            with col2:
                st.metric("📝 Palavras Únicas", f"{results['vocabulary_diversity']['unique_words']:,}")
            
            with col3:
                st.metric("📊 Diversidade Lexical", 
                         f"{results['vocabulary_diversity']['lexical_diversity']:.1%}")
            
            with col4:
                st.metric("📖 Facilidade de Leitura", 
                         f"{results['writing_style']['reading_ease']:.1f}/100")
            
            # Tabs para diferentes visualizações
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🔤 Vícios Linguísticos", 
                "📊 Estilo de Escrita", 
                "💬 Frases Favoritas",
                "🎯 Assinatura Linguística",
                "📈 Comparação"
            ])
            
            with tab1:
                st.subheader("Top Palavras Mais Usadas")
                
                # Word cloud interativa
                wordcloud_fig = create_plotly_wordcloud(
                    results['comfort_words'], 
                    "Nuvem de Vícios Linguísticos"
                )
                st.plotly_chart(wordcloud_fig, use_container_width=True)
                
                # Tabela com top palavras
                st.subheader("📊 Ranking Detalhado")
                words_df = pd.DataFrame(
                    results['comfort_words'][:20], 
                    columns=['Palavra', 'Frequência']
                )
                
                fig_bar = px.bar(
                    words_df, 
                    x='Frequência', 
                    y='Palavra', 
                    orientation='h',
                    color='Frequência',
                    color_continuous_scale='Blues'
                )
                fig_bar.update_layout(height=500)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with tab2:
                st.subheader("Análise de Estilo de Escrita")
                
                # Radar chart
                radar_fig = create_style_radar(
                    results['writing_style'],
                    results['vocabulary_diversity']
                )
                st.plotly_chart(radar_fig, use_container_width=True)
                
                # Métricas detalhadas
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info("**📏 Características Estruturais**")
                    st.write(f"- Tamanho médio de frase: **{results['writing_style']['avg_sentence_length']:.1f}** palavras")
                    st.write(f"- Uso de exclamações: **{results['writing_style']['exclamation_usage']:.2%}**")
                    st.write(f"- Uso de perguntas: **{results['writing_style']['question_usage']:.2%}**")
                
                with col2:
                    st.info("**✍️ Padrões de Pontuação**")
                    punct = results['writing_style']['punctuation_style']
                    st.write(f"- Reticências (...): **{punct['ellipsis_usage']:.2f}** por 1000 chars")
                    st.write(f"- Travessões: **{punct['dash_usage']:.2f}** por 1000 chars")
                    st.write(f"- Parênteses: **{punct['parenthesis_usage']:.2f}** por 1000 chars")
            
            with tab3:
                st.subheader("Frases e Expressões Favoritas")
                
                # Frases mais comuns
                phrases_df = pd.DataFrame(
                    results['favorite_phrases'][:15],
                    columns=['Frase', 'Frequência']
                )
                
                # Filtrar frases com caracteres especiais demais
                phrases_df = phrases_df[phrases_df['Frase'].str.count('[a-zA-Z]') > 5]
                
                fig_phrases = px.treemap(
                    phrases_df,
                    path=['Frase'],
                    values='Frequência',
                    color='Frequência',
                    color_continuous_scale='Viridis'
                )
                fig_phrases.update_layout(height=500)
                st.plotly_chart(fig_phrases, use_container_width=True)
            
            with tab4:
                st.subheader("Assinatura Linguística Única")
                
                fingerprint = results['linguistic_fingerprint']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info("**👋 Estilos de Saudação**")
                    greetings = results['email_patterns']['greeting_style']
                    for style, count in greetings.items():
                        st.write(f"- {style.replace('_', ' ').title()}: **{count}** vezes")
                    
                    st.info("**🔄 Palavras de Transição**")
                    transitions = fingerprint['transition_words']
                    for word, count in list(transitions.items())[:5]:
                        st.write(f"- {word}: **{count}** vezes")
                
                with col2:
                    st.info("**💪 Padrões de Ênfase**")
                    emphasis = fingerprint['emphasis_patterns']
                    st.write(f"- CAPS LOCK: **{emphasis['all_caps']}** ocorrências")
                    st.write(f"- Very/Really: **{emphasis['very_really']}** vezes")
                    st.write(f"- Absolutely/Definitely: **{emphasis['absolutely_definitely']}** vezes")
                    
                    st.info("**✍️ Estilos de Assinatura**")
                    signatures = results['email_patterns']['signature_style']
                    for style, count in signatures.items():
                        st.write(f"- {style.replace('_', ' ').title()}: **{count}** vezes")
            
            with tab5:
                st.subheader("Comparação com Outras Pessoas")
                
                # Analisar mais pessoas para comparação
                if st.button("Gerar Comparação"):
                    with st.spinner("Analisando outras pessoas..."):
                        
                        # Pegar até 5 pessoas
                        other_people = list(person_emails.keys())[:5]
                        comparison_data = []
                        
                        progress_bar = st.progress(0)
                        for i, person in enumerate(other_people):
                            emails = person_emails[person]
                            person_results = analyzer.analyze_person(emails, person)
                            
                            comparison_data.append({
                                'Pessoa': person.split('@')[0],
                                'Diversidade Lexical': person_results['vocabulary_diversity']['lexical_diversity'] * 100,
                                'Facilidade de Leitura': person_results['writing_style']['reading_ease'],
                                'Tamanho Médio de Frase': person_results['writing_style']['avg_sentence_length'],
                                'Total de Emails': person_results['total_emails']
                            })
                            
                            progress_bar.progress((i + 1) / len(other_people))
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        
                        # Gráfico de comparação
                        fig_comp = px.scatter(
                            comparison_df,
                            x='Diversidade Lexical',
                            y='Facilidade de Leitura',
                            size='Total de Emails',
                            hover_data=['Tamanho Médio de Frase'],
                            text='Pessoa',
                            color='Diversidade Lexical',
                            color_continuous_scale='RdYlBu'
                        )
                        
                        fig_comp.update_traces(textposition='top center')
                        fig_comp.update_layout(
                            title="Mapa de Estilos de Escrita",
                            height=600
                        )
                        
                        st.plotly_chart(fig_comp, use_container_width=True)
                        
                        # Tabela comparativa
                        st.dataframe(
                            comparison_df.style.highlight_max(axis=0, subset=['Diversidade Lexical', 'Facilidade de Leitura']),
                            use_container_width=True
                        )

else:  # Modo Texto Personalizado
    st.header("📝 Análise de Texto Personalizado")
    
    # Área de texto
    user_text = st.text_area(
        "Cole seu texto aqui (mínimo 500 palavras):",
        height=300,
        placeholder="Cole aqui emails, documentos ou qualquer texto que você queira analisar..."
    )
    
    if st.button("🔍 Analisar Meu Texto", type="primary"):
        if len(user_text.split()) < 100:
            st.error("❌ Por favor, insira um texto com pelo menos 100 palavras para uma análise significativa.")
        else:
            analyzer = get_analyzer()
            
            # Simular formato de email para reutilizar o analyzer
            fake_emails = [user_text]
            
            with st.spinner("Analisando seu texto..."):
                results = analyzer.analyze_person(fake_emails, "Seu Texto")
            
            # Mostrar resultados
            st.success("✅ Análise completa!")
            
            # Métricas principais
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📝 Palavras Únicas", f"{results['vocabulary_diversity']['unique_words']:,}")
            
            with col2:
                st.metric("📊 Diversidade Lexical", 
                         f"{results['vocabulary_diversity']['lexical_diversity']:.1%}")
            
            with col3:
                st.metric("📖 Facilidade de Leitura", 
                         f"{results['writing_style']['reading_ease']:.1f}/100")
            
            # Vícios linguísticos
            st.subheader("🔤 Seus Vícios Linguísticos")
            
            words_df = pd.DataFrame(
                results['comfort_words'][:15], 
                columns=['Palavra', 'Frequência']
            )
            
            fig = px.bar(
                words_df, 
                x='Palavra', 
                y='Frequência',
                color='Frequência',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Recomendações
            st.subheader("💡 Recomendações Personalizadas")
            
            diversity = results['vocabulary_diversity']['lexical_diversity']
            
            if diversity < 0.15:
                st.warning("""
                **Vocabulário Repetitivo Detectado!**
                - Sua diversidade lexical está abaixo de 15%
                - Tente usar mais sinônimos
                - Evite repetir as mesmas palavras de transição
                """)
            else:
                st.success("""
                **Boa Diversidade Vocabular!**
                - Sua escrita mostra variedade adequada
                - Continue explorando novas palavras
                """)
            
            # Download do relatório
            if st.button("📥 Baixar Relatório Completo"):
                report = f"""
                RELATÓRIO DE ANÁLISE LINGUÍSTICA
                ================================
                
                Palavras Únicas: {results['vocabulary_diversity']['unique_words']}
                Diversidade Lexical: {results['vocabulary_diversity']['lexical_diversity']:.2%}
                Facilidade de Leitura: {results['writing_style']['reading_ease']:.1f}/100
                
                TOP 10 VÍCIOS LINGUÍSTICOS:
                {chr(10).join([f"- {word}: {count} vezes" for word, count in results['comfort_words'][:10]])}
                
                ESTILO DE ESCRITA:
                - Tamanho médio de frase: {results['writing_style']['avg_sentence_length']:.1f} palavras
                - Uso de exclamações: {results['writing_style']['exclamation_usage']:.2%}
                - Uso de perguntas: {results['writing_style']['question_usage']:.2%}
                """
                
                st.download_button(
                    label="Download Relatório TXT",
                    data=report,
                    file_name="analise_linguistica.txt",
                    mime="text/plain"
                )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Desenvolvido com ❤️ usando Python, Streamlit e NLP</p>
    <p>Linguistic Comfort Zone Mapper © 2025</p>
</div>
""", unsafe_allow_html=True)
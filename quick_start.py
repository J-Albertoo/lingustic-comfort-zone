# quick_start.py - Versão corrigida e melhorada

from src.data_loader import EnronDataLoader
from src.analyzer import LinguisticAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

def quick_start_analysis():
    """Script para começar a análise rapidamente"""
    
    # 1. Carregar dados
    print("🚀 Iniciando Linguistic Comfort Zone Mapper!")
    print("-" * 50)
    
    # Verificar se o arquivo existe
    data_path = 'data/raw/'
    if not os.path.exists(os.path.join(data_path, 'emails.csv')):
        print("❌ ERRO: Arquivo 'emails.csv' não encontrado em data/raw/")
        print("📥 Por favor, baixe o dataset do Kaggle primeiro:")
        print("   https://www.kaggle.com/datasets/wcukierski/enron-email-dataset")
        return
    
    loader = EnronDataLoader(data_path)
    
    # Começar com subset pequeno para testar
    df = loader.load_emails_from_csv(limit=5000)
    
    # 2. Preparar dados por pessoa
    person_emails = loader.get_emails_by_person(min_emails=30)
    
    if not person_emails:
        print("❌ Nenhuma pessoa encontrada com emails suficientes!")
        return
    
    # 3. Analisar primeira pessoa
    analyzer = LinguisticAnalyzer()
    
    # Pegar primeira pessoa com muitos emails
    first_person = list(person_emails.keys())[0]
    emails = person_emails[first_person]
    
    print(f"\n📊 Analisando padrões linguísticos de: {first_person}")
    print(f"📧 Total de emails: {len(emails)}")
    print("-" * 50)
    
    # 4. Rodar análise
    results = analyzer.analyze_person(emails, first_person)
    
    # 5. Mostrar resultados
    print("\n🎯 TOP 10 VÍCIOS LINGUÍSTICOS:")
    for word, count in results['comfort_words'][:10]:
        print(f"  • {word}: {count} vezes")
    
    print("\n💬 FRASES FAVORITAS:")
    for phrase, count in results['favorite_phrases'][:5]:
        print(f"  • '{phrase}': {count} vezes")
    
    print("\n📝 ESTILO DE ESCRITA:")
    style = results['writing_style']
    print(f"  • Tamanho médio de frase: {style['avg_sentence_length']:.1f} palavras")
    print(f"  • Facilidade de leitura: {style['reading_ease']:.1f}/100")
    print(f"  • Uso de exclamações: {style['exclamation_usage']:.2%}")
    
    print("\n📊 DIVERSIDADE VOCABULAR:")
    div = results['vocabulary_diversity']
    print(f"  • Palavras únicas: {div['unique_words']:,}")
    print(f"  • Diversidade lexical: {div['lexical_diversity']:.2%}")
    
    print("\n✨ ASSINATURA LINGUÍSTICA:")
    finger = results['linguistic_fingerprint']
    print(f"  • Estilo de saudação: {results['email_patterns']['greeting_style']}")
    print(f"  • Palavras de transição favoritas: {list(finger['transition_words'].keys())[:3]}")
    
    # 6. CRIAR VISUALIZAÇÕES
    create_visualizations(results, first_person)
    
    print("\n✅ Análise inicial completa! Verifique as imagens geradas! 📊")
    
    return results, first_person, person_emails

def create_visualizations(results, person_name):
    """Cria visualizações dos resultados"""
    
    # Criar pasta para outputs se não existir
    os.makedirs('outputs', exist_ok=True)
    
    # 1. Word Cloud dos vícios linguísticos
    print("\n🎨 Gerando visualizações...")
    
    words_freq = dict(results['comfort_words'])
    
    # Configurar word cloud com cores profissionais
    wordcloud = WordCloud(
        width=1200, 
        height=600, 
        background_color='white',
        colormap='viridis',
        max_words=50,
        relative_scaling=0.5,
        min_font_size=10
    ).generate_from_frequencies(words_freq)
    
    # Criar figura
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Vícios Linguísticos de {person_name}', fontsize=16, pad=20)
    plt.tight_layout()
    
    # Salvar
    wordcloud_path = 'outputs/wordcloud_vicios.png'
    plt.savefig(wordcloud_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Word cloud salva em: {wordcloud_path}")
    
    # 2. Gráfico de barras dos top vícios
    plt.figure(figsize=(10, 6))
    
    # Pegar top 15 palavras
    top_words = results['comfort_words'][:15]
    words = [w[0] for w in top_words]
    counts = [w[1] for w in top_words]
    
    # Criar gráfico de barras horizontal
    plt.barh(words, counts, color='steelblue')
    plt.xlabel('Frequência', fontsize=12)
    plt.title(f'Top 15 Palavras Mais Usadas - {person_name}', fontsize=14, pad=20)
    plt.gca().invert_yaxis()  # Maior no topo
    
    # Adicionar valores nas barras
    for i, (word, count) in enumerate(top_words):
        plt.text(count + 5, i, str(count), va='center')
    
    plt.tight_layout()
    
    # Salvar
    bars_path = 'outputs/top_palavras.png'
    plt.savefig(bars_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Gráfico de barras salvo em: {bars_path}")
    
    # 3. Análise de estilo de escrita (radar chart)
    import numpy as np
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    # Preparar dados para o radar
    categories = ['Facilidade\nLeitura', 'Uso de\nExclamações', 'Uso de\nPerguntas', 
                  'Diversidade\nLexical', 'Tamanho\nFrases']
    
    style = results['writing_style']
    div = results['vocabulary_diversity']
    
    # Normalizar valores para escala 0-100
    values = [
        style['reading_ease'],
        style['exclamation_usage'] * 100,
        style['question_usage'] * 100,
        div['lexical_diversity'] * 100,
        min(style['avg_sentence_length'] / 30 * 100, 100)  # Normalizar para max 30 palavras
    ]
    
    # Fechar o radar
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]
    
    # Plot
    ax.plot(angles, values, 'o-', linewidth=2, color='darkblue')
    ax.fill(angles, values, alpha=0.25, color='skyblue')
    
    # Labels
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 100)
    ax.set_title(f'Perfil de Estilo de Escrita - {person_name}', y=1.08, fontsize=14)
    
    plt.tight_layout()
    
    # Salvar
    radar_path = 'outputs/estilo_escrita_radar.png'
    plt.savefig(radar_path, dpi=300, bbox_inches='tight')
    print(f"  ✓ Radar de estilo salvo em: {radar_path}")
    
    plt.close('all')  # Fechar todas as figuras

def analyze_multiple_people(person_emails, analyzer, max_people=5):
    """Analisa múltiplas pessoas para comparação"""
    
    print(f"\n🔍 Analisando {min(max_people, len(person_emails))} pessoas para comparação...")
    
    all_results = {}
    
    for i, (person, emails) in enumerate(person_emails.items()):
        if i >= max_people:
            break
            
        print(f"  • Analisando {person}... ({i+1}/{max_people})")
        results = analyzer.analyze_person(emails, person)
        all_results[person] = results
    
    return all_results

def create_comparison_visualization(all_results):
    """Cria visualização comparando múltiplas pessoas"""
    
    import pandas as pd
    
    # Preparar dados para comparação
    comparison_data = []
    
    for person, results in all_results.items():
        comparison_data.append({
            'Pessoa': person.split('@')[0],  # Apenas nome antes do @
            'Diversidade Lexical': results['vocabulary_diversity']['lexical_diversity'] * 100,
            'Facilidade Leitura': results['writing_style']['reading_ease'],
            'Emails Analisados': results['total_emails']
        })
    
    df = pd.DataFrame(comparison_data)
    
    # Criar gráfico de comparação
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Gráfico 1: Diversidade Lexical
    df.plot(x='Pessoa', y='Diversidade Lexical', kind='bar', ax=ax1, color='teal')
    ax1.set_title('Diversidade Lexical por Pessoa', fontsize=14)
    ax1.set_ylabel('Diversidade (%)')
    ax1.set_xlabel('')
    ax1.set_xticklabels(df['Pessoa'], rotation=45, ha='right')
    
    # Gráfico 2: Facilidade de Leitura
    df.plot(x='Pessoa', y='Facilidade Leitura', kind='bar', ax=ax2, color='coral')
    ax2.set_title('Facilidade de Leitura por Pessoa', fontsize=14)
    ax2.set_ylabel('Score Flesch (0-100)')
    ax2.set_xlabel('')
    ax2.set_xticklabels(df['Pessoa'], rotation=45, ha='right')
    
    plt.suptitle('Comparação de Estilos de Escrita - Dataset Enron', fontsize=16)
    plt.tight_layout()
    
    # Salvar
    comparison_path = 'outputs/comparacao_pessoas.png'
    plt.savefig(comparison_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Gráfico de comparação salvo em: {comparison_path}")
    
    plt.close()

if __name__ == "__main__":
    # Rodar análise principal
    result = quick_start_analysis()
    
    if result:  # Se a análise foi bem sucedida
        results, first_person, person_emails = result
        
        # Perguntar se quer analisar mais pessoas
        print("\n" + "="*50)
        print("🤔 Deseja analisar mais pessoas para comparação? (s/n)")
        
        # Para automação, vamos assumir 'sim'
        # Em produção, você usaria: response = input().lower()
        response = 's'  # Automatizado para o exemplo
        
        if response == 's':
            analyzer = LinguisticAnalyzer()
            all_results = analyze_multiple_people(person_emails, analyzer, max_people=5)
            create_comparison_visualization(all_results)
            
            print("\n🎉 Análise completa! Verifique a pasta 'outputs' para todas as visualizações!")
            print("\n📊 Próximos passos:")
            print("  1. Analise os gráficos gerados")
            print("  2. Identifique padrões interessantes")
            print("  3. Prepare insights para o LinkedIn")
            print("  4. Comece a construir o app Streamlit!")
# Linguistic Comfort Zone Mapper 📝

Mapeie padrões linguísticos, vícios de escrita e assinaturas de estilo em corporações ou textos pessoais, tudo em poucos cliques — com **Python**, **Streamlit** e **NLP**.

> **TL;DR**: Carregue um conjunto de e‑mails (Ex.: *Enron*), escolha uma pessoa e visualize nuvem de palavras, gráfico radar, frases favoritas, métricas de diversidade léxica e comparação entre autores. Ou cole qualquer texto longo e receba um relatório instantâneo.

---
## EXemplo Visual:
![Gravando 2025-07-07 214230](https://github.com/user-attachments/assets/ecbaa309-b6f5-4686-badc-71d1f54f2e00)
---


## 🔥 Destaques

| 💡 | Recurso |
|----|---------|
| 🖼 | **Dashboard interativo** em Streamlit com Plotly & WordCloud |
| 🧠 | **Análise NLP** completa: diversidade lexical, facilidade de leitura, vícios linguísticos, fingerprint |
| 🕵️‍♂️ | **Comparação multi‑autor** para descobrir quem escreve melhor (ou pior!) |
| ⚡ | **Quick‑start CLI** (`quick_start.py`) para insights em 30 s |
| 📦 | Pronto para **Docker/Streamlit Cloud/HF Spaces** |

---

## 🚀 Instalação Rápida

```bash
# 1) Clone o repo
git clone https://github.com/<seu-user>/linguistic-comfort-zone.git
cd linguistic-comfort-zone

# 2) Crie venv + instale deps
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3) Baixe o dataset (opcional)
kaggle datasets download wcukierski/enron-email-dataset -p data/raw
unzip data/raw/enron-email-dataset.zip -d data/raw

## IMPORTAÇÃO DAS FERRAMENTAS NECESSÁRIAS
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import PyPDF2 as pdf
import numpy as np
import pandas as pd
from gtts import gTTS
import io
from PIL import Image
import time
from google.api_core import exceptions

## 1. CONFIGURAÇÃO INICIAL DA PÁGINA
st.set_page_config(
    page_title="brAIn Wiser",
    layout="wide"
)

## 2. CARREGAMENTO DE CONFIGURAÇÕES E API
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Chave de API do Google não encontrada!")
    st.stop()
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"Erro ao configurar a API do Gemini: {e}")
    st.stop()

## 3. DESIGN (CSS)
st.markdown("""
    <style>
        html, body, .stApp { background-color: #1B1C1D !important; color: #FFFFFF !important; font-family: 'sans-serif'; }
        .block-container { padding: 2rem 5rem; }
        .divider { margin-top: 3rem; margin-bottom: 3rem; border-top: 1px solid rgba(255, 255, 255, 0.1); }
        h1, h2, h3 { color: #FFFFFF; font-weight: 300; }
        
        .logo-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #FFFFFF;
        }

        .stTabs [data-baseweb="tab-list"] { gap: 2rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
        .stTabs [data-baseweb="tab"] { padding: 10px 0; background-color: transparent; color: rgba(255, 255, 255, 0.5); border-bottom: 2px solid transparent; transition: color 0.3s; }
        .stTabs [data-baseweb="tab"]:hover { color: #FFFFFF; }
        .stTabs [aria-selected="true"] { color: #FFFFFF; font-weight: 600; border-bottom: 2px solid #355572; }
        .stButton>button { background-color: #355572; color: #FFFFFF; border: none; padding: 12px 25px; border-radius: 8px; font-weight: 600; transition: background-color 0.3s; width: 100%; }
        .stButton>button:hover { background-color: #70315E; }
        .stTextInput input:focus, .stChatInput input:focus { border-color: #355572 !important; box-shadow: 0 0 0 1px #355572 !important; }
        .stMultiSelect > div[data-baseweb="select"]:focus-within { border-color: #355572 !important; box-shadow: 0 0 0 1px #355572 !important; }
        .stMultiSelect div[data-baseweb="tag"] { background-color: #70315E !important; border-radius: 8px; }
        .st-emotion-cache-1c7y2kd { background-color: #2a2a2e; }
        .st-emotion-cache-4oy321 { background-color: #355572; }
        .stChatInput { background-color: #1B1C1D; }
        .stTextInput>div>div>input { background-color: #2a2a2e; border-radius: 8px; }
        .footer { margin-top: 4rem; text-align: center; padding: 1rem; color: rgba(255, 255, 255, 0.3); font-size: 0.9rem; }
    </style>
""", unsafe_allow_html=True)

## 4. FUNÇÕES DO "MOTOR" DA APLICAÇÃO
@st.cache_data
def extract_text_from_pdfs(pdf_folder):
    texts = {}
    if not os.path.exists(pdf_folder): return {}
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            filepath = os.path.join(pdf_folder, filename)
            text = ""
            try:
                reader = pdf.PdfReader(filepath)
                for page in reader.pages: text += page.extract_text() or ""
                texts[filename] = text
            except Exception: pass
    return texts

@st.cache_resource
def create_chunk_embeddings(texts):
    if not texts: return pd.DataFrame()
    model = 'models/text-embedding-004'
    chunks = []
    for doc_name, text in texts.items():
        for i in range(0, len(text), 1000):
            chunks.append({"source": doc_name, "text": text[i:i+1000]})
    df = pd.DataFrame(chunks)
    embeddings_list = []
    progress_bar = st.progress(0, text="Analisando documentos pela primeira vez...")
    for i, row in df.iterrows():
        try:
            result = genai.embed_content(model=model, content=row['text'])
            embeddings_list.append(result['embedding'])
            time.sleep(0.5)
            progress_bar.progress((i + 1) / len(df), text=f"Analisando parágrafo {i+1}/{len(df)}...")
        except exceptions.ResourceExhausted:
            st.error("Limite da API de análise atingido. Aguarde um minuto e recarregue a página.")
            return pd.DataFrame()
    df['embedding'] = embeddings_list
    progress_bar.empty()
    return df

def find_best_chunks(query, dataframe):
    model = 'models/text-embedding-004'
    query_embedding = genai.embed_content(model=model, content=query)['embedding']
    doc_embeddings = np.array(dataframe['embedding'].tolist())
    scores = np.dot(doc_embeddings, query_embedding)
    top_indices = np.argsort(scores)[-3:][::-1]
    return dataframe.iloc[top_indices]

def generate_gemini_response(prompt_text):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt_text)
        return response.text
    except exceptions.ResourceExhausted:
        return "A API está sobrecarregada no momento. Tente novamente."
    except Exception as e:
        return f"Ocorreu um erro: {e}"

def extract_text_from_uploaded_pdf(uploaded_file):
    text = ""
    try:
        reader = pdf.PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception:
        text = "Não foi possível ler o arquivo PDF."
    return text

## 5. LÓGICA DA INTERFACE
all_texts = extract_text_from_pdfs("documentos")
if not all_texts:
    st.error("Nenhum arquivo PDF encontrado na pasta 'documentos'.")
    st.stop()
embeddings_df = create_chunk_embeddings(all_texts)
if embeddings_df.empty: st.stop()

if "messages" not in st.session_state: st.session_state.messages = []
if "last_analysis" not in st.session_state: st.session_state.last_analysis = ""

st.markdown('<h1 class="logo-title">brAIn Wiser</h1>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Chat de estratégia", "Análise cruzada", "Transformar conteúdo"])

with tab1:
    st.header("Descreva sua estratégia ou faça uma pergunta")
    with st.expander("Adicionar um documento de contexto para esta conversa"):
        uploaded_file = st.file_uploader("Selecione um PDF", type="pdf", key="file_uploader")
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Sua mensagem..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analisando..."):
                best_chunks = find_best_chunks(prompt, embeddings_df)
                context = "\n\n".join([f"**Trecho de '{r['source']}':**\n{r['text']}" for _, r in best_chunks.iterrows()])
                if uploaded_file is not None:
                    uploaded_file_text = extract_text_from_uploaded_pdf(uploaded_file)
                    context = f"**Contexto de um documento enviado pelo usuário:**\n{uploaded_file_text}\n\n---\n\n{context}"
                final_prompt = f"**Contexto:**\n{context}\n\n**Pergunta:** {prompt}\n\n**Resposta:**"
                full_response = generate_gemini_response(final_prompt)
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                if "A API está sobrecarregada" not in full_response:
                    st.session_state.last_analysis = full_response
        st.rerun()

with tab2:
    st.header("Cruze informações entre documentos")
    selected_docs = st.multiselect("Selecione os documentos:", list(all_texts.keys()), placeholder="Escolha 2 ou mais documentos")
    if st.button("Analisar sinergias", key="analise_cruzada"):
        if len(selected_docs) < 2:
            st.warning("Selecione pelo menos dois documentos.")
        else:
            with st.spinner("Realizando análise cruzada..."):
                context = "\n\n".join([f"--- Conteúdo do Documento: {d} ---\n{all_texts[d][:4000]}" for d in selected_docs])
                final_prompt = f"Analise os documentos e descreva em tópicos:\n1. Sinergias.\n2. Conflitos.\n3. Recomendações.\n\n{context}"
                analysis_result = generate_gemini_response(final_prompt)
                st.markdown(analysis_result)
                if "A API está sobrecarregada" not in analysis_result:
                    st.session_state.last_analysis = analysis_result

with tab3:
    st.header("Absorva o conteúdo do seu jeito")
    if not st.session_state.last_analysis:
        st.info("Gere um conteúdo no 'chat' ou na 'análise cruzada' primeiro.")
    else:
        st.text_area("Última análise gerada:", st.session_state.last_analysis, height=200, label_visibility="collapsed")
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        col1, col2, _ = st.columns([0.2, 0.2, 0.6])
        with col1:
            if st.button("Gerar mapa mental"):
                with st.spinner("Criando mapa mental..."):
                    
                    final_prompt = f"""
                    Transforme o texto em um mapa mental no formato DOT language do Graphviz com um tema escuro e moderno.
                    Comece a resposta diretamente com 'digraph G {{'. Não inclua a palavra 'graphviz' ou ```.

                    Use este template de estilo:
                    digraph G {{
                        graph [bgcolor="transparent", rankdir=TB];
                        node [shape=box, style="rounded,filled", fontname="sans-serif", fontcolor="#FFFFFF", color="#70315E", fillcolor="#355572"];
                        edge [color="#FFFFFF", style=solid];

                        // Defina as conexões aqui, como "Nó Principal" -> "Sub-nó";
                    }}

                    Texto para converter:
                    {st.session_state.last_analysis}
                    """
                    
                    response_text = generate_gemini_response(final_prompt)
                    st.subheader("Mapa mental da análise")
                    try:
                        st.graphviz_chart(response_text)
                    except Exception:
                        st.error("Não foi possível gerar o mapa mental. A IA pode ter retornado um formato inválido.")
                        st.text(response_text) # Mostra o código gerado para depuração

        with col2:
            if st.button("Gerar áudio da análise"):
                with st.spinner("Gerando áudio..."):
                    tts = gTTS(text=st.session_state.last_analysis, lang='pt-br')
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format='audio/mp3')

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="footer">powered by wiser educação</div>', unsafe_allow_html=True)
# Documentação do projeto: brAIn Wiser (MVP)

**Versão:** 1.0 (MVP)
**Data:** 15 de Setembro de 2025

## 1. Visão geral do projeto

A **brAIn Wiser** é uma plataforma de inteligência estratégica projetada para facilitar a integração e gestão da informação entre os times do grupo Wiser Educação. A solução centraliza o conhecimento contido em diversos documentos, oferecendo uma visão 360º das estratégias e promovendo a descoberta de sinergias entre diferentes projetos e departamentos.

Construído como um MVP (Mínimo Produto Viável), este protótipo demonstra as três funcionalidades principais que formam o núcleo da plataforma, utilizando uma arquitetura de custo zero para fins de validação e demonstração.


---

## 2. Funcionalidades principais (MVP)

O projeto é apresentado em uma interface web com três abas, cada uma correspondendo a uma funcionalidade essencial:

1.  **Chat de Estratégia (com RAG):**
    *   **O que faz:** permite que o usuário converse com os documentos da base de conhecimento da empresa. O usuário pode fazer perguntas em linguagem natural ou descrever uma nova estratégia
    *   **Como funciona:** a IA utiliza um modelo de **RAG (Retrieval-Augmented Generation)** para encontrar os parágrafos mais relevantes nos documentos existentes e, com base neles, formula uma resposta coesa e contextualizada.
    *   **Funcionalidade adicional:** o usuário pode fazer o **upload de um documento PDF** temporário para fornecer contexto adicional para a sua pergunta, ideal para "briefings" de novos projetos

2.  **Análise Cruzada:**
    *   **O que faz:** permite ao usuário selecionar dois ou mais documentos da base de conhecimento para que a IA realize uma análise comparativa.
    *   **Como funciona:** a IA recebe o conteúdo dos documentos selecionados e gera uma análise destacando pontos de sinergia, possíveis conflitos ou sobreposições e recomendações de integração entre as estratégias apresentadas

3.  **Transformar Conteúdo:**
    *   **O que faz:** pega a última análise gerada (seja pelo chat ou pela análise cruzada) e a transforma em formatos alternativos, adaptando-se a diferentes modelos de aprendizagem
    *   **Como funciona:**
        *   **Mapa Mental:** a IA converte o texto em um diagrama visual no formato **Graphviz**, destacando a hierarquia e as conexões entre as ideias. O mapa é estilizado com um tema moderno e escuro
        *   **Áudio:** a IA utiliza uma biblioteca de Text-to-Speech para converter a análise em um arquivo de áudio, permitindo que o usuário ouça o conteúdo em formato de "podcast"

---

## 3. Arquitetura e stack de tecnologias

A arquitetura foi planejada para ter **custo zero** de implantação e manutenção durante a fase de MVP

*   **Linguagem:** Python
*   **Framework web (frontend e backend):** Streamlit
*   **Modelo de IA Generativa:** Google Gemini (`gemini-1.5-flash-latest`) via API do Google AI Studio
*   **Vetorização de texto (Embeddings):** Google Text Embedding Model (`text-embedding-004`)
*   **Processamento de documentos:** PyPDF2
*   **Geração de mapas mentais:** Graphviz (renderizado nativamente pelo Streamlit)
*   **Geração de áudio:** gTTS (Google Text-to-Speech)
*   **Hospedagem:** Streamlit Community Cloud

---

## 4. Estrutura de arquivos do projeto

O projeto está contido em uma única pasta com uma estrutura simples e organizada:

brain_wiser_mvp/
├── documentos/
│   └── (local para os PDFs que formam a base de conhecimento)
├── .env                  # Arquivo para guardar a chave secreta da API do Google
├── app.py                # O código-fonte completo da aplicação
└── requirements.txt      # Lista de todas as dependências do projeto para fácil instalação

---

## 5. Guia de instalação e execução

Para executar o projeto em um ambiente local, siga os passos abaixo:

1.  **Pré-requisitos:** certifique-se de ter o **Python 3.8+** instalado em seu computador
2.  **Obtenha a chave de API:**
    *   Acesse o Google AI Studio (https://aistudio.google.com/)
    *   Gere uma chave de API e cole-a no arquivo `.env` no formato: `GOOGLE_API_KEY="SUA_CHAVE_AQUI"`
3.  **Instale as dependências:**
    *   Abra um terminal de comandos na pasta raiz do projeto
    *   Execute o comando: `pip install -r requirements.txt`
4.  **Adicione os documentos:** coloque os arquivos PDF que servirão de base de conhecimento dentro da pasta `documentos/`
5.  **Execute a aplicação:**
    *   no mesmo terminal, execute o comando: `streamlit run app.py`

---

## 6. Próximos passos e sugestões de evolução

Após a validação, os seguintes passos podem ser considerados para evoluir o projeto:

1.  **Voz de alta qualidade (TTS Neural):** substituir a biblioteca `gTTS` por uma API profissional como a do **Google Cloud Text-to-Speech** ou **ElevenLabs** para gerar áudios com vozes neurais
2.  **Banco de dados vetorial escalável:** migrar a busca de similaridade para um serviço gerenciado como o **Vertex AI Vector Search** ou **Pinecone** para escalar a solução para milhares de documentos
3.  **Autenticação de usuários:** implementar um sistema de login (ex.: OAuth com Contas Google) para garantir a segurança dos dados
4.  **Sincronização uutomática com o Google Drive:** criar um serviço que monitore a pasta do Google Drive da wiser e atualize automaticamente a base de conhecimento

5.  **Geração de vídeos:** implementar a funcionalidade de geração de vídeo utilizando APIs como a do **Synthesia** ou **RunwayML**


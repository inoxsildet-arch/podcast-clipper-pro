# 🎙️ Podcast Clipper PRO

**Automação inteligente de cortes para podcasts.** Transforma vídeos longos do YouTube em Shorts virais e cortes narrativos, usando transcrição por IA, curadoria de conteúdo multi-perspectiva e legendas dinâmicas — tudo rodando localmente.

*Projeto iniciado em Janeiro/2026, em desenvolvimento contínuo desde então.*

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

---

## 📖 Sobre o projeto

O **Podcast Clipper PRO** automatiza o processo (normalmente manual e demorado) de transformar episódios longos de podcast em conteúdo de curta duração pronto para redes sociais. A ferramenta:

1. Baixa o vídeo a partir de uma URL do YouTube (com cache local para evitar downloads repetidos)
2. Transcreve o áudio com [OpenAI Whisper](https://github.com/openai/whisper)
3. Analisa a transcrição usando um modelo de linguagem local (via [Ollama](https://ollama.com)), sob **4 perspectivas de curadoria diferentes e customizáveis** (ex: viral, storytelling, reflexivo, técnico)
4. Corta, ajusta velocidade/volume, converte para formato vertical (9:16) e aplica **legendas dinâmicas estilo karaokê** com dicionário de emojis treinável
5. Organiza tudo em pastas de saída, com relatórios e cache de transcrição reaproveitável

Todo o pipeline roda **localmente** — a única dependência de nuvem opcional é uma API key de LLM (Gemini/Qwen), caso você prefira não usar um modelo local via Ollama.

---

## ✨ Funcionalidades

- **Fila em lote (batch)** — processa múltiplos vídeos de uma vez, um por linha
- **Cache inteligente** — reaproveita download e transcrição se o mesmo vídeo for reprocessado
- **Curadoria por regras customizáveis** — 4 "personas" de análise, editáveis, importáveis/exportáveis em `.json`
- **Cortes duplos**: gera tanto Shorts (30–60s, formato vertical) quanto Cortes narrativos (40–120s, formato horizontal)
- **Edição automática**: aceleração de velocidade, ajuste de volume (dB), espelhamento horizontal, crop inteligente 9:16
- **Legendas dinâmicas** em 4 estilos (Formal, Divertida, Emoji Pop, Karaokê palavra-por-palavra)
- **Dicionário de emojis treinável** — associa palavras-chave a emojis automaticamente nas legendas
- **Modo de Teste Rápido (10s)** — valida fonte, cor e posição da legenda sem precisar rodar o pipeline completo
- **Tela de Configurações** — API keys, endpoint do Ollama, prioridade de modelos, pasta de saída, parâmetros de edição — tudo editável pela interface, sem mexer em código
- **Feedback sonoro** — bips indicando o progresso de cada etapa
- **Desligamento automático** do PC ao final do processamento em lote (opcional)

---

## 🗂️ Estrutura do projeto

```
podcast-clipper-pro/
├── main.py                    # Orquestra o pipeline (download → transcrição → curadoria → edição)
├── gui.py                     # Interface gráfica (CustomTkinter)
├── config.py                  # Configurações centralizadas, persistidas em app_settings.json
├── downloader.py               # Download de vídeos (yt-dlp) com reaproveitamento de cache
├── transcriber.py              # Transcrição de áudio (Whisper) com cache em .json
├── ai_curator.py               # Curadoria de conteúdo via LLM local (Ollama) ou API externa
├── video_editor.py             # Corte, crop, velocidade, volume, espelhamento e composição de legendas
├── subtitle_generator.py       # Geração de legendas dinâmicas (estilos + emojis)
├── requirements.txt
├── app_settings.example.json   # Modelo de configuração (sem dados sensíveis)
├── custom_rules.example.json   # Modelo de regras de curadoria
├── .gitignore
├── LICENSE
└── README.md
```

### Arquivos gerados em tempo de execução (não versionados)

| Caminho | Conteúdo |
|---|---|
| `app_settings.json` | Suas configurações reais (API keys, caminhos, preferências) |
| `custom_rules.json` | Suas regras de curadoria personalizadas |
| `temp/` | Vídeos baixados e transcrições em cache |
| `outputs/` | Vídeos finais, organizados por projeto |
| `venv/` | Ambiente virtual Python |

---

## 🔧 Pré-requisitos

Além do Python, o projeto depende de três programas externos que **não são instalados via pip**:

| Ferramenta | Uso | Link |
|---|---|---|
| **FFmpeg** | Corte e codificação de vídeo/áudio | https://ffmpeg.org/download.html |
| **ImageMagick** | Renderização de texto nas legendas (usado pelo MoviePy) | https://imagemagick.org/script/download.php |
| **Ollama** | Execução local do modelo de IA para curadoria de conteúdo | https://ollama.com/download |

Depois de instalar o Ollama, baixe um modelo compatível (ajuste o nome do modelo em `app_settings.json` conforme o que você baixar):

```bash
ollama pull llama3
```

> **Windows**: garanta que `ffmpeg` e `magick` (ImageMagick) estejam no PATH do sistema, ou configure o caminho completo do ImageMagick diretamente na tela de Configurações do app.

---

## 🚀 Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/podcast-clipper-pro.git
cd podcast-clipper-pro

# 2. Crie e ative um ambiente virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Instale as dependências
python -m pip install -r requirements.txt

# 4. Copie os arquivos de exemplo de configuração
copy app_settings.example.json app_settings.json      # Windows
copy custom_rules.example.json custom_rules.json      # Windows
# cp app_settings.example.json app_settings.json      # Linux/Mac
# cp custom_rules.example.json custom_rules.json      # Linux/Mac

# 5. Edite app_settings.json (ou use a tela de Configurações do app)
#    para apontar a pasta de saída (base_path) e, se necessário,
#    o caminho do ImageMagick.

# 6. Execute
python gui.py
```

---

## ⚙️ Configuração

A maior parte das configurações é editável direto pela interface (botões **🛠️ Configurações** e **🎨 Legendas & Emojis**), sem precisar tocar em código. Os principais campos:

| Campo | Descrição |
|---|---|
| `base_path` | Pasta raiz onde `outputs/` e `temp/` serão criados |
| `local_ai_url` | Endpoint da API local do Ollama (padrão: `http://localhost:11434/api/generate`) |
| `ai_models_priority` | Lista de modelos, em ordem de tentativa (fallback automático se um falhar) |
| `gemini_api_key` / `qwen_api_key` | Chaves opcionais, caso queira usar um provedor de IA externo no lugar do Ollama local |
| `speed_multiplier` / `volume_adjust` | Parâmetros padrão de edição de vídeo |
| `subtitle_*` | Fonte, tamanho, cor, contorno e posição vertical da legenda |
| `imagemagick_path` | Caminho absoluto do `magick.exe`, caso o MoviePy não detecte automaticamente |
| `emoji_dictionary` | Dicionário palavra → emoji, usado no estilo de legenda "Emoji Pop" |

> ⚠️ **Nunca faça commit do seu `app_settings.json` real** se ele contiver API keys. O `.gitignore` já está configurado para ignorá-lo — use `app_settings.example.json` como modelo de referência no repositório.

---

## 🎬 Como usar

1. Abra o app com `python gui.py`
2. Cole uma ou mais URLs do YouTube na caixa de fila, uma por linha, no formato:
   ```
   https://youtube.com/watch?v=exemplo, 0, 0
   ```
   (URL, tempo inicial em segundos, tempo final em segundos — `0, 0` processa o vídeo inteiro)
3. Escolha o modo (`normal` ou `shorts`), opções de edição (velocidade, volume, espelhamento) e se deseja legendas + qual estilo
4. Clique em **🚀 Iniciar Fila**
5. Acompanhe o progresso pelos logs e pelos bips sonoros
6. Ao final, use **📂 Abrir Pasta** para acessar os vídeos gerados

### Testando legendas antes de processar tudo

Use o botão **🧪 Teste Legenda (10s)** para validar fonte, cor, posição e emojis num clipe curto de teste, sem esperar o pipeline completo rodar.

### Customizando as regras de curadoria

O botão **⚙️ Regras** abre um editor onde você pode reescrever os 4 prompts de curadoria (ou criar novos), e importar/exportar perfis diferentes por nicho de conteúdo (ex: `politica.json`, `saude.json`, `humor.json`).

---

## 🧠 Arquitetura do pipeline

```
URL do YouTube
      │
      ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌───────────────┐
│ Downloader  │ ─▶ │ Transcriber  │ ─▶ │ AI Curator  │ ─▶ │  Video Editor │
│  (yt-dlp)   │    │  (Whisper)   │    │  (Ollama)   │    │  (MoviePy)    │
└─────────────┘    └──────────────┘    └─────────────┘    └───────┬───────┘
                                                                    │
                                                                    ▼
                                                          ┌──────────────────┐
                                                          │ Subtitle Generator│
                                                          │  (legendas +      │
                                                          │   emojis)          │
                                                          └──────────────────┘
                                                                    │
                                                                    ▼
                                                             outputs/*.mp4
```

---

## 🛣️ Limitações conhecidas / Roadmap

- [ ] Suporte a outras plataformas de vídeo além do YouTube
- [ ] Interface de progresso mais granular (percentual por etapa)
- [ ] Suporte multi-idioma nas legendas (hoje otimizado para português)
- [ ] Testes automatizados (unitários/integração)
- [ ] Empacotamento como executável standalone (PyInstaller)

---

## 🛠️ Stack técnica

`Python` · `CustomTkinter` · `yt-dlp` · `OpenAI Whisper` · `Ollama` · `MoviePy` · `ImageMagick` · `FFmpeg`

---

## 📄 Licença

Distribuído sob a licença MIT. Veja [`LICENSE`](LICENSE) para mais detalhes.

---

## 👤 Autor

Desenvolvido por **Alexrecv** (também conhecido como **inoxsildet**) — especialista em infraestrutura de TI que utiliza Python e IA como ferramentas de automação.

[LinkedIn](https://www.linkedin.com/in/alexmdo/) · [GitHub](https://github.com/inoxsildet-arch)


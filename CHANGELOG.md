# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [Não lançado]

### Planejado
- Suporte a outras plataformas de vídeo além do YouTube
- Barra de progresso granular por etapa
- Empacotamento como executável standalone (PyInstaller)

## [1.0.0] - 2026-07-01

### Adicionado
- Pipeline completo: download → transcrição → curadoria por IA → edição → legendas
- Fila de processamento em lote (batch)
- Sistema de cache para download e transcrição (evita reprocessamento)
- Curadoria de conteúdo com 4 regras/personas customizáveis, importáveis/exportáveis em JSON
- Geração de dois formatos de corte: Shorts (vertical 9:16) e Cortes narrativos (horizontal)
- Edição automática: velocidade, volume, espelhamento e crop inteligente
- **Legendas dinâmicas conectadas ao pipeline de renderização**, com sincronismo de tempo
  ajustado automaticamente para a velocidade do vídeo
- 4 estilos de legenda: Formal, Divertida, Emoji Pop e Karaokê (palavra por palavra)
- Dicionário de emojis treinável (560+ palavras-chave pré-cadastradas nos temas
  motivacional, psicologia/psicanálise, religião e notícias)
- Tela de Configurações completa (API keys, endpoint do Ollama, prioridade de
  modelos, pasta de saída, parâmetros de edição) editável pela interface
- Tela de edição de aparência de legenda e dicionário de emojis
- Modo de Teste Rápido (10s) para validar legendas sem rodar o pipeline completo
- Feedback sonoro por etapa do processamento
- Opção de desligamento automático do PC ao final do lote
- Suporte a caminho customizado do ImageMagick (resolve problema comum de
  detecção automática no Windows)


import os
import json

class Config:
    # Arquivos de persistência
    RULES_FILE = os.path.join(os.path.dirname(__file__), "custom_rules.json")
    SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "app_settings.json")

    def __init__(self):
        self.curation_rules = self.load_rules()
        self.settings = self.load_settings()
        self._apply_settings()

    def _apply_settings(self):
        """Converte o dicionário de settings em atributos de instância
        (GEMINI_API_KEY, LOCAL_AI_URL, OUTPUT_DIR, etc.)."""
        self.GEMINI_API_KEY = self.settings.get("gemini_api_key", "")
        self.QWEN_API_KEY = self.settings.get("qwen_api_key", "")
        self.LOCAL_AI_URL = self.settings.get("local_ai_url", "http://localhost:11434/api/generate")
        self.AI_MODELS_PRIORITY = self.settings.get("ai_models_priority", ["gemma4"])

        self.BASE_M_PATH = self.settings.get("base_path", r"M:\videos auto")
        self.OUTPUT_DIR = os.path.join(self.BASE_M_PATH, "outputs")
        self.TEMP_DIR = os.path.join(self.BASE_M_PATH, "temp")

        self.SPEED_MULTIPLIER = self.settings.get("speed_multiplier", 1.3)
        self.VOLUME_ADJUST = self.settings.get("volume_adjust", -4.0)

    def load_rules(self):
        default_rules = {
            "VIRAL": {
                "name": "O Viral (Shorts)",
                "prompt": "Foco em ganchos rápidos, polêmicas, frases de impacto e momentos de alta energia para Shorts do YouTube."
            },
            "STORYTELLER": {
                "name": "O Storyteller (Cortes)",
                "prompt": "Foco em histórias completas, causos, experiências de vida e narrativas com início, meio e fim."
            },
            "ZEN": {
                "name": "O Motivacional (Zen)",
                "prompt": "Foco em lições de vida, meditação, reflexões profundas, espiritualidade e frases de sabedoria."
            },
            "ANALYST": {
                "name": "O Analista (Inteligente)",
                "prompt": "Foco em explicações técnicas, conceitos complexos simplificados, insights inteligentes e momentos de aprendizado."
            }
        }

        if os.path.exists(self.RULES_FILE):
            try:
                with open(self.RULES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default_rules
        return default_rules

    def save_rules(self, rules):
        self.curation_rules = rules
        with open(self.RULES_FILE, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=4, ensure_ascii=False)

    def load_settings(self):
        default_settings = {
            "sound_enabled": True,
            "window_geometry": "1000x800+100+100",
            "sound_files": {
                "start": "start.wav",
                "finish": "finish.wav",
                "shutdown": "shutdown.wav"
            },
            # ---- Configurações de IA ----
            "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
            "qwen_api_key": os.getenv("QWEN_API_KEY", ""),
            "local_ai_url": "http://localhost:11434/api/generate",
            "ai_models_priority": ["gemma4"],
            # ---- Pastas ----
            "base_path": r"M:\videos auto",
            # ---- Edição de vídeo ----
            "speed_multiplier": 1.3,
            "volume_adjust": -4.0,
            # ---- Legendas ----
            "subtitle_font": "Impact",
            "subtitle_size": 80,
            "subtitle_color": "yellow",
            "subtitle_outline_color": "black",
            "subtitle_pos_y": 0.75,
            "subtitle_style": "Divertida",
            "subtitle_enabled": True,
            "imagemagick_path": "",
            "emoji_dictionary": {
                "dinheiro": "💰",
                "sucesso": "🚀",
                "trabalho": "💼",
                "amor": "❤️",
                "casamento": "💍",
                "fogo": "🔥"
            },
        }
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                # Mescla: mantém defaults para chaves novas que ainda não existem
                # no arquivo salvo (evita erro ao atualizar o app).
                merged = default_settings.copy()
                merged.update(loaded)
                return merged
            except:
                return default_settings
        return default_settings

    def save_settings(self, settings=None):
        if settings:
            self.settings = settings
        with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)
        # Recalcula os atributos (OUTPUT_DIR, LOCAL_AI_URL etc.) com os novos valores
        self._apply_settings()

    # Regras Locais Gerais (Mantidas para compatibilidade)
    LOCAL_RULES = """
    1. Priorize histórias de vida e vivências pessoais.
    2. Identifique frases motivacionais e lições de superação.
    3. Busque ganchos de impacto nos primeiros 3 segundos.
    4. IGNORE: Propagandas (Insider, etc), cupons, links na descrição, apresentações iniciais e despedidas.
    """

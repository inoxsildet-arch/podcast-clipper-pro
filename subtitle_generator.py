import os
from moviepy import TextClip, CompositeVideoClip, ColorClip
import re

class SubtitleGenerator:
    def __init__(self, config):
        self.config = config
        self.emoji_map = self.config.settings.get("emoji_dictionary", {
            "dinheiro": "💰", "sucesso": "🚀", "trabalho": "💼",
            "amor": "❤️", "casamento": "💍", "fogo": "🔥"
        })

        # Configura o caminho do ImageMagick, se o usuário informou um caminho
        # explícito nas Configurações (Legendas & Emojis). Sem isso, o MoviePy
        # tenta auto-detectar, mas em muitas instalações Windows falha e o
        # TextClip não consegue renderizar o texto.
        imagemagick_path = self.config.settings.get("imagemagick_path", "")
        if imagemagick_path and os.path.exists(imagemagick_path):
            try:
                from moviepy.config import change_settings
                change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})
            except Exception as e:
                print(f"Aviso: não foi possível aplicar o caminho do ImageMagick via change_settings ({e}). "
                      f"Tentando via variável de ambiente.")
                os.environ["IMAGEMAGICK_BINARY"] = imagemagick_path

    def _get_font_path(self, font_name):
        if os.name == 'nt':
            clean_name = font_name.lower().replace(".ttf", "").replace(".otf", "")
            common_paths = [
                f"C:\\Windows\\Fonts\\{clean_name}.ttf",
                f"C:\\Windows\\Fonts\\{font_name}",
                f"C:\\Windows\\Fonts\\{clean_name}bd.ttf",
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return path
        return font_name

    def _add_emojis(self, text):
        words = text.lower().split()
        new_text = text
        for word, emoji in self.emoji_map.items():
            if word in words:
                new_text += f" {emoji}"
                break
        return new_text

    def generate_subtitles(self, video_clip, segments, style_name="Divertida"):
        video_w, video_h = video_clip.size
        user_font = self.config.settings.get("subtitle_font", "Impact")
        font_path = self._get_font_path(user_font)
        user_fontsize = self.config.settings.get("subtitle_size", 80)
        user_color = self.config.settings.get("subtitle_color", "yellow")
        user_outline_color = self.config.settings.get("subtitle_outline_color", "black")
        user_pos_y = self.config.settings.get("subtitle_pos_y", 0.75)
        subtitle_clips = []

        for seg in segments:
            duration = seg['end'] - seg['start']
            if duration <= 0: continue
            full_text = seg['text'].strip().upper()
            if style_name == "Emoji Pop":
                full_text = self._add_emojis(full_text)

            if style_name in ["Karaokê", "Divertida", "Emoji Pop"]:
                words = full_text.split()
                num_words = len(words)
                if num_words == 0: continue
                word_duration = duration / num_words
                for i, word in enumerate(words):
                    word_start = seg['start'] + (i * word_duration)
                    try:
                        shadow = TextClip(
                            text=full_text, font=font_path, font_size=user_fontsize,
                            color=user_outline_color, method="caption",
                            size=(video_w * 0.85, None), text_align="center"
                        ).with_start(word_start).with_duration(word_duration).with_position(('center', video_h * user_pos_y + 4))
                        main_phrase = TextClip(
                            text=full_text, font=font_path, font_size=user_fontsize,
                            color="white", stroke_color=user_outline_color, stroke_width=1,
                            method="caption", size=(video_w * 0.8, None), text_align="center"
                        ).with_start(word_start).with_duration(word_duration).with_position(('center', video_h * user_pos_y))
                        highlight = TextClip(
                            text=word, font=font_path, font_size=int(user_fontsize * 1.2),
                            color=user_color, stroke_color=user_outline_color, stroke_width=2,
                            method="caption", size=(video_w * 0.8, None), text_align="center"
                        ).with_start(word_start).with_duration(word_duration).with_position(('center', video_h * user_pos_y - 5))
                        subtitle_clips.extend([shadow, main_phrase, highlight])
                    except Exception as e: print(f"Erro: {e}")
            else:
                try:
                    txt_clip = TextClip(
                        text=full_text, font=font_path, font_size=user_fontsize,
                        color="white", stroke_color="black", stroke_width=1,
                        method="caption", size=(video_w * 0.8, None), text_align="center"
                    ).with_start(seg['start']).with_duration(duration).with_position(('center', video_h * user_pos_y))
                    subtitle_clips.append(txt_clip)
                except Exception as e: print(f"Erro: {e}")
        return subtitle_clips

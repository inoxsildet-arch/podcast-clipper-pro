import whisper
import os
import json

class Transcriber:
    def __init__(self, model_name="base"):
        self.model = whisper.load_model(model_name)

    def transcribe(self, video_path):
        # MELHORIA: Verificar se já existe transcrição salva para este vídeo no temp
        cache_path = video_path.replace("_original.mp4", "_transcription.json")
        if os.path.exists(cache_path):
            print(f"Transcrição encontrada em cache: {cache_path}")
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                print("Erro ao ler cache, transcrevendo novamente...")

        # Se não houver cache, transcreve
        result = self.model.transcribe(video_path, verbose=False)
        segments = result['segments']

        # Salva no cache para agilizar testes futuros
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(segments, f, indent=4, ensure_ascii=False)
            print(f"Transcrição salva em: {cache_path}")
        except Exception as e:
            print(f"Erro ao salvar cache de transcrição: {e}")

        return segments

    def format_segments_for_ai(self, segments):
        formatted_text = ""
        for seg in segments:
            start = round(seg['start'], 2)
            end = round(seg['end'], 2)
            text = seg['text'].strip()
            formatted_text += f"[{start}s - {end}s]: {text}\n"
        return formatted_text

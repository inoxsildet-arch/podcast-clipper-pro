import os
import sys
import time
import threading
import traceback
import gc
import shutil
import re
import subprocess
import winsound
from datetime import datetime
from config import Config
from downloader import Downloader
from transcriber import Transcriber
from ai_curator import AICurator
from video_editor import VideoEditor

class PodcastClipperApp:
    def __init__(self):
        self.config = Config()
        self.stop_requested = False
        self.is_running = False
        self.current_output_dir = None
        self.queue = []
        
        try:
            os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
            os.makedirs(self.config.TEMP_DIR, exist_ok=True)
        except Exception as e:
            print(f"Aviso: Não foi possível criar diretórios: {e}")

    def play_sound(self, sound_type):
        """Toca sons baseados no tipo de evento se estiver habilitado."""
        if not self.config.settings.get("sound_enabled", True):
            return
        try:
            if sound_type == "start": winsound.Beep(1000, 500)
            elif sound_type == "step": winsound.Beep(800, 200)
            elif sound_type == "clip": winsound.Beep(1200, 100)
            elif sound_type == "finish":
                winsound.Beep(1000, 200); winsound.Beep(1200, 200); winsound.Beep(1500, 400)
            elif sound_type == "shutdown":
                for _ in range(3): winsound.Beep(600, 300); time.sleep(0.1)
        except: pass

    def sanitize_title(self, title, max_words=6):
        clean = re.sub(r'[^\w\s-]', '', title).strip()
        clean = re.sub(r'[\s-]+', '_', clean)
        words = clean.split('_')
        return "_".join(words[:max_words]) + "..." if len(words) > max_words else clean

    def run_batch(self, video_list, mode, speed, volume, mirror, shutdown, status_callback=None,
                  apply_subtitles=False, subtitle_style="Divertida"):
        self.is_running = True
        self.stop_requested = False
        self.play_sound("start")
        
        for i, video_info in enumerate(video_list):
            if self.stop_requested: break
            if status_callback: status_callback(f"--- Processando Vídeo {i+1}/{len(video_list)} ---")
            self._process_single_video(video_info['url'], video_info.get('start', 0), video_info.get('end', 0), 
                                     mode, speed, volume, mirror, status_callback,
                                     apply_subtitles=apply_subtitles, subtitle_style=subtitle_style)
            
        self.is_running = False
        self.play_sound("finish")
        if status_callback: status_callback("Fila finalizada.")
            
        if shutdown and not self.stop_requested:
            self.play_sound("shutdown")
            if status_callback: status_callback("Desligamento em 10 minutos.")
            os.system('shutdown /s /t 600') if os.name == 'nt' else os.system('sudo shutdown -h +10')

    def _process_single_video(self, url, start, end, mode, speed, volume, mirror, status_callback,
                              apply_subtitles=False, subtitle_style="Divertida"):
        def update_status(msg):
            if status_callback: status_callback(msg)

        try:
            # 1. Download (Com reaproveitamento)
            self.play_sound("step")
            downloader = Downloader(self.config.TEMP_DIR)
            video_title = downloader.get_video_info(url)
            short_title = self.sanitize_title(video_title)
            update_status(f"Etapa 1/4: Obtendo vídeo...")
            video_temp_path, _ = downloader.download_video(url, start, end)
            
            # Pasta de Saída
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            status_suffix = "FU" if start == 0 and end == 0 else f"PA_{int(start)}-{int(end)}"
            self.current_output_dir = os.path.join(self.config.OUTPUT_DIR, f"{short_title}_{status_suffix}_{timestamp}")
            os.makedirs(self.current_output_dir, exist_ok=True)
            
            # 2. Transcrição (Com cache)
            if self.stop_requested: return
            self.play_sound("step")
            update_status("Etapa 2/4: Transcrevendo áudio...")
            transcriber = Transcriber()
            segments = transcriber.transcribe(video_temp_path)
            
            # 3. Curadoria IA
            if self.stop_requested: return
            self.play_sound("step")
            update_status("Etapa 3/4: IA analisando conteúdo...")
            curator = AICurator(self.config)
            curator._set_log_paths(self.current_output_dir)
            analysis = curator.analyze_transcription(segments, callback=update_status)
            
            # 4. Renderização
            if self.stop_requested: return
            editor = VideoEditor(self.config)
            
            # Shorts
            for i, item in enumerate(analysis.get("shorts", [])):
                if self.stop_requested: break
                update_status(f"Renderizando Short {i+1}/{len(analysis['shorts'])}...")
                name = f"short_{i+1}.mp4"
                editor.process_clip(video_temp_path, item['start'], item['end'], name, 
                                   is_shorts=(mode == "shorts"), apply_speed=speed, 
                                   apply_volume=volume, apply_mirror=mirror, output_dir=self.current_output_dir,
                                   apply_subtitles=apply_subtitles, subtitle_style=subtitle_style, segments=segments)
                self.play_sound("clip")
                
            # Cortes
            for i, item in enumerate(analysis.get("cuts", [])):
                if self.stop_requested: break
                update_status(f"Renderizando Corte {i+1}/{len(analysis['cuts'])}...")
                name = f"corte_{i+1}.mp4"
                editor.process_clip(video_temp_path, item['start'], item['end'], name, 
                                   is_shorts=False, apply_speed=speed, 
                                   apply_volume=volume, apply_mirror=mirror, output_dir=self.current_output_dir,
                                   apply_subtitles=apply_subtitles, subtitle_style=subtitle_style, segments=segments)
                self.play_sound("clip")
            
            update_status(f"Concluído: {short_title}")

        except Exception as e:
            update_status(f"Erro: {str(e)}")
            print(traceback.format_exc())

    def quick_subtitle_test(self, video_path, subtitle_style="Divertida", status_callback=None):
        """MODO DE TESTE RÁPIDO: renderiza só os primeiros 10s de um vídeo já existente
        na pasta temp, com a legenda aplicada, para validar fonte/cor/posição/emoji
        antes de rodar um processamento longo."""
        def update_status(msg):
            if status_callback: status_callback(msg)

        try:
            from moviepy import VideoFileClip

            if not video_path or not os.path.exists(video_path):
                update_status("❌ Teste: selecione um vídeo válido na pasta temp.")
                return None

            update_status("🧪 Teste Rápido: preparando clipe de 10s...")
            probe_clip = VideoFileClip(video_path)
            test_duration = min(10, probe_clip.duration)
            probe_clip.close()

            preview_dir = os.path.join(self.config.TEMP_DIR, "preview")
            os.makedirs(preview_dir, exist_ok=True)

            update_status("🧪 Transcrevendo os 10s de teste...")
            transcriber = Transcriber()
            # Usa o vídeo original (o Transcriber corta sozinho pelos segmentos por tempo,
            # mas aqui só precisamos dos segmentos que caem nos primeiros 10s).
            all_segments = transcriber.transcribe(video_path)
            segments_10s = [s for s in all_segments if s.get('start', 0) < test_duration]

            update_status("🧪 Renderizando legenda de teste...")
            editor = VideoEditor(self.config)
            output_dir = os.path.join(self.config.OUTPUT_DIR, "_teste_legenda")
            result_path = editor.process_clip(
                video_path, 0, test_duration, "preview_legenda.mp4",
                output_dir=output_dir,
                apply_subtitles=True, subtitle_style=subtitle_style,
                segments=segments_10s
            )

            if result_path and os.path.exists(result_path):
                update_status(f"✅ Teste pronto: {result_path}")
                if os.name == 'nt':
                    os.startfile(result_path)
                else:
                    subprocess.run(['xdg-open', result_path])
            else:
                update_status("❌ Teste: não foi possível gerar o clipe (verifique se há fala nos 10s iniciais).")
            return result_path

        except Exception as e:
            update_status(f"❌ Erro no Teste Rápido: {e}")
            print(traceback.format_exc())
            return None

    def stop_process(self): self.stop_requested = True
    def cancel_shutdown(self): 
        os.system('shutdown /a') if os.name == 'nt' else os.system('sudo shutdown -c')
        return "Desligamento cancelado."
    def clear_temp(self):
        try:
            shutil.rmtree(self.config.TEMP_DIR)
            os.makedirs(self.config.TEMP_DIR, exist_ok=True)
            return "Temp limpo."
        except: return "Erro ao limpar temp."
    def open_output_folder(self):
        folder = self.current_output_dir or self.config.OUTPUT_DIR
        if os.path.exists(folder):
            os.startfile(folder) if os.name == 'nt' else subprocess.run(['xdg-open', folder])
            return f"Abrindo: {folder}"
        return "Pasta não encontrada."

if __name__ == "__main__":
    import customtkinter as ctk
    from gui import PodcastClipperGUI
    app = PodcastClipperGUI()
    app.mainloop()

from moviepy import VideoFileClip, vfx, CompositeVideoClip
import os
from subtitle_generator import SubtitleGenerator

class VideoEditor:
    def __init__(self, config=None):
        self.config = config
        # Se não houver config, define valores padrão para evitar erros
        self.speed_multiplier = getattr(config, 'SPEED_MULTIPLIER', 1.3)
        self.volume_adjust = getattr(config, 'VOLUME_ADJUST', -4.0)
        self.subtitle_generator = SubtitleGenerator(config) if config else None

    def _preparar_segmentos_do_clipe(self, segments, clip_start, clip_end, speed_aplicada):
        """Filtra os segmentos da transcrição (que estão em tempo ABSOLUTO do vídeo
        original) e converte para tempo RELATIVO ao início do clipe cortado (0 = início
        do clipe). Se a velocidade foi alterada, também escala os tempos para manter
        a legenda sincronizada com o vídeo acelerado/desacelerado."""
        if not segments:
            return []

        fator_velocidade = self.speed_multiplier if speed_aplicada else 1.0
        resultado = []
        for seg in segments:
            s_start = seg.get('start', 0)
            s_end = seg.get('end', 0)

            # Ignora segmentos totalmente fora do intervalo do clipe
            if s_end <= clip_start or s_start >= clip_end:
                continue

            rel_start = max(0, s_start - clip_start) / fator_velocidade
            rel_end = max(0, min(s_end, clip_end) - clip_start) / fator_velocidade

            if rel_end <= rel_start:
                continue

            resultado.append({
                'start': rel_start,
                'end': rel_end,
                'text': seg.get('text', '')
            })
        return resultado

    def process_clip(self, input_path, start, end, output_name, output_dir=None, is_shorts=False, 
                     apply_speed=False, apply_volume=False, apply_mirror=False,
                     apply_subtitles=False, subtitle_style="Divertida", segments=None):
        """
        Processa um clipe de vídeo com opções de corte, velocidade, volume, espelhamento
        e legendas dinâmicas.
        output_dir: Pasta onde o arquivo será salvo. Se None, usa o padrão do config.
        segments: lista de segmentos da transcrição (tempo absoluto no vídeo original),
                  necessária apenas se apply_subtitles=True.
        """
        # Define o caminho final de saída
        target_dir = output_dir if output_dir else self.config.OUTPUT_DIR
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        # Garante que o nome tenha extensão .mp4
        if not output_name.endswith(".mp4"):
            output_name += ".mp4"
            
        output_path = os.path.join(target_dir, output_name)
        
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except Exception as e:
                print(f"Aviso: Não foi possível remover arquivo de saída antigo: {e}")

        full_clip = VideoFileClip(input_path)
        video_duration = full_clip.duration
        
        # Garante que o fim não ultrapasse a duração do vídeo
        end_with_margin = min(end + 1.0, video_duration)
        if end_with_margin <= start:
            print(f"Aviso: Tempo de clipe inválido ({start}s a {end_with_margin}s). Pulando.")
            full_clip.close()
            return None
            
        clip = full_clip.subclipped(start, end_with_margin)
        
        # 1. Formato Vertical (Shorts)
        if is_shorts:
            w, h = clip.size
            target_ratio = 9/16
            target_w = h * target_ratio
            x_center = w / 2
            x1 = max(0, x_center - target_w / 2)
            x2 = min(w, x_center + target_w / 2)
            clip = clip.cropped(x1=x1, y1=0, x2=x2, y2=h)
            clip = clip.resized(height=1920)
        
        # 2. Aceleração Independente
        if apply_speed:
            clip = clip.with_effects([vfx.MultiplySpeed(self.speed_multiplier)])
            
        # 3. Volume Independente
        if apply_volume:
            vol_factor = 10**(self.volume_adjust / 20)
            clip = clip.with_volume_scaled(vol_factor)
            
        # 4. Espelhamento Independente
        if apply_mirror:
            clip = clip.with_effects([vfx.MirrorX()])

        # 5. Legendas Dinâmicas (por último: usa o tamanho/duração já finais do clipe)
        if apply_subtitles and segments and self.subtitle_generator:
            clip_segments = self._preparar_segmentos_do_clipe(segments, start, end_with_margin, apply_speed)
            if clip_segments:
                try:
                    subtitle_clips = self.subtitle_generator.generate_subtitles(
                        clip, clip_segments, style_name=subtitle_style
                    )
                    if subtitle_clips:
                        clip = CompositeVideoClip([clip] + subtitle_clips)
                except Exception as e:
                    print(f"Aviso: Falha ao gerar legendas ({e}). Renderizando sem legenda.")

        # Renderização
        clip.write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac", 
            temp_audiofile=os.path.join(target_dir, f'temp-audio-{output_name}.m4a'), 
            remove_temp=True, 
            logger=None
        )
        
        clip.close()
        full_clip.close()
        return output_path

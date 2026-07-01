import yt_dlp
import os
import re

class Downloader:
    def __init__(self, temp_dir="temp"):
        self.temp_dir = temp_dir
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

    def get_video_info(self, url):
        """Extrai o título do vídeo para usar no nome da pasta."""
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video_sem_nome')
            # Limpar caracteres inválidos para nomes de pasta no Windows/Linux
            title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")
            return title

    def download_video(self, url, start_time=None, end_time=None):
        title = self.get_video_info(url)
        # Se houver recorte de tempo, o nome do arquivo deve refletir isso para evitar conflitos
        suffix = f"_{start_time}_{end_time}" if start_time or end_time else ""
        output_path = os.path.join(self.temp_dir, f"{title}{suffix}_original.mp4")
        
        # MELHORIA: Se o arquivo já existe, não baixa de novo
        if os.path.exists(output_path):
            print(f"Vídeo já encontrado em {output_path}. Pulando download.")
            return output_path, title

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'overwrites': True,
        }
        
        if start_time and end_time and end_time > start_time:
            ydl_opts['external_downloader'] = 'ffmpeg'
            ydl_opts['external_downloader_args'] = ['-ss', str(start_time), '-to', str(end_time)]
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        return output_path, title

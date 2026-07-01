import customtkinter as ctk
import threading
import os
import json
from tkinter import filedialog
from datetime import datetime
from main import PodcastClipperApp

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

ESTILOS_LEGENDA = ["Formal", "Divertida", "Emoji Pop", "Karaokê"]

class PodcastClipperGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.app_logic = PodcastClipperApp()
        
        self.title("🎙️ Podcast Clipper PRO")
        
        # MELHORIA: Lembrar posição e tamanho da janela
        geometry = self.app_logic.config.settings.get("window_geometry", "850x650+100+100")
        try:
            self.geometry(geometry)
        except:
            self.geometry("850x650")
            
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configuração de Grid Responsivo
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="🎙️ CLIPPER PRO", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))
        
        self.btn_start = ctk.CTkButton(self.sidebar, text="🚀 Iniciar Fila", fg_color="#28a745", command=self.start_batch)
        self.btn_start.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        
        self.btn_stop = ctk.CTkButton(self.sidebar, text="🛑 Parar Tudo", fg_color="#dc3545", command=self.stop_process)
        self.btn_stop.grid(row=2, column=0, padx=15, pady=5, sticky="ew")
        
        self.btn_rules = ctk.CTkButton(self.sidebar, text="⚙️ Regras", fg_color="#6f42c1", command=self.open_rules_editor)
        self.btn_rules.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        self.btn_settings = ctk.CTkButton(self.sidebar, text="🛠️ Configurações", fg_color="#495057", command=self.open_settings_editor)
        self.btn_settings.grid(row=4, column=0, padx=15, pady=5, sticky="ew")

        self.btn_subtitles = ctk.CTkButton(self.sidebar, text="🎨 Legendas & Emojis", fg_color="#d63384", command=self.open_subtitle_editor)
        self.btn_subtitles.grid(row=5, column=0, padx=15, pady=5, sticky="ew")

        self.btn_quick_test = ctk.CTkButton(self.sidebar, text="🧪 Teste Legenda (10s)", fg_color="#fd7e14", command=self.run_quick_test)
        self.btn_quick_test.grid(row=6, column=0, padx=15, pady=5, sticky="ew")
        
        self.btn_open_folder = ctk.CTkButton(self.sidebar, text="📂 Abrir Pasta", fg_color="#17a2b8", command=self.open_folder)
        self.btn_open_folder.grid(row=7, column=0, padx=15, pady=5, sticky="ew")
        
        self.btn_clear_temp = ctk.CTkButton(self.sidebar, text="🧹 Limpar Temp", fg_color="#6c757d", command=self.clear_temp)
        self.btn_clear_temp.grid(row=8, column=0, padx=15, pady=5, sticky="ew")
        
        self.btn_cancel_shutdown = ctk.CTkButton(self.sidebar, text="⏰ Cancelar Desligar", fg_color="#ffc107", text_color="black", command=self.cancel_shutdown)
        self.btn_cancel_shutdown.grid(row=9, column=0, padx=15, pady=5, sticky="ew")

        # MELHORIA: Controle de Som
        self.sound_var = ctk.BooleanVar(value=self.app_logic.config.settings.get("sound_enabled", True))
        self.check_sound = ctk.CTkCheckBox(self.sidebar, text="Sons Ativos", variable=self.sound_var, command=self.toggle_sound)
        self.check_sound.grid(row=10, column=0, padx=15, pady=20, sticky="ew")
        
        # Main Content
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)
        
        # Batch Input
        self.batch_label = ctk.CTkLabel(self.main_frame, text="Fila de Vídeos (URL, início, fim):", font=ctk.CTkFont(weight="bold"))
        self.batch_label.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")
        
        self.batch_text = ctk.CTkTextbox(self.main_frame, height=120)
        self.batch_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        if self.batch_text.get("1.0", "end-1c").strip() == "":
            self.batch_text.insert("1.0", "https://youtube.com/watch?v=exemplo, 0, 0")
        
        # Options Frame
        self.options_frame = ctk.CTkFrame(self.main_frame)
        self.options_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.mode_var = ctk.StringVar(value="shorts")
        self.mode_menu = ctk.CTkOptionMenu(self.options_frame, values=["normal", "shorts"], variable=self.mode_var, width=120)
        self.mode_menu.grid(row=0, column=0, padx=10, pady=10)
        
        self.check_speed = ctk.CTkCheckBox(self.options_frame, text="1.3x")
        self.check_speed.grid(row=0, column=1, padx=10, pady=10)
        self.check_speed.select()
        
        self.check_volume = ctk.CTkCheckBox(self.options_frame, text="-4dB")
        self.check_volume.grid(row=0, column=2, padx=10, pady=10)
        self.check_volume.select()
        
        self.check_mirror = ctk.CTkCheckBox(self.options_frame, text="Espelhar")
        self.check_mirror.grid(row=0, column=3, padx=10, pady=10)
        
        self.check_shutdown = ctk.CTkCheckBox(self.options_frame, text="Desligar PC")
        self.check_shutdown.grid(row=0, column=4, padx=10, pady=10)

        # NOVO: Linha de Legendas
        subtitle_default_on = self.app_logic.config.settings.get("subtitle_enabled", True)
        self.check_subtitles_var = ctk.BooleanVar(value=subtitle_default_on)
        self.check_subtitles = ctk.CTkCheckBox(self.options_frame, text="Legendas", variable=self.check_subtitles_var)
        self.check_subtitles.grid(row=1, column=0, padx=10, pady=(0, 10))

        estilo_default = self.app_logic.config.settings.get("subtitle_style", "Divertida")
        self.subtitle_style_var = ctk.StringVar(value=estilo_default)
        self.subtitle_style_menu = ctk.CTkOptionMenu(self.options_frame, values=ESTILOS_LEGENDA, variable=self.subtitle_style_var, width=140)
        self.subtitle_style_menu.grid(row=1, column=1, columnspan=2, padx=10, pady=(0, 10), sticky="w")
        
        # Log Area
        self.log_text = ctk.CTkTextbox(self.main_frame, font=("Consolas", 11), fg_color="#1e1e1e")
        self.log_text.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.log_text.configure(state="disabled")

    def toggle_sound(self):
        self.app_logic.config.settings["sound_enabled"] = self.sound_var.get()
        self.app_logic.config.save_settings()

    def update_log(self, message):
        self.log_text.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{ts}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def start_batch(self):
        raw_input = self.batch_text.get("1.0", "end-1c").strip()
        if not raw_input: return
            
        video_list = []
        for line in raw_input.split('\n'):
            if not line.strip(): continue
            parts = [p.strip() for p in line.split(',')]
            if parts:
                url = parts[0]
                try:
                    start = float(parts[1]) if len(parts) > 1 else 0
                    end = float(parts[2]) if len(parts) > 2 else 0
                except: start, end = 0, 0
                video_list.append({'url': url, 'start': start, 'end': end})
        
        self.btn_start.configure(state="disabled")
        threading.Thread(target=self.run_thread, args=(video_list,), daemon=True).start()

    def run_thread(self, video_list):
        self.app_logic.run_batch(
            video_list, self.mode_var.get(), 
            self.check_speed.get(), self.check_volume.get(), self.check_mirror.get(), 
            self.check_shutdown.get(), self.update_log,
            apply_subtitles=self.check_subtitles_var.get(),
            subtitle_style=self.subtitle_style_var.get()
        )
        self.btn_start.configure(state="normal")

    def run_quick_test(self):
        """Abre um seletor de arquivo na pasta temp e roda o Modo de Teste Rápido (10s)."""
        temp_dir = self.app_logic.config.TEMP_DIR
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)

        video_path = filedialog.askopenfilename(
            title="Selecione um vídeo da pasta temp para testar a legenda",
            initialdir=temp_dir,
            filetypes=[("Vídeos", "*.mp4 *.mkv *.mov"), ("Todos os arquivos", "*.*")]
        )
        if not video_path:
            return

        estilo = self.subtitle_style_var.get()
        self.btn_quick_test.configure(state="disabled")

        def worker():
            self.app_logic.quick_subtitle_test(video_path, subtitle_style=estilo, status_callback=self.update_log)
            self.btn_quick_test.configure(state="normal")

        threading.Thread(target=worker, daemon=True).start()

    def open_rules_editor(self):
        editor = ctk.CTkToplevel(self)
        editor.title("Editor de Regras")
        editor.geometry("600x600")
        editor.attributes("-topmost", True)
        
        # Frame para botões de Importar/Exportar no topo
        top_actions = ctk.CTkFrame(editor)
        top_actions.pack(fill="x", padx=10, pady=5)
        
        scroll = ctk.CTkScrollableFrame(editor)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.rule_entries = {}

        def refresh_list():
            for widget in scroll.winfo_children():
                widget.destroy()
            self.rule_entries = {}
            for key, rule in self.app_logic.config.curation_rules.items():
                frame = ctk.CTkFrame(scroll)
                frame.pack(fill="x", pady=5, padx=5)
                ctk.CTkLabel(frame, text=f"ID: {key}", font=("Arial", 10, "italic")).pack(anchor="w")
                name_entry = ctk.CTkEntry(frame); name_entry.insert(0, rule['name']); name_entry.pack(fill="x", padx=5)
                prompt_entry = ctk.CTkTextbox(frame, height=70); prompt_entry.insert("1.0", rule['prompt']); prompt_entry.pack(fill="x", padx=5)
                self.rule_entries[key] = (name_entry, prompt_entry)

        def add_new_rule():
            new_id = f"RULE_{len(self.rule_entries) + 1}"
            frame = ctk.CTkFrame(scroll); frame.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(frame, text=f"ID: {new_id}", font=("Arial", 10, "italic")).pack(anchor="w")
            name_entry = ctk.CTkEntry(frame, placeholder_text="Nome da Regra"); name_entry.pack(fill="x", padx=5)
            prompt_entry = ctk.CTkTextbox(frame, height=70, placeholder_text="Prompt da Regra"); prompt_entry.pack(fill="x", padx=5)
            self.rule_entries[new_id] = (name_entry, prompt_entry)

        def save():
            new_rules = {}
            for k, (n, p) in self.rule_entries.items():
                nv, pv = n.get().strip(), p.get("1.0", "end-1c").strip()
                if nv and pv: new_rules[k] = {"name": nv, "prompt": pv}
            self.app_logic.config.save_rules(new_rules)
            self.update_log("Regras salvas com sucesso!")
            editor.destroy()

        def export_rules():
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if file_path:
                current_rules = {}
                for k, (n, p) in self.rule_entries.items():
                    nv, pv = n.get().strip(), p.get("1.0", "end-1c").strip()
                    if nv and pv: current_rules[k] = {"name": nv, "prompt": pv}
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(current_rules, f, indent=4, ensure_ascii=False)
                self.update_log(f"Regras exportadas para: {os.path.basename(file_path)}")

        def import_rules():
            file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        imported = json.load(f)
                    self.app_logic.config.save_rules(imported)
                    refresh_list()
                    self.update_log(f"Regras importadas de: {os.path.basename(file_path)}")
                except Exception as e:
                    self.update_log(f"Erro ao importar: {e}")

        # Botões de Ação no Topo
        ctk.CTkButton(top_actions, text="📥 Importar Regras", command=import_rules, fg_color="gray").pack(side="left", padx=5, expand=True)
        ctk.CTkButton(top_actions, text="📤 Exportar Regras", command=export_rules, fg_color="gray").pack(side="left", padx=5, expand=True)

        # Botões de Ação no Rodapé
        footer = ctk.CTkFrame(editor)
        footer.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(footer, text="+ Nova Regra", command=add_new_rule).pack(side="left", padx=5, expand=True)
        ctk.CTkButton(footer, text="SALVAR E APLICAR", fg_color="green", command=save).pack(side="left", padx=5, expand=True)

        refresh_list()

    def open_settings_editor(self):
        """Tela: Configurações gerais (API keys, Ollama, pasta de saída, edição de vídeo)."""
        cfg = self.app_logic.config
        s = cfg.settings

        editor = ctk.CTkToplevel(self)
        editor.title("Configurações")
        editor.geometry("520x620")
        editor.attributes("-topmost", True)

        scroll = ctk.CTkScrollableFrame(editor)
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        def add_section_title(text):
            ctk.CTkLabel(scroll, text=text, font=ctk.CTkFont(size=14, weight="bold")).pack(
                anchor="w", pady=(15, 5))

        def add_entry(label_text, value, show=None):
            ctk.CTkLabel(scroll, text=label_text, font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(5, 2))
            entry = ctk.CTkEntry(scroll, show=show)
            entry.insert(0, str(value))
            entry.pack(fill="x", pady=(0, 5))
            return entry

        # ---- Seção: IA / API Keys ----
        add_section_title("🤖 Inteligência Artificial")

        entry_gemini = add_entry("Gemini API Key:", s.get("gemini_api_key", ""), show="*")
        entry_qwen = add_entry("Qwen API Key:", s.get("qwen_api_key", ""), show="*")
        entry_ollama_url = add_entry("Endereço do Ollama (local):", s.get("local_ai_url", "http://localhost:11434/api/generate"))

        modelos_atual = ", ".join(s.get("ai_models_priority", ["gemma4"]))
        entry_modelos = add_entry("Modelos de IA (em ordem de prioridade, separados por vírgula):", modelos_atual)

        # ---- Seção: Pastas ----
        add_section_title("📁 Pasta de Saída")

        pasta_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        pasta_frame.pack(fill="x", pady=(5, 5))
        entry_pasta = ctk.CTkEntry(pasta_frame)
        entry_pasta.insert(0, s.get("base_path", r"M:\videos auto"))
        entry_pasta.pack(side="left", fill="x", expand=True, padx=(0, 5))

        def escolher_pasta():
            caminho = filedialog.askdirectory()
            if caminho:
                entry_pasta.delete(0, "end")
                entry_pasta.insert(0, caminho)

        ctk.CTkButton(pasta_frame, text="Procurar...", width=90, command=escolher_pasta).pack(side="right")

        # ---- Seção: Edição de vídeo ----
        add_section_title("🎬 Edição de Vídeo")

        entry_speed = add_entry("Multiplicador de Velocidade (ex: 1.3):", s.get("speed_multiplier", 1.3))
        entry_volume = add_entry("Ajuste de Volume em dB (ex: -4.0):", s.get("volume_adjust", -4.0))

        status_label = ctk.CTkLabel(scroll, text="", text_color="#28a745")
        status_label.pack(pady=(10, 0))

        def salvar():
            try:
                novos_modelos = [m.strip() for m in entry_modelos.get().split(",") if m.strip()]
                if not novos_modelos:
                    novos_modelos = ["gemma4"]

                novo_speed = float(entry_speed.get().replace(",", "."))
                novo_volume = float(entry_volume.get().replace(",", "."))

                s["gemini_api_key"] = entry_gemini.get().strip()
                s["qwen_api_key"] = entry_qwen.get().strip()
                s["local_ai_url"] = entry_ollama_url.get().strip()
                s["ai_models_priority"] = novos_modelos
                s["base_path"] = entry_pasta.get().strip()
                s["speed_multiplier"] = novo_speed
                s["volume_adjust"] = novo_volume

                cfg.save_settings(s)  # já recalcula OUTPUT_DIR/TEMP_DIR/etc internamente

                status_label.configure(text="✅ Configurações salvas com sucesso!")
                self.update_log("Configurações atualizadas.")
            except ValueError:
                status_label.configure(text="❌ Velocidade e Volume precisam ser números (ex: 1.3 / -4.0)", text_color="#dc3545")
            except Exception as e:
                status_label.configure(text=f"❌ Erro ao salvar: {e}", text_color="#dc3545")

        ctk.CTkButton(scroll, text="SALVAR CONFIGURAÇÕES", fg_color="green", command=salvar).pack(
            fill="x", pady=(15, 5))

    def open_subtitle_editor(self):
        """NOVA TELA: Aparência das legendas + Dicionário de Emojis treinável."""
        cfg = self.app_logic.config
        s = cfg.settings

        editor = ctk.CTkToplevel(self)
        editor.title("Legendas & Emojis")
        editor.geometry("560x680")
        editor.attributes("-topmost", True)

        scroll = ctk.CTkScrollableFrame(editor)
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(scroll, text="🎨 Aparência da Legenda", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", pady=(0, 10))

        def add_entry(label_text, value):
            ctk.CTkLabel(scroll, text=label_text, font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(5, 2))
            entry = ctk.CTkEntry(scroll)
            entry.insert(0, str(value))
            entry.pack(fill="x", pady=(0, 5))
            return entry

        entry_font = add_entry("Fonte (nome do arquivo .ttf ou nome do sistema, ex: Impact):", s.get("subtitle_font", "Impact"))
        entry_size = add_entry("Tamanho da fonte (px):", s.get("subtitle_size", 80))
        entry_color = add_entry("Cor do texto (nome ou #hex, ex: yellow):", s.get("subtitle_color", "yellow"))
        entry_outline = add_entry("Cor do contorno (nome ou #hex, ex: black):", s.get("subtitle_outline_color", "black"))
        entry_pos_y = add_entry("Posição vertical (0.0 topo — 1.0 rodapé, ex: 0.75):", s.get("subtitle_pos_y", 0.75))

        # ---- ImageMagick ----
        ctk.CTkLabel(scroll, text="Caminho do ImageMagick (magick.exe):", font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(5, 2))
        magick_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        magick_frame.pack(fill="x", pady=(0, 5))
        entry_magick = ctk.CTkEntry(magick_frame)
        entry_magick.insert(0, s.get("imagemagick_path", ""))
        entry_magick.pack(side="left", fill="x", expand=True, padx=(0, 5))

        def escolher_magick():
            caminho = filedialog.askopenfilename(
                title="Selecione o magick.exe",
                filetypes=[("Executável", "*.exe"), ("Todos os arquivos", "*.*")]
            )
            if caminho:
                entry_magick.delete(0, "end")
                entry_magick.insert(0, caminho)

        ctk.CTkButton(magick_frame, text="Procurar...", width=90, command=escolher_magick).pack(side="right")
        ctk.CTkLabel(
            scroll,
            text="Necessário para renderizar as legendas. Deixe em branco se o MoviePy\nencontrar o ImageMagick sozinho (auto-detecção).",
            font=ctk.CTkFont(size=10), text_color="#9ca3af", justify="left"
        ).pack(anchor="w", pady=(0, 10))

        # ---- Dicionário de Emojis ----
        ctk.CTkLabel(scroll, text="😀 Dicionário de Emojis (palavra → emoji)", font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", pady=(20, 10))

        emoji_dict_atual = s.get("emoji_dictionary", {})
        linhas_emoji = []  # lista de (frame, entry_palavra, entry_emoji)
        emoji_rows_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        emoji_rows_frame.pack(fill="x")

        def add_emoji_row(palavra="", emoji=""):
            row = ctk.CTkFrame(emoji_rows_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            entry_palavra = ctk.CTkEntry(row, placeholder_text="palavra-chave")
            entry_palavra.insert(0, palavra)
            entry_palavra.pack(side="left", fill="x", expand=True, padx=(0, 5))

            entry_emoji = ctk.CTkEntry(row, placeholder_text="emoji", width=70)
            entry_emoji.insert(0, emoji)
            entry_emoji.pack(side="left", padx=(0, 5))

            def remover():
                row.destroy()
                linhas_emoji.remove(item)

            btn_remove = ctk.CTkButton(row, text="✕", width=30, fg_color="#dc3545", command=remover)
            btn_remove.pack(side="left")

            item = (row, entry_palavra, entry_emoji)
            linhas_emoji.append(item)

        for palavra, emoji in emoji_dict_atual.items():
            add_emoji_row(palavra, emoji)

        ctk.CTkButton(scroll, text="+ Adicionar palavra", command=lambda: add_emoji_row()).pack(
            fill="x", pady=(8, 5))

        status_label = ctk.CTkLabel(scroll, text="", text_color="#28a745")
        status_label.pack(pady=(10, 0))

        def salvar():
            try:
                novo_size = int(float(entry_size.get().replace(",", ".")))
                novo_pos_y = float(entry_pos_y.get().replace(",", "."))

                novo_dict = {}
                for _, e_palavra, e_emoji in linhas_emoji:
                    palavra = e_palavra.get().strip().lower()
                    emoji = e_emoji.get().strip()
                    if palavra and emoji:
                        novo_dict[palavra] = emoji

                s["subtitle_font"] = entry_font.get().strip()
                s["subtitle_size"] = novo_size
                s["subtitle_color"] = entry_color.get().strip()
                s["subtitle_outline_color"] = entry_outline.get().strip()
                s["subtitle_pos_y"] = novo_pos_y
                s["imagemagick_path"] = entry_magick.get().strip()
                s["emoji_dictionary"] = novo_dict

                cfg.save_settings(s)

                status_label.configure(text="✅ Legendas & Emojis salvos! Use o Teste Rápido para conferir.")
                self.update_log("Configurações de legenda atualizadas.")
            except ValueError:
                status_label.configure(text="❌ Tamanho e Posição precisam ser números.", text_color="#dc3545")
            except Exception as e:
                status_label.configure(text=f"❌ Erro ao salvar: {e}", text_color="#dc3545")

        ctk.CTkButton(scroll, text="SALVAR LEGENDAS & EMOJIS", fg_color="green", command=salvar).pack(
            fill="x", pady=(15, 5))

    def stop_process(self): self.app_logic.stop_process()
    def open_folder(self): self.update_log(self.app_logic.open_output_folder())
    def clear_temp(self): self.update_log(self.app_logic.clear_temp())
    def cancel_shutdown(self): self.update_log(self.app_logic.cancel_shutdown())
    def on_closing(self):
        self.app_logic.config.settings["window_geometry"] = self.geometry()
        self.app_logic.config.save_settings()
        self.destroy()

if __name__ == "__main__":
    app = PodcastClipperGUI()
    app.mainloop()

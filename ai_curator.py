# HISTÓRICO DE MANUTENÇÃO:
# -------------------------------------------------------------------------------------------------
# PROBLEMA: O sistema estava gerando apenas Shorts e nenhum Corte. Além disso, ocorreu um erro 
# "ValueError: Number of samples must be non-negative" que interrompeu o processamento e o PC 
# desligou antes de terminar a fila.
#
# SOLUÇÃO: 
# 1. Otimização de Prompt: Reforcei a necessidade de encontrar "Cortes" (40-120s) com narrativas completas.
# 2. Blindagem de Tempo: Adicionei uma verificação para garantir que 'end' seja sempre maior que 'start'.
# 3. Normalização Robusta: Se a IA sugerir um tempo inválido, o sistema agora descarta o item antes de 
# tentar renderizar, evitando o travamento do MoviePy.
# 4. Histórico no Topo: Implementado este cabeçalho para rastreabilidade de versões.
# -------------------------------------------------------------------------------------------------

import json
import requests
import time
import re
import os
from datetime import datetime

class AICurator:
    def __init__(self, config):
        self.config = config
        self.url = config.LOCAL_AI_URL
        self.models = config.AI_MODELS_PRIORITY
        # Ajustado para usar curation_rules conforme definido no config.py do usuário
        self.rules = getattr(config, 'curation_rules', getattr(config, 'CURATION_RULES', {}))
        self.raw_log_file = None

    def _set_log_paths(self, output_dir):
        """Define o caminho para salvar as respostas brutas da IA para depuração."""
        self.raw_log_file = os.path.join(output_dir, "ai_raw_response.json")

    def analyze_transcription(self, segments, callback=None):
        """Divide a transcrição em blocos e aplica as 4 regras de curadoria em cada um."""
        all_shorts = []
        all_cuts = []
        
        # Blocos de 10 minutos (600 segundos)
        block_size = 600
        total_duration = segments[-1]['end'] if segments else 0
        num_blocks = int(total_duration // block_size) + 1
        
        if callback: callback(f"Iniciando análise multi-regra de {num_blocks} blocos...")

        for i in range(num_blocks):
            start_t = i * block_size
            end_t = (i + 1) * block_size
            block_segments = [s for s in segments if s['start'] >= start_t and s['start'] < end_t]
            
            if not block_segments:
                continue
                
            block_text = "\n".join([f"[{s['start']:.1f}s - {s['end']:.1f}s]: {s['text']}" for s in block_segments])
            
            # Aplicar as 4 regras para cada bloco
            for rule_key, rule_info in self.rules.items():
                if callback: callback(f"Analisando bloco {i+1}/{num_blocks} - Regra: {rule_info['name']}...")
                
                results = self._get_ai_suggestions(block_text, rule_info)
                
                # Processar Shorts
                for item in results.get("shorts", []):
                    item = self._normalize_item(item, rule_info['name'])
                    if item and item['end'] > item['start']: # Blindagem contra tempos negativos
                        expanded = self._expand_and_clean(item, is_short=True, chunk_min=start_t, chunk_max=end_t)
                        if not self._is_duplicate(expanded, all_shorts):
                            all_shorts.append(expanded)
                        
                # Processar Cortes
                for item in results.get("cuts", []):
                    item = self._normalize_item(item, rule_info['name'])
                    if item and item['end'] > item['start']: # Blindagem contra tempos negativos
                        expanded = self._expand_and_clean(item, is_short=False, chunk_min=start_t, chunk_max=end_t)
                        if not self._is_duplicate(expanded, all_cuts):
                            all_cuts.append(expanded)

        return {"shorts": all_shorts, "cuts": all_cuts}

    def _get_ai_suggestions(self, text, rule_info):
        """Tenta obter sugestões da IA usando o sistema de fallback de modelos e extração robusta."""
        prompt = self._build_prompt(text, rule_info)
        
        for model in self.models:
            try:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_ctx": 4096, "temperature": 0.7}
                }
                
                endpoints = [self.url, "http://localhost:11434/api/generate", "http://127.0.0.1:11434/api/generate"]
                for endpoint in endpoints:
                    try:
                        response = requests.post(endpoint, json=payload, timeout=180)
                        if response.status_code == 200:
                            raw_content = response.json().get("response", "")
                            
                            if self.raw_log_file:
                                with open(self.raw_log_file, "a", encoding="utf-8") as f:
                                    f.write(f"\n--- MODELO: {model} | REGRA: {rule_info['name']} ---\n")
                                    f.write(raw_content + "\n")

                            parsed = self._parse_json_robust(raw_content)
                            if parsed.get("shorts") or parsed.get("cuts"):
                                return parsed
                    except:
                        continue
            except Exception as e:
                print(f"Erro com modelo {model}: {e}")
                continue
        return {"shorts": [], "cuts": []}

    def _build_prompt(self, text, rule_info):
        return f"""
Você é um editor de vídeos especialista em podcasts virais e cortes de alta retenção.
Sua missão é encontrar os melhores momentos na transcrição abaixo seguindo esta REGRA ESPECÍFICA:

REGRA: {rule_info['name']} - {rule_info['prompt']}

INSTRUÇÕES CRÍTICAS DE EQUILÍBRIO:
1. SHORTS (30-60s): Momentos de impacto, frases rápidas, ganchos virais.
2. CORTES (40-120s): Narrativas completas, histórias com início, meio e fim, explicações profundas.
3. IMPORTANTE: Você DEVE encontrar pelo menos 1 CORTE longo para cada 2 SHORTS. Não ignore as histórias longas!
4. Responda OBRIGATORIAMENTE em formato JSON.
5. IGNORE propagandas, cupons, links, apresentações iniciais e despedidas.
6. Para cada item, forneça: 'start', 'end', 'context' (em português) e 'quote' (frase exata).

TRANSCRIÇÃO:
{text}

FORMATO DE RESPOSTA (JSON PURO):
{{
    "shorts": [ {{"start": 0.0, "end": 30.0, "context": "...", "quote": "..."}} ],
    "cuts": [ {{"start": 0.0, "end": 60.0, "context": "...", "quote": "..."}} ]
}}
"""

    def _parse_json_robust(self, content):
        """Extrai JSON de dentro de qualquer texto explicativo da IA."""
        try:
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                json_str = match.group()
                json_str = json_str.replace('```json', '').replace('```', '')
                return json.loads(json_str)
            return json.loads(content)
        except:
            try:
                clean_content = re.sub(r'//.*', '', content)
                match = re.search(r'\{.*\}', clean_content, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except:
                pass
            return {"shorts": [], "cuts": []}

    def _normalize_item(self, item, rule_name):
        """Garante que os campos existam e estejam nos nomes corretos (PT/EN)."""
        try:
            start = float(item.get("start", item.get("inicio", 0)))
            end = float(item.get("end", item.get("fim", 0)))
            
            # Se o tempo for negativo ou fim menor que início, retorna None para descartar
            if start < 0 or end <= start:
                return None

            normalized = {
                "start": start,
                "end": end,
                "context": str(item.get("context", item.get("contexto", "Sem descrição"))),
                "quote": str(item.get("quote", item.get("citacao", ""))),
                "rule": rule_name
            }
            return normalized
        except:
            return None

    def _expand_and_clean(self, item, is_short, chunk_min, chunk_max):
        """Garante duração mínima e limpa o contexto."""
        min_duration = 30 if is_short else 40
        duration = item['end'] - item['start']
        
        if duration < min_duration:
            diff = min_duration - duration
            item['start'] = max(chunk_min, item['start'] - diff/2)
            item['end'] = min(chunk_max, item['end'] + diff/2)
            
        item['context'] = self._translate_common_terms(item['context'])
        return item

    def _translate_common_terms(self, text):
        translations = {
            "Rule applied": "Regra aplicada",
            "Speaker": "Falante",
            "Context": "Contexto",
            "Motivation": "Motivação",
            "Story": "História",
            "Applied Rule": "Regra Aplicada"
        }
        for eng, pt in translations.items():
            text = text.replace(eng, pt)
        return text

    def _is_duplicate(self, new_item, existing_list):
        """Evita que o mesmo trecho seja processado várias vezes."""
        for item in existing_list:
            if abs(item['start'] - new_item['start']) < 10 and abs(item['end'] - new_item['end']) < 10:
                return True
        return False

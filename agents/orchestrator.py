# agents/orchestrator.py
"""Implementação do Agente Orquestrador Acadêmico com triagem Maestro e gerenciamento de estado."""

from typing import Generator, List, Optional
import os

try:
    import streamlit as st
except ImportError:
    st = None

from langchain_core.prompts import ChatPromptTemplate
from agents.prompts import (
    ORCHESTRATOR_SYSTEM_PROMPT, 
    ESTRUTURADOR_SYSTEM_PROMPT, 
    QA_SYSTEM_PROMPT
)
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class OrchestratorAgent:
    """Agente Maestro que orquestra a triagem e delegação para especialistas."""

    def __init__(self, model_manager, docs_manager=None):
        self.mm = model_manager
        self.docs_manager = docs_manager
        
        # Inicializa chaves no session_state do ModelManager
        ss = self.mm.session_state
        if 'agente_ativo' not in ss:
            ss['agente_ativo'] = 'ORCHESTRATOR'
        if 'active_doc_id' not in ss:
            ss['active_doc_id'] = None
        if 'last_active_section' not in ss:
            ss['last_active_section'] = None

    @property
    def llm(self):
        """Acessa o LLM dinamicamente do session_state do ModelManager."""
        return self.mm.session_state.get('llm')

    def create_google_doc_from_structure(self, structure: dict):
        """Creates a Google Doc based on the approved structure. Reuses existing if title matches."""
        ss = self.mm.session_state
        existing_id = ss.get('active_doc_id')
        if existing_id:
            print(f"[GOOGLE DOCS] Reutilizando documento ID: {existing_id}")
            return existing_id

        if self.docs_manager:
            title = structure.get("titulo", "Trabalho Acadêmico")
            print(f"[GOOGLE DOCS] Criando novo documento: {title}")
            try:
                doc_id = self.docs_manager.create_academic_document(
                    title=title,
                    structure=structure
                )
                ss['active_doc_id'] = doc_id
                ss['current_structure'] = structure # Salva a estrutura ativa para mapeamento dinâmico
                return doc_id
            except Exception as e:
                print(f"[GOOGLE DOCS] Erro ao criar documento: {e}")
                return None
        return None

    def extrair_estrutura_da_mensagem(self, mensagem_ai: str) -> dict:
        """Usa o LLM para converter o texto em JSON de estrutura."""
        ss = self.mm.session_state
        if not self.llm:
            return None
            
        prompt = f"""Analise a proposta de estrutura acadêmica abaixo e extraia o título e as seções principais.

PROPOSTA:
{mensagem_ai}

REGRAS DE EXTRAÇÃO:
1. Identifique o TÍTULO principal do trabalho.
2. Identifique CADA UMA das seções propostas (ex: INTRODUÇÃO, METODOLOGIA, RESUMO GERAL, etc).
3. Capture inclusive seções que pareçam resumos iniciais se elas tiverem um título próprio.
4. Formate rigorosamente como este JSON: {{"titulo": "...", "secoes": [{{"key": "CHAVE_EM_MAIUSCULO", "titulo": "Nome Completo da Seção"}}]}}
5. Retorne APENAS o JSON.

JSON:"""
        # Tenta extrair da mensagem direta
        try:
            res = self.llm.invoke(prompt).content.strip()
            import json, re
            match = re.search(r'\{.*\}', res, re.DOTALL)
            if match:
                data = json.loads(match.group())
                valido = [s for s in data.get("secoes", []) if s.get("key") and s.get("titulo")]
                if valido:
                    data["secoes"] = valido
                    print(f"[ESTRUTURA] Parser LLM extraiu {len(valido)} seções.")
                    ss['current_structure'] = data # Atualiza o mapeamento dinâmico
                    return data
        except Exception as e:
            print(f"[ESTRUTURA] Erro no parsing JSON: {e}")

        # Heurística de regex: Busca por ### Nome da Seção
        print("[ESTRUTURA] Falha no Parser LLM. Tentando heurística de regex...")
        import re
        headers = re.findall(r'###\s*(.*)', mensagem_ai)
        if headers:
            secoes = []
            for h in headers:
                clean = h.split(":")[0].strip()
                if clean:
                    secoes.append({"key": clean.upper().replace(" ", "_"), "titulo": clean})
            if secoes:
                data = {"titulo": "Trabalho Acadêmico", "secoes": secoes}
                ss['current_structure'] = data
                return data

        print("[ESTRUTURA] Nenhuma estrutura válida encontrada na mensagem.")
        return None

    def write_section_to_doc(self, section_key: str, content: str):
        """Writes a generated section to the active Google Doc."""
        doc_id = self.mm.session_state.get('active_doc_id')
        if self.docs_manager and doc_id:
            self.docs_manager.write_section(doc_id, section_key, content)
            return True
        return False

    def _is_approval(self, text: str) -> bool:
        """Heurística simples para detectar aprovação."""
        keywords = ["sim", "aprovo", "ok", "pode", "prossiga", "aceito", "está bom", "tá bom", "manda ver", "com certeza"]
        text_lower = text.lower().strip()
        # Match exato ou início
        if text_lower in keywords:
            return True
        for k in keywords:
            if text_lower.startswith(k + " ") or text_lower.startswith(k + "."):
                return True
        return False

    def route_request(self, input_usuario: str) -> Generator[str, None, None]:
        """Realiza a triagem, troca de estado se necessário e delega para o especialista."""
        if not self.llm:
            raise ValueError("LLM não inicializado no ModelManager.")

        ss = self.mm.session_state
        
        # 0. Interceptação de Aprovação de Estrutura
        if ss.get('agente_ativo') == 'AGUARDANDO_APROVACAO':
            if self._is_approval(input_usuario):
                print(f"[ORCHESTRATOR] Aprovação detectada! Criando documento...")
                current_struct = ss.get('current_structure')
                if current_struct:
                    doc_id = self.create_google_doc_from_structure(current_struct)
                    if doc_id:
                        link = f"https://docs.google.com/document/d/{doc_id}"
                        msg_confirmacao = f"✅ **Estrutura Aprovada!**\n\n📄 Documento criado com sucesso: [Abrir no Google Docs]({link})\n\nIniciando a escrita do conteúdo...\n\n---\n\n"
                        yield msg_confirmacao
                        # Muda estado para ESTRUTURADOR para o LLM continuar escrevendo
                        ss['agente_ativo'] = 'ESTRUTURADOR'
            else:
                # Se não for aprovação (ex: pedido de ajuste), volta para ESTRUTURADOR para refinar
                ss['agente_ativo'] = 'ESTRUTURADOR'

        # 1. Classificação de Intenção (Agora centralizada aqui)
        self.classificar_e_atualizar_estado(input_usuario)
        
        # 2. Seleção do Prompt baseado no Estado Atual
        agente_atual = self.mm.session_state['agente_ativo']
        prompt_sistema = self._get_prompt_por_agente(agente_atual)
        
        # 3. Detecção de Necessidade de Cobertura Total (Global)
        is_global = self._is_global_query(input_usuario, agente_atual)
        
        # 4. Recuperação de Contexto (RAG)
        contexto_rag = self.mm.rag_manager.get_contexto_para_prompt(
            input_usuario, 
            cobertura_total=is_global
        )
        
        # 5. Execução da Chain
        template = ChatPromptTemplate.from_messages([
            ('system', prompt_sistema),
            ('placeholder', '{chat_history}'),
            ('user', '{input}')
        ])
        
        chain = template | self.llm
        
        input_rich = input_usuario
        if contexto_rag and contexto_rag != "Nenhum contexto relevante encontrado nos documentos.":
             label = "CONTEXTO GLOBAL (Todos os docs)" if is_global else "CONTEXTO DOS DOCUMENTOS"
             input_rich = f"{label}:\n{contexto_rag}\n\nSOLICITAÇÃO: {input_usuario}"

        # 5b. Injeção da Estrutura Aprovada no contexto (se existir)
        ss = self.mm.session_state
        current_struct = ss.get('current_structure')
        if current_struct and agente_atual == 'ESTRUTURADOR':
            secoes_str = "\n".join([f"  - {s['key']}: {s['titulo']}" for s in current_struct.get('secoes', [])])
            input_rich = f"ESTRUTURA APROVADA (RESPEITAR RIGOROSAMENTE):\n{secoes_str}\n\n{input_rich}"

        full_response = ""
        for chunk in chain.stream({
            'input': input_rich,
            'chat_history': self.mm.get_historico_langchain()
        }):
            full_response += chunk.content
            yield chunk.content
        
        # 6. Persistência Automática no Google Docs (se aplicável)
        doc_id = ss.get('active_doc_id')
        if doc_id and self.docs_manager:
            import re
            
            # 1. TENTA DIVIDIR EM BLOCOS POR HEADERS (Multi-seção)
            import re
            valid_blocks = []
            # Encontra as posições de todos os cabeçalhos que iniciam uma linha com #
            header_matches = list(re.finditer(r'(?m)^#+.*$', full_response))
            
            if header_matches:
                for i in range(len(header_matches)):
                    start = header_matches[i].start()
                    # O bloco termina no início do próximo cabeçalho ou no fim da resposta
                    end = header_matches[i+1].start() if i+1 < len(header_matches) else len(full_response)
                    block = full_response[start:end].strip()
                    if block:
                        valid_blocks.append(block)
            
            # Fallback: Se não encontrou blocos com #, mas a resposta é longa, trata como seção única
            if not valid_blocks and len(full_response.strip()) > 50:
                valid_blocks = [full_response.strip()]

            if len(valid_blocks) > 0:
                print(f"[GOOGLE DOCS] Detectados {len(valid_blocks)} blocos potenciais.")
                for block in valid_blocks:
                    # Detecta a chave da seção para este bloco específico
                    section_key = self._detect_section_key(input_usuario, block)
                    
                    if section_key:
                        try:
                            clean_content = self._limpar_conteudo_para_doc(block)
                            
                            # Tenta pegar o título real da estrutura para o Title Hint
                            title_hint = None
                            if current_struct:
                                for s in current_struct.get('secoes', []):
                                    if s['key'] == section_key:
                                        title_hint = s['titulo']
                                        break

                            print(f"[GOOGLE DOCS] Salvando bloco: {section_key} ({title_hint})")
                            self.docs_manager.write_section(doc_id, section_key, clean_content, title_hint=title_hint)
                            ss['last_active_section'] = section_key
                        except Exception as e:
                            print(f"Erro ao salvar bloco {section_key}: {e}")
            else:
                print("[GOOGLE DOCS] Nenhum bloco de seção detectado na resposta.")

        # Estado: se propusemos estrutura mas não temos doc, aguardamos aprovação
        if ss['agente_ativo'] == 'ESTRUTURADOR' and not doc_id:
            estrutura = self.extrair_estrutura_da_mensagem(full_response)
            if estrutura:
                ss['agente_ativo'] = 'AGUARDANDO_APROVACAO'

    def _detect_section_key(self, user_text: str, ai_text: str = "") -> str:
        """Heurística robusta para detectar qual seção está sendo referenciada."""
        import re
        import unicodedata
        
        def normalize_simple(t: str) -> str:
            if not t: return ""
            return ''.join(c for c in unicodedata.normalize('NFD', t) 
                          if unicodedata.category(c) != 'Mn').upper().replace("_", " ").strip()

        user_norm = normalize_simple(user_text)
        ai_norm = normalize_simple(ai_text)
        ss = self.mm.session_state
        current_struct = ss.get('current_structure', {})
        secoes = current_struct.get('secoes', [])
        
        # 1. PRIORIDADE: KEY DIRETA NO TEXTO (Ex: INTRODUCAO)
        for s in secoes:
            key_norm = s['key'].upper()
            if key_norm in ai_norm:
                return s['key']

        # 2. PRIORIDADE: TÍTULO EXATO COMO HEADER (### Título)
        for s in secoes:
            titulo_norm = normalize_simple(s['titulo'])
            # pattern busca o título como primeira linha ou após quebra, possivelmente com #
            pattern = rf'(^|\n)(\#+\s*)?{re.escape(titulo_norm)}'
            if re.search(pattern, ai_norm):
                return s['key']

        # 3. PRIORIDADE: SUBSTRING DO TÍTULO NO INÍCIO DO BLOCO (Fuzzy)
        for s in secoes:
            titulo_norm = normalize_simple(s['titulo'])
            # Se o título da seção está contido nas primeiras palavras do bloco
            if titulo_norm in ai_norm[:100] or ai_norm[:50] in titulo_norm:
                return s['key']

        # 4. FALLBACK: MAPEAMENTO ESTÁTICO
        mapping = {
            "INTRODUCAO": "INTRODUCAO",
            "METODOLOGIA": "METODOLOGIA",
            "RESULTADOS": "RESULTADOS",
            "CONCLUSAO": "CONCLUSAO",
            "REFERENCIAS": "REFERENCIAS",
            "RESUMO": "RESUMO"
        }
        for kw, key in mapping.items():
            if kw in ai_norm:
                return key

        # 5. ÚLTIMO RECURSO: ÚLTIMA SEÇÃO ATIVA
        if ss.get('last_active_section') and any(kw in user_norm for kw in ["MAIS", "CONTINUE", "PROSSIGA", "OK"]):
            return ss['last_active_section']
            
        return None

    def _limpar_conteudo_para_doc(self, text: str) -> str:
        """Remove conversas amigáveis da IA (início e fim) para salvar apenas o texto acadêmico."""
        import re
        
        lines = text.split('\n')
        academic_lines = []
        
        # Frases conversacionais de INÍCIO (antes do conteúdo acadêmico)
        conversational_starters = [
            "claro", "com certeza", "aqui está", "entendido", "excelente",
            "perfeito", "vou redigir", "vamos prosseguir", "vou começar",
            "segue abaixo", "segue a redação", "vou escrever", "apresento"
        ]
        
        # Frases conversacionais de FIM (após o conteúdo acadêmico)
        conversational_footers = [
            r"posso prosseguir.*\?", r"espero que.*", r"estou à disposição.*", 
            r"se precisar.*", r"qualquer dúvida.*", r"o que achou.*",
            r"gostaria que eu.*\?", r"deseja que eu.*\?", r"quer que eu.*\?",
            r"próxima seção.*", r"posso continuar.*\?"
        ]
        
        # Fase 1: Encontrar o início do conteúdo acadêmico
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            # Pula linhas que parecem conversacionais
            if any(kw in stripped.lower() for kw in conversational_starters):
                start_idx = i + 1
                continue
            # Pula títulos de seção (ex: "INTRODUÇÃO" sozinho ou "### INTRODUÇÃO")  
            if stripped.startswith('###'):
                start_idx = i + 1
                continue
            # Se a linha é um título standalone em maiúsculas curto (ex: "INTRODUÇÃO")
            if stripped.isupper() and len(stripped.split()) <= 5:
                start_idx = i + 1
                continue
            break
        
        # Fase 2: Encontrar o fim do conteúdo acadêmico (de trás pra frente)
        end_idx = len(lines)
        for i in range(len(lines) - 1, start_idx - 1, -1):
            stripped = lines[i].strip()
            if not stripped:
                end_idx = i
                continue
            is_footer = False
            for footer_regex in conversational_footers:
                if re.search(footer_regex, stripped, re.IGNORECASE):
                    is_footer = True
                    break
            if is_footer:
                end_idx = i
                continue
            break
        
        academic_lines = lines[start_idx:end_idx]
        cleansed = "\n".join(academic_lines).strip()
        
        # Fallback: se o sanduíche ficou vazio, usa o texto original com limpeza básica
        if not cleansed or len(cleansed) < 20:
            cleansed = text.strip()
        
        return cleansed

    def _is_global_query(self, input_usuario: str, agente_ativo: str) -> bool:
        """Detecta se a pergunta exige análise de todos os documentos."""
        if agente_ativo == 'ESTRUTURADOR':
            return True
            
        keywords_globais = [
            "todos", "cada um", "resumo geral", "comparativo", 
            "quais são os artigos", "lista de artigos", "panorama"
        ]
        input_lower = input_usuario.lower()
        if any(kw in input_lower for kw in keywords_globais):
            return True
            
        return False

    def classificar_e_atualizar_estado(self, input_usuario: str):
        """Classifica a intenção e atualiza o agente ativo no session_state."""
        ss = self.mm.session_state
        estado_atual = ss.get('agente_ativo')
        
        if estado_atual == 'AGUARDANDO_APROVACAO':
            input_lower = input_usuario.lower()
            # Heurística de aprovação: palavras positivas ou comando direto
            keywords_aprovacao = ["aprov", "gostei", "pode criar", "ok", "perfeito", "excelente", "manda ver", "seguir", "continuar"]
            
            if any(kw in input_lower for kw in keywords_aprovacao):
                print("[TRIAGEM] Estrutura aprovada. Iniciando criação do Google Doc...")
                
                # Recupera a última mensagem da IA para extrair a estrutura
                mensagens = self.mm.mensagens
                ultimo_texto_ia = ""
                for msg in reversed(mensagens):
                    if msg['role'] == 'ai':
                        ultimo_texto_ia = msg['content']
                        break
                
                if ultimo_texto_ia:
                    estrutura = self.extrair_estrutura_da_mensagem(ultimo_texto_ia)
                    if estrutura:
                        doc_id = self.create_google_doc_from_structure(estrutura)
                        if doc_id:
                            print(f"[TRIAGEM] Google Doc criado: {doc_id}")
                            ss['active_doc_id'] = doc_id
            
            ss['agente_ativo'] = 'ESTRUTURADOR'
            return

        last_classified = ss.get('last_input_classified')
        if last_classified == input_usuario:
            return

        prompt_classificador = """Analise o último input do usuário e classifique a intenção em uma única palavra:
- ESCRITA: O usuário quer criar, escrever, estruturar, PRODUZIR OU EDITAR um novo documento.
- CONSULTA: O usuário quer tirar dúvidas sobre o conteúdo ou análise dos documentos existentes.
- ORCHESTRATOR: Saudação, conversa fiada ou algo irrelevante.

CRITÉRIO DE DESEMPATAR: Se o usuário quer "ESCREVER" algo novo, a prioridade é ESCRITA.
Resposta (apenas a palavra):"""
        
        historico_resumo = "\n".join([f"{m['role']}: {m['content'][:150]}..." for m in self.mm.mensagens[-3:]])
        
        mensagens = [
            SystemMessage(content=prompt_classificador),
            HumanMessage(content=f"Histórico Recente:\n{historico_resumo}\n\nÚltimo Input: {input_usuario}")
        ]
        
        try:
            resposta_raw = self.llm.invoke(mensagens).content.strip().upper()
            ss['last_input_classified'] = input_usuario
            
            if "ESCRITA" in resposta_raw:
                novo_estado = 'ESTRUTURADOR'
            elif "CONSULTA" in resposta_raw:
                novo_estado = 'QA'
            else:
                novo_estado = 'ORCHESTRATOR'

            input_lower = input_usuario.lower()
            
            # Heurística 1: Palavras-chave expandidas
            keywords_escrita = [
                "escrever", "criar", "estruturar", "produzir", "redigir", "editar", 
                "mudar", "alterar", "melhorar", "corrigir", "atualizar", "revisar",
                "alteração", "correção", "edição", "mudança", "atualização", "revisão",
                "incluir", "inclusão", "texto", "seção", "capítulo"
            ]
            
            if any(kw in input_lower for kw in keywords_escrita):
                novo_estado = 'ESTRUTURADOR'
            elif any(kw in input_lower for kw in ["pergunta", "dúvida", "quem", "o que", "onde", "quando", "resuma"]):
                if novo_estado == 'ORCHESTRATOR':
                    novo_estado = 'QA'
            
            # Heurística 2: Menção direta a Seções do Documento Ativo (FORCE UPDATE)
            active_doc = ss.get('active_doc_id')
            current_struct = ss.get('current_structure')
            if active_doc and current_struct:
                for s in current_struct.get('secoes', []):
                    # Verifica se o título da seção está na mensagem
                    if s['titulo'].lower() in input_lower:
                        print(f"[TRIAGEM] Menção à seção '{s['titulo']}' detectada. Forçando ESTRUTURADOR.")
                        novo_estado = 'ESTRUTURADOR'
                        break

            print(f"[TRIAGEM] Input: {input_usuario[:30]}... | Resposta: {resposta_raw} | Estado Final: {novo_estado}")
            ss['agente_ativo'] = novo_estado
            
        except Exception as e:
            print(f"Erro na classificação: {e}")
            ss['agente_ativo'] = 'ORCHESTRATOR'

    def _get_prompt_por_agente(self, agente: str) -> str:
        if agente == 'ESTRUTURADOR':
            return ESTRUTURADOR_SYSTEM_PROMPT
        elif agente == 'QA':
            return QA_SYSTEM_PROMPT
        return ORCHESTRATOR_SYSTEM_PROMPT

    def planejar_documento(self, objetivo: str) -> Generator[str, None, None]:
        """Mantido por compatibilidade."""
        yield from self.route_request(objetivo)

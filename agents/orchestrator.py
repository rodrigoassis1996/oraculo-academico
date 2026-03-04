# agents/orchestrator.py
"""Implementação do Agente Orquestrador Acadêmico com triagem Maestro e gerenciamento de estado."""

from typing import Generator, List, Optional
import os
import re
import json
import traceback

from langchain_core.prompts import ChatPromptTemplate
from agents.prompts import (
    ORCHESTRATOR_SYSTEM_PROMPT, 
    ESTRUTURADOR_SYSTEM_PROMPT, 
    QA_SYSTEM_PROMPT
)
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from services.google_docs import exceptions as gdocs_exceptions

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
        if 'pending_section' not in ss:
            ss['pending_section'] = None  # {key, titulo, content} aguardando aprovação
        if 'sections_queue' not in ss:
            ss['sections_queue'] = []  # Fila de seções a serem escritas
        if 'completed_sections' not in ss:
            ss['completed_sections'] = []  # Seções já aprovadas e escritas

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
            doc_id = self.docs_manager.create_academic_document(
                title=title,
                structure=structure
            )
            ss['active_doc_id'] = doc_id
            ss['current_structure'] = structure # Salva a estrutura ativa para mapeamento dinâmico
            return doc_id
            
        print("[GOOGLE DOCS] docs_manager é None! Verifique se credentials.json existe.") # Log when docs_manager is None
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
            match = re.search(r'\{.*\}', res, re.DOTALL)
            if match:
                data = json.loads(match.group())
                valido = [s for s in data.get("secoes", []) if s.get("key") and s.get("titulo")]
                if valido:
                    data["secoes"] = valido
                    print(f"[ESTRUTURA] Parser LLM extraiu {len(valido)} seções.")
                    ss['current_structure'] = data
                    return data
                else:
                    print(f"[ESTRUTURA] LLM retornou JSON mas sem seções válidas: {res[:200]}")
            else:
                print(f"[ESTRUTURA] LLM não retornou JSON válido: {res[:200]}")
        except Exception as e:
            print(f"[ESTRUTURA] Erro no parsing LLM: {e}")

        # Heurística de regex: Busca por ### Nome da Seção ou 1. Nome da Seção
        print("[ESTRUTURA] Falha no Parser LLM. Tentando heurística de regex...")
        secoes = []

        # Divide por linhas para evitar problemas com âncoras ^ em textos complexos
        linhas = [l.strip() for l in mensagem_ai.splitlines() if l.strip()]
        
        for linha in linhas:
            # Prioridade 1: Headers ### 
            match_h = re.search(r'^#{1,4}\s*(.*)', linha)
            if match_h:
                titulo = match_h.group(1).split(":")[0].split("|")[0].strip().replace("*", "")
                if titulo:
                    print(f"[DEBUG] Heurística Regex detectou seção (Header): {titulo}")
                    secoes.append({"key": titulo.upper().replace(" ", "_"), "titulo": titulo})
                continue
            
            # Prioridade 2: Lista Numerada (1., 1), 1.1, 1.1.)
            match_n = re.search(r'^(\d+[\.\d]*)[.\)]?\s+(.*)', linha)
            if match_n:
                num_part = match_n.group(1)
                titulo = match_n.group(2).split(":")[0].split("|")[0].strip().replace("*", "")
                if titulo:
                    print(f"[DEBUG] Heurística Regex detectou seção (Lista): {titulo}")
                    secoes.append({"key": titulo.upper().replace(" ", "_"), "titulo": titulo})

        if secoes:
            # Remove duplicatas mantendo ordem
            secoes_unicas = []
            vistos = set()
            for s in secoes:
                if s['key'] not in vistos:
                    secoes_unicas.append(s)
                    vistos.add(s['key'])
            
            data = {"titulo": "Trabalho Acadêmico", "secoes": secoes_unicas}
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

    def _get_reauth_message(self) -> str:
        """Gera uma mensagem amigável com link de reautenticação."""
        try:
            if not getattr(self.mm, 'auth_manager', None):
                return "⚠️ **Sua autorização com o Google Docs expirou ou foi revogada.**\n\n" \
                       "Não foi possível gerar um link automático. Por favor, reinicie sua sessão ou verifique as credenciais do sistema."
            
            # Define a URL de callback (pode precisar de ajuste dependendo do ambiente)
            redirect_uri = "http://localhost:8000/api/v1/auth/google/callback"
            session_id = getattr(self.mm, 'session_id', None) or "local-dev"
            
            auth_url = self.mm.auth_manager.get_authorization_url(
                redirect_uri=redirect_uri,
                state=session_id
            )
            # Adiciona o session_id como parâmetro de estado ou similar se a API suportar
            # Para simplificar agora, apenas indicamos que o usuário deve clicar.
            return (
                "⚠️ **Sua autorização com o Google Docs expirou ou foi revogada.**\n\n"
                "Para continuar, você precisa autorizar o acesso novamente:\n"
                f"1. [Clique aqui para autorizar o Oráculo]({auth_url})\n"
                "2. Após autorizar, copie o código exibido e cole-o aqui ou simplesmente tente enviar sua mensagem novamente.\n\n"
                "*Dica: A nova autorização é válida por tempo indeterminado até que seja revogada.*"
            )
        except Exception as e:
            return f"⚠️ Erro ao gerar link de reautenticação: {str(e)}"

    def _is_approval(self, text: str) -> bool:
        """Heurística simples para detectar aprovação."""
        keywords = ["sim", "aprovo", "aprovado", "ok", "pode", "prossiga", "aceito", "está bom", "tá bom", "manda ver", "com certeza", "fechado"]
        # Remove pontuação comum para facilitar o match
        text_clean = text.lower().strip().replace(",", "").replace(".", "").replace("!", "")
        
        if any(text_clean == k for k in keywords):
            return True
        for k in keywords:
            if text_clean.startswith(k + " "):
                return True
        return False

    def route_request(self, input_usuario: str) -> Generator[str, None, None]:
        """Realiza a triagem, troca de estado se necessário e delega para o especialista."""
        if not self.llm:
            raise ValueError("LLM não inicializado no ModelManager.")

        ss = self.mm.session_state
        
        # 1. Classificação de Intenção (Centralizada)
        triage_result = self.classificar_e_atualizar_estado(input_usuario)
        
        if triage_result == "ERROR_FAIL_DOC":
            yield "⚠️ **Atenção**: Não consegui extrair a estrutura proposta ou criar o documento no Google Docs. \n\nPor favor, garanta que a estrutura proposta use títulos claros (###) ou listas numeradas.\n\n---\n\n"
            return
        elif triage_result == "AUTH_REVOKED":
            yield self._get_reauth_message()
            return
        elif triage_result == "CONTENT_APPROVED":
            # Conteúdo da seção foi aprovado e escrito no doc
            pending = ss.get('pending_section')
            if pending:
                yield f"✅ Seção **{pending.get('titulo', '')}** aprovada e salva no Google Docs!\n\n"
            # Avança para próxima seção
            yield from self._generate_next_section()
            return
        elif triage_result == "CONTENT_REJECTED":
            # Reescreve a seção corrente
            yield "🔄 Entendido! Vou reescrever a seção com as suas considerações.\n\n---\n\n"
            yield from self._rewrite_current_section(input_usuario)
            return
        elif triage_result and triage_result not in ("ORCHESTRATOR", "ESCRITA", "CONSULTA", "ESTRUTURADOR", "QA"):
            # É um doc_id retornado pela aprovação da estrutura
            link = f"https://docs.google.com/document/d/{triage_result}"
            msg_confirmacao = f"✅ **Estrutura Aprovada!**\n\n📄 Documento criado com sucesso: [Abrir no Google Docs]({link})\n\nIniciando a redação do conteúdo...\n\n---\n\n"
            yield msg_confirmacao
            print(f"[ORCHESTRATOR] Estrutura aprovada. Iniciando geração da primeira seção...")
            # Inicia a escrita da primeira seção automaticamente
            yield from self._generate_next_section()
            return

        # 2. Seleção do Prompt baseado no Estado Atual
        agente_atual = ss.get('agente_ativo', 'ORCHESTRATOR')
        print(f"[ORCHESTRATOR] Agente ativo selecionado: {agente_atual}")
        prompt_sistema = self._get_prompt_por_agente(agente_atual)

        # 3. Detecção de Necessidade de Cobertura Total (Global)
        is_global = self._is_global_query(input_usuario, agente_atual)

        # 4. Recuperação de Contexto (RAG)
        print(f"[ORCHESTRATOR] Buscando contexto RAG (global={is_global})...")
        contexto_rag = self.mm.rag_manager.get_contexto_para_prompt(
            input_usuario,
            cobertura_total=is_global
        )
        print(f"[ORCHESTRATOR] Contexto RAG recuperado ({len(contexto_rag or '')} chars).")
        
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

        # 5b. Injeção da Estrutura no contexto para o Estruturador
        current_struct = ss.get('current_structure')
        if current_struct and agente_atual == 'ESTRUTURADOR':
            secoes_str = "\n".join([f"  - {s['key']}: {s['titulo']}" for s in current_struct.get('secoes', [])])
            input_rich = f"ESTRUTURA APROVADA (RESPEITAR RIGOROSAMENTE):\n{secoes_str}\n\n{input_rich}"

        full_response = ""
        print(f"[ORCHESTRATOR] Iniciando stream da resposta do LLM...")
        try:
            for chunk in chain.stream({
                'input': input_rich,
                'chat_history': self.mm.get_historico_langchain()
            }):
                full_response += chunk.content
                yield chunk.content
            print(f"[ORCHESTRATOR] Stream finalizado ({len(full_response)} chars).")
        except Exception as e:
            print(f"[ORCHESTRATOR] ERRO no stream do LLM: {e}")
            yield f"\n\n⚠️ Erro na comunicação com a IA: {str(e)}"
            return
        
        # 6. Detecção de estrutura proposta (transição para AGUARDANDO_APROVACAO)
        doc_id = ss.get('active_doc_id')
        if agente_atual in ['ESTRUTURADOR', 'ORCHESTRATOR'] and not doc_id:
            print(f"[ORCHESTRATOR] Analisando resposta para detectar estrutura... (len={len(full_response)})")
            estrutura = self.extrair_estrutura_da_mensagem(full_response)
            if estrutura:
                ss['agente_ativo'] = 'AGUARDANDO_APROVACAO'
                print(f"[ORCHESTRATOR] Estrutura detectada e estado -> AGUARDANDO_APROVACAO")
            else:
                print(f"[ORCHESTRATOR] Nenhuma estrutura detectada na resposta da IA.")

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
                # Verifica se não é apenas parte de outra palavra
                if re.search(rf'\b{re.escape(key_norm)}\b', ai_norm):
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

    def _handle_approval_flow(self) -> Optional[str]:
        """Tenta extrair estrutura e criar o Google Doc com o esqueleto."""
        ss = self.mm.session_state
        print("[APROVAÇÃO] Iniciando fluxo de aprovação e criação do Google Doc...")
        
        # 1. PRIORIDADE: Reutiliza estrutura já salva no session_state
        estrutura = ss.get('current_structure')
        if estrutura:
            print(f"[APROVAÇÃO] Reutilizando estrutura salva ({len(estrutura.get('secoes', []))} seções).")
        else:
            # 2. FALLBACK: Extrai da última mensagem da IA
            print("[APROVAÇÃO] Nenhuma estrutura salva. Tentando extrair da última mensagem...")
            ultimo_texto_ia = next(
                (msg['content'] for msg in reversed(self.mm.mensagens) if msg['role'] == 'ai'), 
                ""
            )
            if not ultimo_texto_ia:
                print("[APROVAÇÃO] ERRO: Nenhuma mensagem da IA encontrada no histórico!")
                ss['agente_ativo'] = 'ESTRUTURADOR'
                return "ERROR_FAIL_DOC"
            
            estrutura = self.extrair_estrutura_da_mensagem(ultimo_texto_ia)
        
        if not estrutura:
            print("[APROVAÇÃO] ERRO: Não foi possível obter a estrutura.")
            ss['agente_ativo'] = 'ESTRUTURADOR'
            return "ERROR_FAIL_DOC"
        
        print(f"[APROVAÇÃO] Estrutura com {len(estrutura.get('secoes', []))} seções.")
        
        if not self.docs_manager:
            print("[APROVAÇÃO] ERRO: docs_manager é None! credentials.json pode estar faltando.")
            ss['agente_ativo'] = 'ESTRUTURADOR'
            return "ERROR_FAIL_DOC"
        
        try:
            doc_id = self.create_google_doc_from_structure(estrutura)
        except (gdocs_exceptions.TokenRevokedError, gdocs_exceptions.AuthenticationError) as auth_e:
            print(f"[APROVAÇÃO] Erro de autenticação detectado: {auth_e}")
            return "AUTH_REVOKED"
        except Exception as e:
            print(f"[APROVAÇÃO] Erro inesperado: {e}")
            traceback.print_exc()
            return "ERROR_FAIL_DOC"

        if doc_id:
            print(f"[APROVAÇÃO] Google Doc criado com sucesso: {doc_id}")
            ss['active_doc_id'] = doc_id
            # Prepara fila de seções para escrita pelo Orquestrador
            ss['sections_queue'] = list(estrutura.get('secoes', []))
            ss['completed_sections'] = []
            ss['pending_section'] = None
            ss['agente_ativo'] = 'ORCHESTRATOR'
            return doc_id
        
        print("[APROVAÇÃO] ERRO: create_google_doc_from_structure retornou None.")
        ss['agente_ativo'] = 'ESTRUTURADOR'
        return "ERROR_FAIL_DOC"

    def _handle_content_approval(self, input_usuario: str) -> str:
        """Trata a aprovação ou rejeição do conteúdo de uma seção."""
        ss = self.mm.session_state
        pending = ss.get('pending_section')
        
        if not pending:
            print("[CONTEÚDO] ERRO: Nenhuma seção pendente para aprovação.")
            ss['agente_ativo'] = 'ORCHESTRATOR'
            return None
        
        if self._is_approval(input_usuario):
            # Escreve o conteúdo aprovado no Google Doc
            doc_id = ss.get('active_doc_id')
            if doc_id and self.docs_manager:
                try:
                    clean_content = self._limpar_conteudo_para_doc(pending['content'])
                    self.docs_manager.write_section(
                        doc_id, 
                        pending['key'], 
                        clean_content, 
                        title_hint=pending.get('titulo')
                    )
                    print(f"[CONTEÚDO] Seção '{pending['key']}' escrita no Google Doc.")
                    ss['completed_sections'].append(pending['key'])
                    ss['last_active_section'] = pending['key']
                except (gdocs_exceptions.TokenRevokedError, gdocs_exceptions.AuthenticationError) as auth_e:
                    print(f"[CONTEÚDO] Erro de autenticação detectado: {auth_e}")
                    return "AUTH_REVOKED"
                except Exception as e:
                    print(f"[CONTEÚDO] Erro ao escrever seção '{pending['key']}': {e}")
                    traceback.print_exc()
            
            ss['pending_section'] = None
            ss['agente_ativo'] = 'ORCHESTRATOR'
            return "CONTENT_APPROVED"
        else:
            # Usuário deu feedback, reescrever
            ss['agente_ativo'] = 'ORCHESTRATOR'
            return "CONTENT_REJECTED"

    def _generate_next_section(self) -> Generator[str, None, None]:
        """Gera o conteúdo da próxima seção na fila e exibe no chat."""
        ss = self.mm.session_state
        queue = ss.get('sections_queue', [])
        
        if not queue:
            yield "\n\n🎉 **Todas as seções foram finalizadas!** O documento está completo no Google Docs.\n"
            ss['agente_ativo'] = 'ORCHESTRATOR'
            return
        
        # Pega a próxima seção da fila
        next_section = queue.pop(0)
        ss['sections_queue'] = queue
        
        section_key = next_section['key']
        section_titulo = next_section['titulo']
        total = len(ss.get('completed_sections', [])) + len(queue) + 1
        current_num = len(ss.get('completed_sections', [])) + 1
        
        print(f"[ESCRITA] Gerando seção {current_num}/{total}: {section_titulo}")
        
        # Prepara o contexto RAG
        contexto_rag = self.mm.rag_manager.get_contexto_para_prompt(
            section_titulo, 
            cobertura_total=True
        )
        
        # Monta o prompt de escrita acadêmica
        current_struct = ss.get('current_structure', {})
        secoes_str = "\n".join([f"  - {s['titulo']}" for s in current_struct.get('secoes', [])])
        
        prompt_escrita = f"""Você é um redator acadêmico especialista. Escreva APENAS o conteúdo da seção abaixo.

ESTRUTURA COMPLETA DO TRABALHO:
{secoes_str}

SEÇÃO A ESCREVER AGORA ({current_num}/{total}): {section_titulo}

REGRAS:
- Primeira linha: ### {section_titulo}
- Escreva apenas esta seção, com rigor acadêmico e norma ABNT.
- Tom formal e impessoal.
- Ao finalizar, pergunte: "Você aprova esta seção e posso prosseguir para a próxima?"

CONTEXTO DOS DOCUMENTOS:
{contexto_rag}"""
        
        template = ChatPromptTemplate.from_messages([
            ('system', ESTRUTURADOR_SYSTEM_PROMPT),
            ('placeholder', '{chat_history}'),
            ('user', '{input}')
        ])
        
        chain = template | self.llm
        full_response = ""
        
        for chunk in chain.stream({
            'input': prompt_escrita,
            'chat_history': self.mm.get_historico_langchain()
        }):
            full_response += chunk.content
            yield chunk.content
        
        # Salva o conteúdo pendente para aprovação
        ss['pending_section'] = {
            'key': section_key,
            'titulo': section_titulo,
            'content': full_response
        }
        ss['agente_ativo'] = 'AGUARDANDO_APROVACAO_CONTEUDO'
        print(f"[ESCRITA] Seção '{section_titulo}' gerada. Estado -> AGUARDANDO_APROVACAO_CONTEUDO")

    def _rewrite_current_section(self, feedback: str) -> Generator[str, None, None]:
        """Reescreve a seção atual com o feedback do usuário."""
        ss = self.mm.session_state
        pending = ss.get('pending_section')
        
        if not pending:
            yield "⚠️ Nenhuma seção pendente para reescrever.\n"
            return
        
        section_titulo = pending['titulo']
        section_key = pending['key']
        previous_content = pending['content']
        
        contexto_rag = self.mm.rag_manager.get_contexto_para_prompt(
            section_titulo, 
            cobertura_total=True
        )
        
        prompt_reescrita = f"""Você já escreveu esta seção anteriormente, mas o usuário solicitou alterações.

SEÇÃO: {section_titulo}

VERSÃO ANTERIOR:
{previous_content[:2000]}

FEEDBACK DO USUÁRIO:
{feedback}

REGRAS:
- Primeira linha: ### {section_titulo}
- Reescreva incorporando o feedback.
- Tom formal e impessoal, norma ABNT.
- Ao finalizar, pergunte: "Você aprova esta seção e posso prosseguir para a próxima?"

CONTEXTO DOS DOCUMENTOS:
{contexto_rag}"""
        
        template = ChatPromptTemplate.from_messages([
            ('system', ESTRUTURADOR_SYSTEM_PROMPT),
            ('placeholder', '{chat_history}'),
            ('user', '{input}')
        ])
        
        chain = template | self.llm
        full_response = ""
        
        for chunk in chain.stream({
            'input': prompt_reescrita,
            'chat_history': self.mm.get_historico_langchain()
        }):
            full_response += chunk.content
            yield chunk.content
        
        # Atualiza o conteúdo pendente
        ss['pending_section'] = {
            'key': section_key,
            'titulo': section_titulo,
            'content': full_response
        }
        ss['agente_ativo'] = 'AGUARDANDO_APROVACAO_CONTEUDO'
        print(f"[ESCRITA] Seção '{section_titulo}' reescrita. Estado -> AGUARDANDO_APROVACAO_CONTEUDO")

    def classificar_e_atualizar_estado(self, input_usuario: str) -> Optional[str]:
        """Classifica a intenção e atualiza o agente ativo no session_state. Retorna doc_id se criado."""
        ss = self.mm.session_state
        estado_atual = ss.get('agente_ativo')
        
        # 1. Atalho: Estado AGUARDANDO_APROVACAO_CONTEUDO (aprovação de conteúdo de seção)
        if estado_atual == 'AGUARDANDO_APROVACAO_CONTEUDO':
            return self._handle_content_approval(input_usuario)
        
        # 2. Atalho: Aprovação da estrutura
        if estado_atual == 'AGUARDANDO_APROVACAO' and self._is_approval(input_usuario):
            return self._handle_approval_flow()

        last_classified = ss.get('last_input_classified')
        if last_classified == input_usuario:
            return None

        prompt_classificador = """Analise o último input do usuário e classifique a intenção em uma única palavra:
- APROVACAO: O usuário está concordando, aprovando, confirmando ou aceitando uma sugestão (ex: "sim", "pode ser", "ok", "aprovado", "fechado").
- ESCRITA: O usuário quer criar, escrever, estruturar, PRODUZIR OU EDITAR um novo documento.
- CONSULTA: O usuário quer tirar dúvidas sobre o conteúdo ou análise dos documentos existentes.
- ORCHESTRATOR: Saudação, conversa fiada ou algo irrelevante.

CRITÉRIO DE DESEMPATE: Se o usuário estiver aprovando uma estrutura proposta anteriormente, responda APROVACAO. Se quiser escrever algo do zero, ESCRITA.
Resposta (apenas a palavra):"""
        
        historico_resumo = "\n".join([f"{m['role']}: {m['content'][:150]}..." for m in self.mm.mensagens[-3:]])
        
        mensagens = [
            SystemMessage(content=prompt_classificador),
            HumanMessage(content=f"Histórico Recente:\n{historico_resumo}\n\nÚltimo Input: {input_usuario}")
        ]
        
        try:
            resposta_raw = self.llm.invoke(mensagens).content.strip().upper()
            ss['last_input_classified'] = input_usuario
            
            if "APROVACAO" in resposta_raw:
                return self._handle_approval_flow()
            elif "ESCRITA" in resposta_raw:
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
                "incluir", "inclusão", "texto", "seção", "capítulo", "artigo", "trabalho",
                "monografia", "tese", "dissertação", "acadêmico", "fazer"
            ]
            
            if any(kw in input_lower for kw in keywords_escrita):
                novo_estado = 'ESTRUTURADOR'
            elif any(kw in input_lower for kw in ["pergunta", "dúvida", "quem", "o que", "onde", "quando", "resuma"]):
                if novo_estado == 'ORCHESTRATOR':
                    novo_estado = 'QA'
            
            # Heurística 2: Menção direta a Seções do Documento Ativo
            active_doc = ss.get('active_doc_id')
            current_struct = ss.get('current_structure')
            if active_doc and current_struct:
                for s in current_struct.get('secoes', []):
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

# agents/orchestrator.py
"""Implementação do Agente Orquestrador Acadêmico com triagem Maestro e gerenciamento de estado."""

from typing import Generator, List
import streamlit as st
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
        if 'agente_ativo' not in st.session_state:
            st.session_state['agente_ativo'] = 'ORCHESTRATOR'
        if 'active_doc_id' not in st.session_state:
            st.session_state['active_doc_id'] = None
        if 'last_active_section' not in st.session_state:
            st.session_state['last_active_section'] = None

    @property
    def llm(self):
        """Acessa o LLM dinamicamente do session_state."""
        return st.session_state.get('llm')

    def create_google_doc_from_structure(self, structure: dict):
        """Creates a Google Doc based on the approved structure. Reuses existing if title matches."""
        existing_id = st.session_state.get('active_doc_id')
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
                st.session_state['active_doc_id'] = doc_id
                return doc_id
            except Exception as e:
                print(f"[GOOGLE DOCS] Erro ao criar documento: {e}")
                return None
        return None

    def extrair_estrutura_da_mensagem(self, mensagem_ai: str) -> dict:
        """Usa o LLM para converter o texto em JSON de estrutura."""
        prompt = f"""Analise a proposta de estrutura acadêmica abaixo e extraia o título e as seções principais.

PROPOSTA:
{mensagem_ai}

REGRAS DE EXTRAÇÃO:
1. Identifique o TÍTULO principal do trabalho (ou crie um se for óbvio).
2. Identifique cada SEÇÃO (como INTRODUÇÃO, METODOLOGIA, etc).
3. Formate rigorosamente como este JSON: {{"titulo": "...", "secoes": [{{"key": "CHAVE_EM_MAIUSCULO", "titulo": "Nome Completo da Seção"}}]}}
4. Não inclua o "Resumo" do capítulo no nome da seção no JSON.
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
                return {"titulo": "Trabalho Acadêmico", "secoes": secoes}

        print("[ESTRUTURA] Nenhuma estrutura válida encontrada na mensagem.")
        return None

    def write_section_to_doc(self, section_key: str, content: str):
        """Writes a generated section to the active Google Doc."""
        doc_id = st.session_state.get('active_doc_id')
        if self.docs_manager and doc_id:
            self.docs_manager.write_section(doc_id, section_key, content)
            return True
        return False

    def route_request(self, input_usuario: str) -> Generator[str, None, None]:
        """Realiza a triagem, troca de estado se necessário e delega para o especialista."""
        if not self.llm:
            raise ValueError("LLM não inicializado no ModelManager.")

        # 1. Classificação de Intenção (Fase Silenciosa)
        # Delegamos para o método de classificação que já possui as proteções de estado
        self.classificar_e_atualizar_estado(input_usuario)
        
        # 2. Seleção do Prompt baseado no Estado Atual
        agente_atual = st.session_state['agente_ativo']
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

        full_response = ""
        for chunk in chain.stream({
            'input': input_rich,
            'chat_history': self.mm.get_historico_langchain()
        }):
            full_response += chunk.content
            yield chunk.content
        
        # 6. Persistência Automática no Google Docs (se aplicável)
        doc_id = st.session_state.get('active_doc_id')
        if doc_id and self.docs_manager:
            section_key = self._detect_section_key(input_usuario)
            if section_key:
                try:
                    # Limpa a resposta para salvar apenas o conteúdo acadêmico
                    clean_content = self._limpar_conteudo_para_doc(full_response)
                    self.docs_manager.write_section(doc_id, section_key, clean_content)
                    st.session_state['last_active_section'] = section_key
                except Exception as e:
                    print(f"Erro ao salvar seção automaticamente: {e}")

        # Se o agente for o Estruturador, entramos no estado de guarda para aprovação
        if st.session_state['agente_ativo'] == 'ESTRUTURADOR':
            st.session_state['agente_ativo'] = 'AGUARDANDO_APROVACAO'

    def _detect_section_key(self, text: str) -> str:
        """Heurística para detectar qual seção o usuário quer escrever ou editar."""
        text = text.lower()
        mapping = {
            "introdução": "INTRODUCAO",
            "metodologia": "METODOLOGIA",
            "resultados": "RESULTADOS",
            "conclusão": "CONCLUSAO",
            "resumo": "RESUMO",
            "abstract": "ABSTRACT",
            "referências": "REFERENCIAS",
            "agradecimentos": "AGRADECIMENTOS"
        }
        
        # Busca explícita
        for kw, key in mapping.items():
            if kw in text:
                return key
        
        # Se não houver palavra-chave, mas estivemos editando uma seção recentemente
        # e o contexto parece de edição/escrita
        if st.session_state.get('last_active_section') and st.session_state.get('agente_ativo') == 'ESTRUTURADOR':
             if any(kw in text for kw in ["mais", "melhore", "corrija", "mude", "altere", "adicione", "remova"]):
                 return st.session_state['last_active_section']
                 
        return None

    def _limpar_conteudo_para_doc(self, text: str) -> str:
        """Remove conversas amigáveis da IA para salvar apenas o texto acadêmico."""
        import re
        # Remove saudações comuns e confirmações no início
        # Ex: "Com certeza! Aqui está o texto atualizado..."
        prefixes = [
            r"com certeza!.*[:\n]",
            r"aqui está.*[:\n]",
            r"claro!.*[:\n]",
            r"entendido.*[:\n]",
            r"excelente!.*[:\n]",
            r"atualizei.*[:\n]",
            r"com base no seu feedback.*[:\n]"
        ]
        cleansed = text
        for p in prefixes:
            cleansed = re.sub(p, "", cleansed, flags=re.IGNORECASE | re.DOTALL)
            
        # Tenta pegar apenas o que está em blocos de markdown ou após um cabeçalho se houver
        # Mas em geral, se o agente seguir o ESTRUTURADOR_SYSTEM_PROMPT, ele gera um bloco limpo.
        return cleansed.strip()

    def _is_global_query(self, input_usuario: str, agente_ativo: str) -> bool:
        """Detecta se a pergunta exige análise de todos os documentos."""
        # Regra 1: Se o agente for o Estruturador, ele precisa de visão global para propor capítulos.
        if agente_ativo == 'ESTRUTURADOR':
            return True
            
        # Regra 2: Keywords que indicam visão geral
        keywords_globais = [
            "todos", "cada um", "resumo geral", "comparativo", 
            "quais são os artigos", "lista de artigos", "panorama"
        ]
        input_lower = input_usuario.lower()
        if any(kw in input_lower for kw in keywords_globais):
            return True
            
        return False

    def classificar_e_atualizar_estado(self, input_usuario: str):
        """Usa o LLM para classificar a intenção e atualizar o st.session_state['agente_ativo']."""
        # Proteção 1: Se estivermos em loop de refinamento ou estruturando, mantemos o estado
        # até que o usuário aprove ou mude explicitamente (via botões na UI)
        estado_atual = st.session_state.get('agente_ativo')
        if estado_atual in ['AGUARDANDO_APROVACAO', 'ESTRUTURADOR']:
            st.session_state['agente_ativo'] = 'ESTRUTURADOR'
            return

        # Só classifica se for uma nova mensagem (prevenção de loop de tokens no rerun)
        last_classified = st.session_state.get('last_input_classified')
        if last_classified == input_usuario:
            return

        prompt_classificador = """Analise o último input do usuário e classifique a intenção em uma única palavra:
- ESCRITA: O usuário quer criar, escrever, estruturar, PRODUZIR OU EDITAR um novo documento (mesmo que seja um "resumo acadêmico" novo).
- CONSULTA: O usuário quer tirar dúvidas sobre o conteúdo, pedir explicação ou análise dos documentos existentes.
- ORCHESTRATOR: Saudação, conversa fiada ou algo irrelevante para as funções acima.

CRITÉRIO DE DESEMPATAR: Se o usuário quer "ESCREVER" algo novo, a prioridade é ESCRITA.
Resposta (apenas a palavra):"""
        
        historico_resumo = "\n".join([f"{m['role']}: {m['content'][:150]}..." for m in self.mm.mensagens[-3:]])
        
        mensagens = [
            SystemMessage(content=prompt_classificador),
            HumanMessage(content=f"Histórico Recente:\n{historico_resumo}\n\nÚltimo Input: {input_usuario}")
        ]
        
        try:
            resposta_raw = self.llm.invoke(mensagens).content.strip().upper()
            st.session_state['last_input_classified'] = input_usuario
            
            # Busca as palavras-chave na resposta para ser mais resiliente
            if "ESCRITA" in resposta_raw:
                novo_estado = 'ESTRUTURADOR'
            elif "CONSULTA" in resposta_raw:
                novo_estado = 'QA'
            else:
                novo_estado = 'ORCHESTRATOR'

            # Heurística de Segurança: Se o LLM falhar, palavras óbvias forçam o estado
            input_lower = input_usuario.lower()
            if any(kw in input_lower for kw in ["escrever", "criar", "estruturar", "produzir", "redigir", "editar", "mudar", "alterar", "melhorar", "corrigir"]):
                novo_estado = 'ESTRUTURADOR'
            elif any(kw in input_lower for kw in ["pergunta", "dúvida", "quem", "o que", "onde", "quando", "resuma"]):
                if novo_estado == 'ORCHESTRATOR': # Só força se estiver indefinido
                    novo_estado = 'QA'
            
            # Log discreto para debug
            print(f"[TRIAGEM] Input: {input_usuario[:30]}... | Resposta: {resposta_raw} | Estado Final: {novo_estado}")
            st.session_state['agente_ativo'] = novo_estado
            
        except Exception as e:
            print(f"Erro na classificação: {e}")
            st.session_state['agente_ativo'] = 'ORCHESTRATOR'

    def _get_prompt_por_agente(self, agente: str) -> str:
        if agente == 'ESTRUTURADOR':
            return ESTRUTURADOR_SYSTEM_PROMPT
        elif agente == 'QA':
            return QA_SYSTEM_PROMPT
        return ORCHESTRATOR_SYSTEM_PROMPT

    def planejar_documento(self, objetivo: str) -> Generator[str, None, None]:
        """Mantido por compatibilidade."""
        yield from self.route_request(objetivo)

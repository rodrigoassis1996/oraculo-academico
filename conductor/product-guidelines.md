# Diretrizes do Produto: Oráculo Acadêmico

Este documento orienta a comunicação, o design e o vocabulário do ecossistema.

## Tom de Voz

O **Oráculo Acadêmico** deve se comunicar de forma:
-   **Profissional e Acadêmica**: Linguagem clara, objetiva e baseada em evidências.
-   **Assistencial**: Pronta para guiar o usuário, mas respeitando sua autonomia intelectual.
-   **Confiável**: Transparente sobre as fontes e limitações da IA.

## Glossário de Termos

-   **Maestro/Orquestrador**: Agente central que gerencia chats e coordena outros especialistas.
-   **RAG (Retrieval-Augmented Generation)**: Técnica que usa documentos carregados para fundamentar as respostas da IA.
-   **Triagem Inteligente**: Processo de distinguir se o usuário quer escrever, tirar dúvidas ou configurar o sistema.
-   **Escrita Seccional**: Geração de texto fragmentada por seções do sumário aprovado.

## Padrões de Design UI/UX

-   **Frontend**: Uso consistente de **Ant Design** (v6) para componentes estruturais (botões, modais, inputs).
-   **Layout**: Responsividade baseada em **TailwindCSS** (v4). Dark mode e light mode devem ser suportados.
-   **Streaming**: Feedback visual em tempo real para respostas de IA (uso de esqueletos de carregamento e cursors ativos).

## Mensagens de Erro

-   Erros técnicos de backend (ex: OAuth 401) devem apresentar soluções claras (ex: link de reautenticação) em vez de apenas códigos de erro.
-   Notificações de sistema devem ser discretas mas informativas.

---

> [!TIP]
> **Consistência Visual**: Use o `AntdConfigProvider` para garantir que temas e cores estejam alinhados em todo o aplicativo.

# Fluxos de Trabalho: Oráculo Acadêmico

Este documento descreve as práticas de desenvolvimento, padrões de colaboração e garantias de qualidade.

## Ciclo de Desenvolvimento (TDD-ish)

1.  **Contexto**: Iniciar cada tarefa lendo os artefatos em `conductor/`.
2.  **Especificação**: Definir o que será construído antes de codificar.
3.  **Implementação**: Escrever código acompanhado de testes unitários.
4.  **Verificação**: Garantir aprovação total na suíte de QA.

## Padrões de Código

-   **Python**: PEP 8, Type Hinting obrigatório em interfaces públicas e modelos.
-   **TypeScript**: Clean code em React, hooks personalizados para lógica de estado, Ant Design para componentes UI.

## Estratégia de Testes

-   **Testes Unitários**: Devem cobrir a lógica de negócio principal em `agents/` e `services/`.
-   **Testes de Integração**: Validar a comunicação entre agentes e o `RAGManager`.
-   **Testes E2E (End-to-End)**: Marcar com `@pytest.mark.e2e`. Requerem `credentials.json` válidas.

### Comandos de Teste

```bash
# Executar testes unitários e de integração
pytest -m "not e2e"

# Executar testes E2E
pytest -m e2e

# Executar testes de frontend
cd frontend && npm test
```

## Convenções de Commits

O projeto utiliza o padrão [Conventional Commits](https://www.conventionalcommits.org/):

-   `feat`: Nova funcionalidade.
-   `fix`: Correção de bug.
-   `docs`: Mudanças na documentação.
-   `style`: Mudanças de formatação/estilo (não afetam código).
-   `refactor`: Mudança de código que não corrige bug nem adiciona feature.
-   `test`: Adição ou correção de testes.

## Fluxo de Git

-   **`main`**: Ramo estável, sempre pronto para produção.
-   **Feature branches**: Criar ramos específicos para cada nova funcionalidade (`feat/nome-da-feature`).
-   **Pull Requests**: Devem passar por lint e testes antes do merge.

---

> [!IMPORTANT]
> **Qualidade é Primordial**: Nenhum código deve ser integrado se quebrar a suíte de testes existente.

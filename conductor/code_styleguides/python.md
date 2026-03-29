# Guia de Estilo: Python (FastAPI/LangChain)

Este documento estabelece as convenções de codificação para o backend do **Oráculo Acadêmico**.

## Regras Gerais

-   **PEP 8**: Siga rigorosamente as normas de estilo (uso de `flake8` ou `black` é recomendado).
-   **Docstrings**: Obrigatórias para classes e funções públicas (padrão Google).
-   **Módulos**: Mantenha arquivos pequenos e focados em uma única responsabilidade.

## Type Hinting

O uso de `typing` é obrigatório em:
-   Assinaturas de funções.
-   Instância de modelos `Pydantic`.
-   Estados de sessão (`Dict[str, Any]`).

```python
# Correto
def get_session(session_id: str) -> Dict[str, Any]:
    ...
```

## Padrões de FastAPI

-   **Depêndencias**: Use `Depends` para injeção de estado e serviços.
-   **Modelos**: Use `Pydantic (BaseModel)` para validação de entrada e saída da API.
-   **Exceptions**: Use `HTTPException` com códigos de status apropriados.

## Integração LangChain

-   **Prompts**: Mantenha os templates de prompts em `agents/prompts.py` para fácil manutenção e versionamento.
-   **Streaming**: Use geradores (`yield`) para respostas de streaming da IA.

## Testes

-   **Mocks**: Use `pytest-mock` para isolar chamadas de rede (OpenAI, Google APIs).
-   **Nomenclatura**: Arquivos de teste devem começar com `test_`.

---

> [!TIP]
> **Performance**: Use funções assíncronas (`async def`) quando realizar operações de I/O (banco de dados, requisições externas).

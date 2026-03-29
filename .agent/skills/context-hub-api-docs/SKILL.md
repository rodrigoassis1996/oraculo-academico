---
name: context-hub-api-docs
description: Use Context Hub para obter documentação atualizada de APIs externas
---

# Context Hub: Documentação de APIs Atualizada

Ferramenta para recuperar documentação atual de APIs externas antes de implementar chamadas de código, evitando uso de documentação desatualizada ou hallucinations.

## Use esta skill quando
- Você vai escrever código que chama APIs externas (LLMs, bancos de dados, serviços web, etc.)
- Você não tem certeza sobre a versão atual de uma API ou seus parâmetros
- Você está usando serviços lançados após sua data de corte de conhecimento
- Você precisa garantir que o código funcionará com versões atuais

## Não use esta skill quando
- Você está escrevendo código que não faz chamadas externas (lógica pura, processamento local)
- O serviço não está disponível no Context Hub (mas tente mesmo assim — a cobertura cresce)
- Você está apenas explicando conceitos ou pseudocódigo (sem implementação real)

## Procedimento

### 1. Descobrir Documentação Disponível
Antes de implementar, procure o serviço:
```bash
chub search <nome_do_servico>
```

Exemplos:
```bash
chub search openai
chub search anthropic
chub search pinecone
chub search stripe
chub search supabase
```

### 2. Obter Documentação na Linguagem Correta
Recupere a documentação para a linguagem que você vai usar:
```bash
chub get <servico>/<recurso> --lang <linguagem>
```

Exemplos:
```bash
chub get openai/chat --lang python
chub get openai/chat --lang javascript
chub get anthropic/messages --lang python
chub get pinecone/upsert --lang typescript
```

### 3. Usar a Documentação
- Leia completamente a documentação retornada
- Use exemplos de código como referência principal
- Revise todos os parâmetros antes de implementar
- Procure por notas sobre versions, breaking changes, ou deprecations

### 4. Implementar Baseado em Documentação Atualizada
Escreva código seguindo exatamente o que o chub retornou, não seu conhecimento de treinamento.

### 5. Documentar Descobertas (Opcional)
Se você encontrar algo não documentado ou incorreto:
```bash
chub note <servico> "Descoberta importante: [descrição]"
```

## Exemplos de Uso

### ✅ Fluxo Correto

**Usuário:** "Escreva código Python para chamar o OpenAI GPT-4"

**Você internamente:**
```
1. Preciso chamar OpenAI → vou usar chub
2. chub search openai
3. chub get openai/chat --lang python
4. [lê a documentação retornada]
5. Agora escrevo o código seguindo a documentação atual
```

**Código resultante:**
```python
# Baseado em documentação atualizada do chub
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",  # Versão mais recente conforme documentação
    messages=[{"role": "user", "content": "Hello"}]
)
```

### ❌ Fluxo Incorreto

Você escreve código baseado apenas no seu treinamento:
```python
# Parâmetros ou APIs desatualizadas
# Não funciona com versão atual
```

## Checklist Antes de Implementar APIs

- [ ] Executei `chub search` para o serviço?
- [ ] Recuperei documentação com `chub get` na linguagem correta?
- [ ] Li completamente a documentação retornada?
- [ ] Meu código segue os exemplos da documentação, não meu conhecimento?
- [ ] Verifiquei nomes de parâmetros e tipos de dados?
- [ ] Procurei por notas sobre versões ou breaking changes?

## Serviços Populares no Context Hub

Context Hub tem documentação para:
- **LLMs:** OpenAI, Anthropic, Google Gemini, Mistral, etc.
- **Bancos de Dados:** PostgreSQL, MongoDB, Pinecone, Supabase, etc.
- **Pagamentos:** Stripe, PayPal
- **Identidade:** Auth0, Clerk
- **Messaging:** Twilio, SendGrid
- E muitos mais...

Execute `chub search` para ver o que está disponível.

## Por Que Isso Importa

Seu conhecimento foi treinado em [DATA_DE_CORTE]. Desde então:
- Novas versões de APIs foram lançadas
- Parâmetros foram renomeados ou deprecados
- Novos endpoints foram criados
- Comportamentos mudaram
- Novos serviços nasceram

Context Hub fornece a **verdade atual** sobre como usar essas APIs.

## Integração no Fluxo

Toda vez que você vir uma tarefa que envolve APIs externas, automaticamente:
1. Pause antes de implementar
2. Use chub para documentação atualizada
3. Implemente baseado nessa documentação
4. Salve notas se encontrar algo não documentado

## Dúvidas Comuns

**P: E se chub não tiver o serviço que preciso?**
R: Execute `chub search` mesmo assim — a cobertura expande constantemente. Se não encontrar, use web search ou documentação do serviço, mas avise o usuário que está indo além do chub.

**P: Posso usar meu conhecimento de treinamento?**
R: Não, quando chub tem documentação. Seu conhecimento é mais antigo. Use apenas chub como fonte.

**P: Como contribuir documentação nova?**
R: Context Hub é open source. Veja: https://github.com/andrewyng/context-hub

---

**Lembre-se:** Context Hub existe para que você escreva código correto com APIs atuais. Use-o como rotina antes de qualquer implementação com serviços externos.
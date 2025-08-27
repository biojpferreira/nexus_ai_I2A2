# Agente de Automação de Benefícios VR/VA

## Visão Geral

Este projeto implementa um agente conversacional para automação de cálculos de benefícios VR (Vale Refeição) e VA (Vale Alimentação).
O agente é capaz de processar planilhas, realizar cálculos automatizados e responder perguntas em linguagem natural através de um chatbot no terminal.

---
## Funcionalidades

Processamento de Planilhas VR/VA: lê e interpreta dados das planilhas de benefícios.
Cálculo de VR Mensal: realiza automaticamente o cálculo de VR para um período solicitado.
Processamento de Funcionários: ferramenta para calcular os benefícios de todos os funcionários de uma vez.
Chatbot no Terminal: interação direta com o usuário em modo de perguntas e respostas.

---
## Estrutura do Projeto

**project/**
- **agent_vrva/**
  - `main.py` (código principal do agente)
  - `tools.py` (ferramentas auxiliares)
- **data/** (arquivos de entrada, como planilhas VR/VA)
- **logs/** (logs gerados automaticamente)
- `requirements.txt`
  
---
## Dependências

* Python 3.10+
* Bibliotecas:
* langchain
* langchain-google-genai
* pandas
* tabulate
* argparse
* logging

## Instalação: 
```pip install -r requirements.txt```

---
## Uso

Execução no terminal:

```bash python agent_vrva/main.py```

Durante a execução, o agente permite interação direta em formato de chatbot.
Digite suas perguntas no terminal e use exit para encerrar a sessão.

---
## Tratamento de Erros

O agente possui tratamento para:
Arquivos não encontrados
Erros de permissão
Erros de valores
Exceções genéricas

---
## Logging

Salvo em arquivo (logs/) e exibido em stdout.
Formato: [2025-08-27 10:00:00] [agent_vrva] INFO: Mensagem

---

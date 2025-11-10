# 🤖 Agente para atendimento whatsapp

Sistema de chatbot inteligente para WhatsApp utilizando CrewAI e Flask, com integração via Uazapi para automação de atendimento com foco em vendas de leads AVCB/CLCB. O Agente possui memória persistente, buffer de mensagem e RAG.

## 📋 Sobre o Projeto

Este projeto implementa um agente de IA conversacional que atua como assistente de vendas no WhatsApp. O bot responde automaticamente as mensagens dos clientes de forma amigável e contextualizada, 
usa consulta com RAG para verificar os itens disponiveis e a quantidade conforme a solicitação do cliente. O agente também consegue identificar e ler documentos PDF, imagem e Audio.

**OBS:** 
- Caso queira, pode ser utilizado em **VPS**

## ⚠️ IMPORTANTE ⚠️
- Não utilize este modelo em produção! Faça as alterações necessárias.

## 🔄 Fluxo de Funcionamento

1. Usuário envia mensagem de texto, audio, PDF ou imagem no WhatsApp
2. Uazapi recebe a mensagem e envia para o webhook
3. Flask valida e processa a requisição (no caso de multiplas mensagens, aciona o buffer)
4. Bot simula digitação e processa com IA (acessa o RAG caso necessário)
5. Retorna a mensagem do Agente para o cliente via Uazapi (somente texto)

### Tecnologias Utilizadas

- **CrewAI** - Orquestração do agente de IA
- **OpenAI GPT-4o-mini** - Modelo de linguagem
- **Flask** - API de webhook
- **Uazapi** - Integração com WhatsApp
- **Docker Compose** - Containerização
- **Ngrok** - Tunnel para webhook
- **mem0** - Gerenciador para memória vetorial persistente
- **qdrant** - Banco de dados vetorial (Vector Base) para busca semântica (Vector Search)

**OBS:**
Outras tecnologias foram testadas e aplicadas:
- **HUGGINGFACE** - Caso queira utilizar para fazer RAG ou banco de dados
- **EVO API ou Waha** - Caso queira usar API localhosted
- **Supabase** - Para RAG/banco de dados, memoria do agente e outros. - Não recomendado, pois há integração nativa com mem0 e qdrant, sendo assim o consumo de tokens acaba sendo menor.

- ## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Docker e Docker Compose instalados
- Conta ativa na Uazapi (A API fornece servidor gratuíto para testes)
- Chave API da OpenAI
- Ngrok instalado (ou alternativa de tunnel)

- ### Passo 1: Clone o Repositório

```bash
git clone <url-do-repositorio>
cd <nome-do-projeto>

```bash
# Criar o ambiente virtual
python -m venv .venv

# Ativar o ambiente virtual
# No Linux/Mac:
source .venv/bin/activate

# No Windows:
.venv\Scripts\activate (ou .bat / ps1)
```

### Passo 3: Instale as Dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
OPENAI_API_KEY=sua-chave-api-openai
UAZAPI_TOKEN=seu-token-uazapi
UAZAPI_URL=sua-instancia-uazapi
QDRANT_HOST=localhost
QDRANT_PORT=6333
MEM0_API_KEY = m0-sua-api-key
```

**Importante:** Nunca commite o arquivo `.env` no repositório!

## 🐳 Executando com Docker

### Subir os Containers

```bash
# Buildar e iniciar os containers
docker-compose up --build -d
```

### Verificar Status dos Containers

```bash
# Ver containers em execução
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f chatbot
```

### Parar os Containers

```bash
# Parar os containers
docker-compose down

# Parar e remover volumes
docker-compose down -v
```

### Reconstruir Após Alterações

```bash
# Rebuild e restart
docker-compose up --build -d
```

## 🌐 Configurando o Tunnel

O webhook precisa ser acessível publicamente. Configure um tunnel para expor sua aplicação local.

### Opção 1: Usando Ngrok (Recomendado)

1. Baixe e instale o Ngrok: https://ngrok.com/download

2. Inicie o tunnel apontando para a porta 5000:

```bash
ngrok http 5000
```

3. Copie a URL gerada (exemplo: `https://abc123.ngrok.io`)

4. Use esta URL para configurar o webhook na Uazapi

**IMPORTANTE:** O Ngrok no plano **FREE** não fornece **URL** do Tunnel estático, então todas as vezes que iniciar, terá que alterar manualmente na **API UAZAPI**. Pode criar um script também que captura o **URL** gerado dinamicamente pelo NGROK e fazer **POST** na **API** para atualizar dinamicamente.

6. ### Opção 2: Cloudflare Tunnel

```bash
# Instalar cloudflared (Linux)
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Criar tunnel
cloudflared tunnel --url http://localhost:5000
```

## ⚙️ Configuração do Webhook na Uazapi

1. Acesse o painel da Uazapi
2. Navegue até a seção de **Webhooks**
3. Configure os seguintes parâmetros:
   - **URL do Webhook:** `https://sua-url-do-tunnel/chatbot/webhook/`
   - **Método:** POST
   - **Eventos:** Marque a opção "Mensagens"
4. Salve as configurações
5. Teste enviando uma mensagem para o número conectado

## 🏃 Executando Localmente (Sem Docker)

Se preferir executar sem Docker:

```bash
# Ative o ambiente virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Execute a aplicação
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

## 🐛 Troubleshooting

### O webhook não recebe mensagens

- Verifique se o tunnel (Ngrok) está ativo e rodando
- Confirme se a URL no painel da Uazapi está correta
- Verifique os logs do container: `docker-compose logs -f`

### Erro de autenticação OpenAI

- Verifique se a variável `OPENAI_API_KEY` está no arquivo `.env`
- Confirme que a chave API é válida e tem créditos

### Container não inicia

- Verifique os logs de erro: `docker-compose logs chatbot`
- Reconstrua a imagem: `docker-compose up --build`
- Verifique se as portas não estão em uso: `lsof -i :5000`

- ### Mensagens não estão sendo respondidas

- Confirme que o bot não está respondendo mensagens próprias (fromMe)
- Verifique se o evento recebido é do tipo "messages"
- Analise os logs para identificar erros no processamento

## 📊 Monitoramento

### Ver Logs em Tempo Real

```bash
docker-compose logs -f chatbot
```

## 🔒 Segurança

- Nunca commite o arquivo `.env` no repositório
- Mantenha suas chaves API seguras e privadas
- Use variáveis de ambiente para todas as credenciais
- Revogue tokens comprometidos imediatamente

## 🏗️ Modelo Visual

[comentário]: # ![Schema do Agente AI](assets/Schema_AgenteAI.png)



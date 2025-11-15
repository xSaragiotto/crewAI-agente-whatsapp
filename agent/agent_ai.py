from crewai import Agent, Task, Crew, LLM
from crewai.memory.external.external_memory import ExternalMemory
from qdrant_client import QdrantClient
# from agent.agent_memory import QdrantChatStorage
from agent.supabase_rag_tool import SupabaseRAGTool
from dotenv import load_dotenv
import os

load_dotenv() # Carrega variáveis do arquivo .env

class BotVania:  # Agent AI

    def __init__(self, user_id: str):
        api_key = os.environ.get('OPENAI_API_KEY')  # Pega a chave do .env
        self.__llm = LLM(model='gpt-4o-mini', temperature=0.7, api_key=api_key)  # Configura o LLM

        self.memory = ExternalMemory(  # Usando mem0 + qdrant para acessar memória semântica
            embedder_config={
                'provider': 'mem0',
                'config': {
                    'user_id': user_id,
                    'local_mem0_config': {
                        'vector_store': {
                            'provider': 'qdrant',
                            'config': {
                                'host': os.environ.get('QDRANT_HOST', 'qdrant'),
                                'port': int(os.environ.get('QDRANT_PORT', 6333))
                            }
                        }
                    },
                    'infer': True
                }
            }
        )
        print(f"[DEBUG] user_id recebido: {user_id} ({type(user_id)})")  # Log

        # Test memory (não utilizado no projeto final)
        """
        Arquivo de teste para o modelo de memória do agente.
        Este bloco é mantido apenas para referência e testes locais.

        self.memory = ExternalMemory(
            storage=QdrantChatStorage(
                user_id,
                host=os.environ.get('QDRANT_HOST', 'localhost'),
                port=int(os.environ.get('QDRANT_PORT', 6333))
            )
        )
        """

        self.agent = Agent(
            role="Especialista em Vendas",
            goal="Ajudar clientes com AVCB/CLCB de forma clara e eficiente",
            backstory="""Você é Vania Franco, especialista da Nakaya Engenharia.
            Você responde de forma amigável e simpática, sempre em no máximo 200 caracteres.
            Você tem expertise em AVCB/CLCB e ajuda clientes com clareza.""",
            llm=self.__llm,
            tools=[SupabaseRAGTool()],
            verbose=True # Logs
        )
        
        resposta_padrao = Task(
            description='Responda a pergunta do usuário: {question}. Use a ferramenta de busca quando precisar consultar informações sobre AVCB e CLCB no banco de dados.',
            expected_output='Resposta clara, amigável e com máximo 200 caracteres',
            agent=self.agent
        )

        self.crew = Crew(
            agents=[self.agent],
            tasks=[resposta_padrao],
            external_memory=self.memory # Memoria LLM
        )

    def kickoff(self, question: str):
        # prompt = f"""
        # Você é vania Sales, especialista em vendas de AVCB/CLCB da Nakaya Engenharia.
        # Sempre responda de forma amigável e simpatica, no maximo 200 caracteres.
        # <texto>
        # {question}
        # </texto>
        # """
        return self.crew.kickoff(inputs={'question': question})

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from supabase import create_client
import os
import openai

class SupabaseRAGInput(BaseModel):
    query: str = Field(..., description="Consulta para buscar no RAG")

class SupabaseRAGTool(BaseTool):
    name: str = "Supabase RAG Search"
    description: str = "Busca informações no banco documents_duplicate do Supabase"
    args_schema: type[BaseModel] = SupabaseRAGInput
    
    def _run(self, query: str) -> str:
        # 1. Conectar ao Supabase
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        # 2. Gerar embedding da query
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = response.data[0].embedding
        
        # 3. Buscar usando sua função RPC
        result = supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_count': 5,
                'filter': {}  # Adicione filtros se necessário
            }
        ).execute()
        
        # 4. Retornar conteúdo
        if result.data:
            docs = "\n\n".join([doc['content'] for doc in result.data])
            return docs
        return "Nenhum resultado encontrado."
import os
import chromadb
from chromadb.config import Settings
import google.genai as genai
from typing import List, Dict

from dotenv import load_dotenv
load_dotenv()

# Make sure GOOGLE_API_KEY is available in the environment
API_KEY = os.environ.get("GOOGLE_API_KEY")

class GeminiEmbeddingFunction(chromadb.EmbeddingFunction):
    """
    Custom embedding function for ChromaDB that uses Google's Gemini text-embedding-004.
    """
    def __init__(self, api_key: str):
        if not api_key:
            print("WARNING: GOOGLE_API_KEY is not set. Vector sync/retrieval will fail.")
        self._api_key = api_key
        self._client = genai.Client(api_key=api_key) if api_key else None

    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        """
        Embed a list of text documents into vector representations using Gemini.
        Uses batch embedding for efficiency, with exponential backoff on rate limits.
        """
        if not self._client:
            raise ValueError("Google API key is missing. Cannot generate embeddings.")

        import time
        all_embeddings = []
        BATCH_SIZE = 20  # Conservative batch size for rate limiting
        BATCH_DELAY = 6  # seconds between batches (respects 10 RPM free tier)
        MAX_RETRIES = 5

        for i, batch_start in enumerate(range(0, len(input), BATCH_SIZE)):
            batch = input[batch_start:batch_start + BATCH_SIZE]
            
            # Add a polite delay between batches (except before the first one)
            if i > 0:
                time.sleep(BATCH_DELAY)
            
            for attempt in range(MAX_RETRIES):
                try:
                    response = self._client.models.embed_content(
                        model="gemini-embedding-001",
                        contents=list(batch),
                        config={"task_type": "RETRIEVAL_DOCUMENT"}
                    )
                    for emb in response.embeddings:
                        all_embeddings.append(emb.values)
                    break  # success, move to next batch
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        wait_time = (2 ** attempt) * 10  # 10s, 20s, 40s, 80s, 160s
                        print(f"Rate limit hit. Retrying in {wait_time}s (attempt {attempt+1}/{MAX_RETRIES})...")
                        time.sleep(wait_time)
                    else:
                        raise
            else:
                raise RuntimeError(f"Embedding failed after {MAX_RETRIES} retries due to rate limiting.")

        return all_embeddings

class VectorDBService:
    def __init__(self):
        self.client = None
        self.embedding_function = None
        self.collection_name = "promptboost_projects"
        self._initialize()

    def _initialize(self):
        """Initialize local ChromaDB client and Gemini embedding function."""
        try:
            # Persistent storage in the server directory
            persist_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_data")
            os.makedirs(persist_directory, exist_ok=True)
            
            self.client = chromadb.PersistentClient(path=persist_directory)
            if API_KEY:
                self.embedding_function = GeminiEmbeddingFunction(api_key=API_KEY)
            print("✅ Vector DB Service initialized successfully.")
        except Exception as e:
            import traceback
            print(f"❌ Failed to initialize Vector DB: {e}")
            traceback.print_exc()

    def is_ready(self) -> bool:
        return self.client is not None and self.embedding_function is not None

    def upsert_project_documents(self, project_id: str, documents: List[str], metadatas: List[Dict], ids: List[str]):
        """
        Wipes existing project vectors and replaces them with a fresh sync.
        """
        if not self.is_ready():
            raise RuntimeError("Vector DB not ready.")
            
        # Get or create the master collection
        collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
        
        # 1. Delete old documents for this project to avoid duplicates on resync
        try:
            collection.delete(where={"project_id": project_id})
        except Exception:
            pass # collection might be empty
            
        # 2. Add the new documents
        # We enforce that every metadata gets the project_id flag for proper filtering later
        for meta in metadatas:
            meta["project_id"] = project_id
            
        # Chroma handles the embedding automatically using our GeminiEmbeddingFunction
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully synced {len(documents)} chunks for project {project_id}.")

    def query_project_context(self, project_id: str, query_text: str, n_results: int = 5) -> str:
        """
        Retrieve the top N most relevant code chunks for a specific prompt.
        """
        if not self.is_ready():
            print("Vector DB missing or API key absent. Skipping RAG.")
            return ""
            
        try:
            collection = self.client.get_collection(
                name=self.collection_name, 
                embedding_function=self.embedding_function
            )
            
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={"project_id": project_id} # Critical: only search within this project
            )
            
            if not results['documents'] or not results['documents'][0]:
                return ""
                
            # Compile chunks into a single readable context string for the LLM
            context_parts = []
            for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                filename = meta.get('filename', 'Unknown File')
                context_parts.append(f"--- File: {filename} ---\n{doc}")
                
            return "\n\n".join(context_parts)
            
        except Exception as e:
            print(f"Error querying Vector DB: {e}")
            return ""

# Global singleton instance to be imported by endpoints
vector_db = VectorDBService()

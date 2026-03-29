"""
RAG Agent - Advanced version with Elasticsearch and document processing
"""
import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

# Elasticsearch
try:
    from elasticsearch import Elasticsearch, exceptions
    ES_AVAILABLE = True
except ImportError:
    ES_AVAILABLE = False
    print("Elasticsearch not installed")

# Document processing
try:
    import pdfplumber
    from docx import Document
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Sentence transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

# LLM Integration
try:
    from gigachat import GigaChat
    from gigachat.models import Chat, Messages, Message
    GIGACHAT_AVAILABLE = True
except ImportError:
    GIGACHAT_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class RAGAgentAdvanced:
    """
    Advanced RAG Agent with:
    - Elasticsearch vector search
    - Document upload (PDF, DOCX, TXT)
    - LLM integration (GigaChat / OpenAI)
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.name = "RAG Agent Advanced"
        self.version = "2.0.0"
        self.config = config or {}
        
        # Initialize Elasticsearch
        self.es = None
        self.index_name = self.config.get("es_index", "knowledge_base")
        self._init_elasticsearch()
        
        # Initialize embeddings model
        self.embedding_model = None
        self._init_embeddings()
        
        # Initialize LLM
        self.llm = None
        self.llm_type = self.config.get("llm_type", "gigachat")  # or "openai"
        self._init_llm()
        
        # Document storage
        self.upload_dir = self.config.get("upload_dir", "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)
        
        print(f"✅ {self.name} v{self.version} initialized")
        print(f"   Elasticsearch: {'✅' if self.es else '❌'}")
        print(f"   Embeddings: {'✅' if self.embedding_model else '❌'}")
        print(f"   LLM ({self.llm_type}): {'✅' if self.llm else '❌'}")
    
    def _init_elasticsearch(self):
        """Initialize Elasticsearch connection"""
        if not ES_AVAILABLE:
            return
        
        try:
            es_host = self.config.get("es_host", "localhost")
            es_port = self.config.get("es_port", 9200)
            
            self.es = Elasticsearch([f"http://{es_host}:{es_port}"])
            
            # Check connection
            if self.es.ping():
                print(f"Connected to Elasticsearch at {es_host}:{es_port}")
                self._create_index()
            else:
                print("Cannot connect to Elasticsearch")
                self.es = None
        except Exception as e:
            print(f"Elasticsearch error: {e}")
            self.es = None
    
    def _create_index(self):
        """Create Elasticsearch index with vector mapping"""
        if not self.es:
            return
        
        # Check if index exists
        if not self.es.indices.exists(index=self.index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "title": {"type": "text"},
                        "content": {"type": "text"},
                        "content_vector": {
                            "type": "dense_vector",
                            "dims": 384,  # For sentence-transformers/all-MiniLM-L6-v2
                            "index": True,
                            "similarity": "cosine"
                        },
                        "file_name": {"type": "keyword"},
                        "file_type": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "tags": {"type": "keyword"},
                        "source": {"type": "keyword"}
                    }
                }
            }
            self.es.indices.create(index=self.index_name, body=mapping)
            print(f"Created index: {self.index_name}")
    
    def _init_embeddings(self):
        """Initialize sentence transformer model"""
        if not EMBEDDINGS_AVAILABLE:
            return
        
        try:
            model_name = self.config.get("embedding_model", "all-MiniLM-L6-v2")
            self.embedding_model = SentenceTransformer(model_name)
            print(f"Loaded embeddings model: {model_name}")
        except Exception as e:
            print(f"Embeddings error: {e}")
    
    def _init_llm(self):
        """Initialize LLM (GigaChat or OpenAI)"""
        if self.llm_type == "gigachat" and GIGACHAT_AVAILABLE:
            try:
                credentials = self.config.get("gigachat_credentials", os.getenv("GIGACHAT_CREDENTIALS"))
                if credentials:
                    self.llm = GigaChat(credentials=credentials, verify_ssl_certs=False)
                    print("GigaChat initialized")
                else:
                    print("GigaChat credentials not found")
            except Exception as e:
                print(f"GigaChat error: {e}")
        
        elif self.llm_type == "openai" and OPENAI_AVAILABLE:
            try:
                api_key = self.config.get("openai_api_key", os.getenv("OPENAI_API_KEY"))
                if api_key:
                    self.llm = OpenAI(api_key=api_key)
                    print("OpenAI initialized")
                else:
                    print("OpenAI API key not found")
            except Exception as e:
                print(f"OpenAI error: {e}")
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if not self.embedding_model:
            return []
        
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"Embedding error: {e}")
            return []
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            return ""
        
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return ""
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"DOCX extraction error: {e}")
            return ""
    
    def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"TXT extraction error: {e}")
            return ""
    
    def upload_document(self, file_path: str, metadata: Dict = None) -> Dict:
        """
        Upload and index a document
        
        Args:
            file_path: Path to the document
            metadata: Additional metadata (tags, source, etc.)
        
        Returns:
            Dict with upload status
        """
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        # Get file extension
        ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)
        
        # Extract text based on file type
        text = ""
        if ext == '.pdf':
            text = self._extract_text_from_pdf(file_path)
        elif ext == '.docx':
            text = self._extract_text_from_docx(file_path)
        elif ext == '.txt':
            text = self._extract_text_from_txt(file_path)
        else:
            return {"error": f"Unsupported file type: {ext}"}
        
        if not text:
            return {"error": "Could not extract text from document"}
        
        # Split into chunks (simple chunking)
        chunk_size = 500
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        # Index each chunk
        indexed_chunks = []
        for i, chunk in enumerate(chunks):
            doc_id = hashlib.md5(f"{file_name}_{i}".encode()).hexdigest()
            
            document = {
                "title": file_name,
                "content": chunk,
                "file_name": file_name,
                "file_type": ext,
                "created_at": datetime.now().isoformat(),
                "tags": metadata.get("tags", []) if metadata else [],
                "source": metadata.get("source", "upload") if metadata else "upload"
            }
            
            # Add embedding
            if self.embedding_model:
                document["content_vector"] = self._get_embedding(chunk)
            
            # Index in Elasticsearch
            if self.es:
                try:
                    self.es.index(index=self.index_name, id=doc_id, body=document)
                    indexed_chunks.append({"chunk": i, "id": doc_id})
                except Exception as e:
                    print(f"Indexing error: {e}")
        
        return {
            "success": True,
            "file_name": file_name,
            "file_type": ext,
            "chunks": len(chunks),
            "indexed_chunks": len(indexed_chunks)
        }
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of relevant documents
        """
        if not self.es:
            return []
        
        # Generate query embedding
        query_embedding = self._get_embedding(query)
        
        if query_embedding:
            # Vector search
            search_body = {
                "size": top_k,
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'content_vector') + 1.0",
                            "params": {"query_vector": query_embedding}
                        }
                    }
                }
            }
        else:
            # Text search
            search_body = {
                "size": top_k,
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^2", "content", "tags"]
                    }
                }
            }
        
        try:
            response = self.es.search(index=self.index_name, body=search_body)
            results = []
            for hit in response["hits"]["hits"]:
                results.append({
                    "score": hit["_score"],
                    "title": hit["_source"].get("title", ""),
                    "content": hit["_source"].get("content", ""),
                    "source": hit["_source"].get("source", ""),
                    "tags": hit["_source"].get("tags", [])
                })
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def generate_answer(self, query: str, context: List[str]) -> str:
        """
        Generate answer using LLM
        
        Args:
            query: User question
            context: Retrieved context documents
        
        Returns:
            Generated answer
        """
        if not self.llm:
            return self._generate_fallback_answer(query, context)
        
        # Prepare prompt
        context_text = "\n\n".join(context[:3])  # Use top 3 contexts
        
        prompt = f"""You are a helpful assistant. Answer the question based on the context provided.

Context:
{context_text}

Question: {query}

Answer:"""
        
        try:
            if self.llm_type == "gigachat":
                # GigaChat API
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
                response = self.llm.chat(messages)
                return response.choices[0].message.content
            
            elif self.llm_type == "openai":
                # OpenAI API
                response = self.llm.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content
            
        except Exception as e:
            print(f"LLM error: {e}")
            return self._generate_fallback_answer(query, context)
    
    def _generate_fallback_answer(self, query: str, context: List[str]) -> str:
        """Generate fallback answer without LLM"""
        if not context:
            return f"I couldn't find relevant information about '{query}'. Please try rephrasing your question."
        
        answer = f"📚 **Found information about: {query}**\n\n"
        for i, ctx in enumerate(context[:3], 1):
            answer += f"**{i}.** {ctx[:200]}...\n\n"
        answer += "\n💡I can provide more details if you have specific questions."
        return answer
    
    def process(self, message: str, context: Dict = None) -> str:
        """
        Process user query
        
        Args:
            message: User query
            context: Additional context
        
        Returns:
            Response
        """
        # Search for relevant documents
        results = self.search(message, top_k=5)
        
        if not results:
            return f"I couldn't find relevant information about '{message}'. Try uploading documents or rephrasing your question."
        
        # Extract contexts
        contexts = [r["content"] for r in results]
        
        # Generate answer
        answer = self.generate_answer(message, contexts)
        
        # Add sources
        sources = "\n".join([f"- {r['title']} (score: {r['score']:.2f})" for r in results[:3]])
        answer += f"\n\n**Sources:**\n{sources}"
        
        return answer
    
    def get_stats(self) -> Dict:
        """Get agent statistics"""
        stats = {
            "name": self.name,
            "version": self.version,
            "elasticsearch": self.es is not None,
            "embeddings": self.embedding_model is not None,
            "llm": self.llm is not None,
            "llm_type": self.llm_type if self.llm else None
        }
        
        if self.es:
            try:
                count = self.es.count(index=self.index_name)
                stats["documents_count"] = count["count"]
            except:
                stats["documents_count"] = 0
        
        return stats


# Example usage
if __name__ == "__main__":
    print("Testing Advanced RAG Agent")

    # Initialize agent
    agent = RAGAgentAdvanced(config={
        "llm_type": "gigachat",  # or "openai"
        "es_host": "localhost",
        "es_port": 9200
    })
    
    # Test search
    response = agent.process("What is Kubernetes?")
    print(f"\nResponse:\n{response}")
    
    # Show stats
    print(f"\nStats: {agent.get_stats()}")
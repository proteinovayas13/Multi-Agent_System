"""
RAG Agent with Elasticsearch REST API
"""
import requests
import json
import os
import hashlib

class RAGAgentRest:
    def __init__(self, es_url="http://host.minikube.internal:9200", index_name="knowledge_base"):
        self.es_url = es_url
        self.index_name = index_name
        self.connected = False
        self._connect()
    
    def _connect(self):
        """Connect to Elasticsearch"""
        try:
            response = requests.get(f"{self.es_url}", timeout=5)
            if response.status_code == 200:
                self.connected = True
                print(f"✅ Connected to Elasticsearch at {self.es_url}")
                self._create_index()
            else:
                print(f"⚠️ Elasticsearch returned status {response.status_code}")
        except Exception as e:
            self.connected = False
            print(f"❌ Cannot connect to Elasticsearch: {e}")
            print("Make sure Elasticsearch is running:")
            print("docker run -d -p 9200:9200 -e discovery.type=single-node elasticsearch:8.11.0")
    
    def _create_index(self):
        """Create index if it doesn't exist"""
        if not self.connected:
            return
        
        try:
            response = requests.head(f"{self.es_url}/{self.index_name}")
            if response.status_code == 404:
                mapping = {
                    "mappings": {
                        "properties": {
                            "title": {"type": "text", "analyzer": "standard"},
                            "content": {"type": "text", "analyzer": "standard"},
                            "created_at": {"type": "date"}
                        }
                    }
                }
                response = requests.put(
                    f"{self.es_url}/{self.index_name}",
                    json=mapping,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    print(f"✅Created index: {self.index_name}")
                else:
                    print(f"⚠️ Failed to create index: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error creating index: {e}")
    
    def add_document(self, title, content, doc_id=None):
        """Add a document to the index"""
        if not self.connected:
            print(f"⚠️ Cannot add document: not connected to Elasticsearch")
            return False
        
        doc = {"title": title, "content": content}
        if doc_id is None:
            doc_id = hashlib.md5(title.encode()).hexdigest()[:16]
        
        try:
            response = requests.post(
                f"{self.es_url}/{self.index_name}/_doc/{doc_id}",
                json=doc,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code in [200, 201]:
                print(f"✅ Added document: {title}")
                return True
            else:
                print(f"⚠️ Failed to add document: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error adding document: {e}")
            return False
    
    def search(self, query, top_k=3):
        """Search for relevant documents"""
        if not self.connected:
            return []
        
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^2", "content"],
                    "fuzziness": "AUTO"
                }
            },
            "size": top_k
        }
        
        try:
            response = requests.post(
                f"{self.es_url}/{self.index_name}/_search",
                json=search_body,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                results = response.json()
                hits = results.get('hits', {}).get('hits', [])
                return [{
                    "title": hit['_source'].get('title', ''),
                    "content": hit['_source'].get('content', ''),
                    "score": hit.get('_score', 0)
                } for hit in hits]
            return []
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def process(self, message, context=None):
        """Process user query"""
        if not self.connected:
            return "⚠️ Elasticsearch is not connected. Please start Elasticsearch."
        
        results = self.search(message)
        
        if not results:
            return f"I couldn't find information about '{message}'. Please upload relevant documents."
        
        answer = f"📚 **Information about: {message}**\n\n"
        for i, result in enumerate(results, 1):
            answer += f"**{i}. {result['title']}** (score: {result['score']:.2f})\n"
            answer += f"{result['content'][:300]}\n\n"
        
        return answer
    
    def add_sample_data(self):
        """Add sample data to the index"""
        if not self.connected:
            print("⚠️ Cannot add sample data: not connected to Elasticsearch")
            return 0
        
        samples = [
            ("Kubernetes", "Kubernetes is a container orchestration platform for automating deployment, scaling, and management of containerized applications."),
            ("LangGraph", "LangGraph is a library for building stateful, multi-agent LLM applications with cycles and conditional branching."),
            ("Docker", "Docker is a platform for developing, shipping, and running applications in containers."),
            ("Python", "Python is a high-level programming language for general-purpose programming.")
        ]
        
        count = 0
        for title, content in samples:
            if self.add_document(title, content):
                count += 1
        print(f"Added {count} sample documents")
        return count
    
    def get_documents_count(self):
        """Get number of documents in index"""
        if not self.connected:
            return 0
        try:
            response = requests.get(f"{self.es_url}/{self.index_name}/_count")
            if response.status_code == 200:
                return response.json().get('count', 0)
            return 0
        except:
            return 0
    
    def delete_all_documents(self):
        """Delete all documents from index"""
        if not self.connected:
            return False
        try:
            response = requests.post(
                f"{self.es_url}/{self.index_name}/_delete_by_query",
                json={"query": {"match_all": {}}},
                headers={"Content-Type": "application/json"}
            )
            return response.status_code == 200
        except:
            return False


# Test
if __name__ == "__main__":

    print("Testing RAG Agent with Elasticsearch")

    # Initialize agent
    agent = RAGAgentRest()
    
    if agent.connected:
        # Add sample data
        agent.add_sample_data()
        
        # Test search
        queries = ["What is Kubernetes?", "Tell me about LangGraph", "Docker"]
        
        for q in queries:
            print(f"\n📝 Query: {q}")
            response = agent.process(q)
            print(response)
        
        print(f"\n📊Total documents: {agent.get_documents_count()}")
    else:
        print("\n⚠️Please start Elasticsearch first:")
        print("docker run -d -p 9200:9200 -e discovery.type=single-node elasticsearch:8.11.0")
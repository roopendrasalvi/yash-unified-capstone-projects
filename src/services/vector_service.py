"""
Vector Service
Handles vector database operations (Pinecone and Milvus)
"""

from typing import List, Dict, Any, Optional
import pinecone
from pinecone import ServerlessSpec
from pymilvus import Collection, FieldSchema, CollectionSchema, DataType, connections, utility
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import Pinecone
from langchain_classic.chains import RetrievalQA
from langchain_litellm import ChatLiteLLMRouter
from litellm import Router
from src.services.embedding_service import EmbeddingService
from config.config_loader import get_vector_db_config, get_model_config
import os
import logging

logger = logging.getLogger(__name__)


class VectorService:
    """Service for vector database operations"""
    
    def __init__(self):
        """Initialize the Vector Service"""
        self.vector_config = get_vector_db_config()
        self.model_config = get_model_config()
        self.embedding_service = EmbeddingService()
        self.pinecone_client = None
        self.milvus_connected = False
        logger.info("Vector Service initialized")
    
    # ==================== Pinecone Operations ====================
    
    def setup_pinecone(self) -> pinecone.Pinecone:
        """
        Setup Pinecone client
        
        Returns:
            Pinecone client instance
        """
        if self.pinecone_client is None:
            pinecone_config = self.vector_config.get("pinecone", {})
            api_key = pinecone_config.get("api_key")
            
            self.pinecone_client = pinecone.Pinecone(api_key=api_key)
            logger.info("Pinecone client initialized")
        
        return self.pinecone_client
    
    def create_pinecone_index(self, index_name: Optional[str] = None) -> str:
        """
        Create a Pinecone index if it doesn't exist
        
        Args:
            index_name: Name of the index (uses default if None)
            
        Returns:
            Index name
        """
        try:
            pc = self.setup_pinecone()
            pinecone_config = self.vector_config.get("pinecone", {})
            index_config = pinecone_config.get("index", {})
            
            if index_name is None:
                index_name = index_config.get("name", "email-embeddings")
            
            # Check if index exists
            if index_name not in pc.list_indexes().names():
                spec_config = index_config.get("spec", {})
                
                pc.create_index(
                    name=index_name,
                    dimension=index_config.get("dimension", 1536),
                    metric=index_config.get("metric", "cosine"),
                    spec=ServerlessSpec(
                        cloud=spec_config.get("cloud", "aws"),
                        region=spec_config.get("region", "us-east-1")
                    )
                )
                logger.info(f"Created Pinecone index: {index_name}")
            else:
                logger.info(f"Pinecone index already exists: {index_name}")
            
            return index_name
            
        except Exception as e:
            logger.error(f"Error creating Pinecone index: {str(e)}")
            raise
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        splitter_config = self.vector_config.get("pinecone", {}).get("text_splitter", {})
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=splitter_config.get("chunk_size", 100),
            chunk_overlap=splitter_config.get("chunk_overlap", 20),
        )
        
        chunks = text_splitter.split_text(text)
        logger.info(f"Text split into {len(chunks)} chunks")
        return chunks
    
    def store_vectors_pinecone(
        self,
        texts: List[str],
        index_name: str,
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> Any:
        """
        Store vectors in Pinecone
        
        Args:
            texts: List of texts to store
            index_name: Name of the index
            metadata: Optional metadata for each text
            
        Returns:
            Vectorstore instance
        """
        try:
            pc = self.setup_pinecone()
            
            # Get embeddings
            embeddings = self.embedding_service.get_embeddings(texts)
            
            # Get index
            index = pc.Index(index_name)
            
            # Prepare vectors for upsert
            vectors = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                vector_id = f"vec_{i}"
                meta = metadata[i] if metadata and i < len(metadata) else {"text": text}
                vectors.append((vector_id, embedding, meta))
            
            # Upsert vectors
            index.upsert(vectors=vectors)
            
            logger.info(f"Stored {len(vectors)} vectors in Pinecone index: {index_name}")
            return index
            
        except Exception as e:
            logger.error(f"Error storing vectors in Pinecone: {str(e)}")
            raise
    
    def query_pinecone(
        self,
        query_text: str,
        index_name: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Query Pinecone index
        
        Args:
            query_text: Query text
            index_name: Name of the index
            top_k: Number of results to return
            
        Returns:
            List of query results
        """
        try:
            pc = self.setup_pinecone()
            index = pc.Index(index_name)
            
            # Get query embedding
            query_embedding = self.embedding_service.get_embeddings(query_text)
            
            # Query index
            results = index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            logger.info(f"Queried Pinecone index: {index_name}")
            return results.matches
            
        except Exception as e:
            logger.error(f"Error querying Pinecone: {str(e)}")
            raise

    # ==================== Milvus Operations ====================

    def connect_milvus(self):
        """Connect to Milvus database"""
        if not self.milvus_connected:
            milvus_config = self.vector_config.get("milvus", {})

            connections.connect(
                alias=milvus_config.get("connection", {}).get("alias", "default"),
                host=milvus_config.get("host", "localhost"),
                port=milvus_config.get("port", "19530")
            )

            self.milvus_connected = True
            logger.info("Connected to Milvus")

    def create_milvus_collection(self, collection_name: Optional[str] = None) -> Collection:
        """
        Create a Milvus collection

        Args:
            collection_name: Name of the collection

        Returns:
            Collection instance
        """
        try:
            self.connect_milvus()

            milvus_config = self.vector_config.get("milvus", {})

            if collection_name is None:
                collection_name = milvus_config.get("collection", {}).get("name", "email_collection")

            # Check if collection exists
            if utility.has_collection(collection_name):
                logger.info(f"Milvus collection already exists: {collection_name}")
                return Collection(collection_name)

            # Get schema configuration
            schema_config = milvus_config.get("schema", {}).get("fields", [])

            # Create fields
            fields = []
            for field_config in schema_config:
                field_name = field_config.get("name")
                field_type = field_config.get("type")

                # Map string type to DataType
                dtype_map = {
                    "INT64": DataType.INT64,
                    "VARCHAR": DataType.VARCHAR,
                    "FLOAT_VECTOR": DataType.FLOAT_VECTOR
                }

                dtype = dtype_map.get(field_type, DataType.VARCHAR)

                field_params = {
                    "name": field_name,
                    "dtype": dtype,
                }

                if field_config.get("is_primary"):
                    field_params["is_primary"] = True
                    field_params["auto_id"] = field_config.get("auto_id", False)

                if field_config.get("max_length"):
                    field_params["max_length"] = field_config["max_length"]

                if field_config.get("dim"):
                    field_params["dim"] = field_config["dim"]

                fields.append(FieldSchema(**field_params))

            # Create schema
            schema = CollectionSchema(fields)

            # Create collection
            collection = Collection(name=collection_name, schema=schema)

            logger.info(f"Created Milvus collection: {collection_name}")
            return collection

        except Exception as e:
            logger.error(f"Error creating Milvus collection: {str(e)}")
            raise

    def create_milvus_index(self, collection_name: Optional[str] = None):
        """
        Create index on Milvus collection

        Args:
            collection_name: Name of the collection
        """
        try:
            self.connect_milvus()

            milvus_config = self.vector_config.get("milvus", {})

            if collection_name is None:
                collection_name = milvus_config.get("collection", {}).get("name", "email_collection")

            collection = Collection(collection_name)

            # Get index configuration
            index_config = milvus_config.get("index", {})

            # Create index
            collection.create_index(
                field_name=index_config.get("field_name", "embedding"),
                index_params={
                    "index_type": index_config.get("index_type", "IVF_FLAT"),
                    "metric_type": index_config.get("metric_type", "COSINE"),
                    "params": index_config.get("params", {"nlist": 128})
                }
            )

            logger.info(f"Created index on Milvus collection: {collection_name}")

        except Exception as e:
            logger.error(f"Error creating Milvus index: {str(e)}")
            raise

    def insert_milvus_vectors(
        self,
        collection_name: str,
        data: List[List[Any]]
    ):
        """
        Insert vectors into Milvus collection

        Args:
            collection_name: Name of the collection
            data: Data to insert (list of field values)
        """
        try:
            self.connect_milvus()
            collection = Collection(collection_name)

            collection.insert(data)
            collection.flush()

            logger.info(f"Inserted data into Milvus collection: {collection_name}")

        except Exception as e:
            logger.error(f"Error inserting into Milvus: {str(e)}")
            raise

    def search_milvus(
        self,
        collection_name: str,
        query_vectors: List[List[float]],
        top_k: int = 10
    ) -> List[Any]:
        """
        Search Milvus collection

        Args:
            collection_name: Name of the collection
            query_vectors: Query vectors
            top_k: Number of results to return

        Returns:
            Search results
        """
        try:
            self.connect_milvus()
            collection = Collection(collection_name)
            collection.load()

            # Search
            results = collection.search(
                data=query_vectors,
                anns_field="embedding",
                param={"metric_type": "COSINE", "params": {"nprobe": 10}},
                limit=top_k
            )

            logger.info(f"Searched Milvus collection: {collection_name}")
            return results

        except Exception as e:
            logger.error(f"Error searching Milvus: {str(e)}")
            raise

    def delete_milvus_collection(self, collection_name: str):
        """
        Delete a Milvus collection

        Args:
            collection_name: Name of the collection to delete
        """
        try:
            self.connect_milvus()

            if utility.has_collection(collection_name):
                utility.drop_collection(collection_name)
                logger.info(f"Deleted Milvus collection: {collection_name}")
            else:
                logger.warning(f"Collection does not exist: {collection_name}")

        except Exception as e:
            logger.error(f"Error deleting Milvus collection: {str(e)}")
            raise


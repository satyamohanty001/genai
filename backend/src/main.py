from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from llama_parse import LlamaParse
from langchain_ollama.llms import OllamaLLM
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from llama_index.core import SimpleDirectoryReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.schema import Document as LangChainDocument

# Initialize Flask application
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing to allow requests from frontend
CORS(app)

class RAGPipeline:
    """
    Retrieval-Augmented Generation (RAG) Pipeline class that handles document loading,
    parsing, embedding, vectorstore management, and query processing.
    """
    def __init__(self, model_name="llama3.1:8b", temperature=0):
        """
        Initialize the RAG pipeline with model and configuration parameters.
        
        Args:
            model_name (str): The name of the Ollama model to use (default: "llama3.1:8b")
            temperature (float): The temperature for model generation (default: 0, more deterministic)
        """
        # Initialize the language model for response generation
        self.llm = OllamaLLM(model=model_name, temperature=temperature)
        # Initialize embeddings model for vector representations
        self.embeddings = OllamaEmbeddings(model=model_name)
        # Initialize parser for document processing
        self.parser = LlamaParse(result_type="text")
        # Configure text splitter to chunk documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,  # Maximum size of text chunks
            chunk_overlap=200,  # Overlap between chunks for context preservation
            length_function=len
        )
        # Path to the data directory containing documents
        self.file_path = "..\data"
        # Placeholders for vectorstore and retrieval chain
        self.vectorstore = None
        self.retrieval_chain = None
        # Initialize the pipeline components
        self.initialize_pipeline()

    def load_and_parse_documents(self):
        """
        Load and parse documents from the file path.
        Handles multiple file formats including Excel, PDF, and Word.
        
        Returns:
            list: List of processed LangChain Document objects
        """
        # Configure file extractors for different document types
        file_extractor = {
            ".xlsx": self.parser,  # Excel files
            ".pdf": self.parser,   # PDF files
            ".doc": self.parser    # Word files
        }
        
        # Load documents using llama_index SimpleDirectoryReader
        llama_documents = SimpleDirectoryReader(
            input_dir=self.file_path,
            file_extractor=file_extractor
        ).load_data()
        
        # Convert llama_index documents to LangChain documents
        langchain_documents = []
        for doc in llama_documents:
            langchain_doc = LangChainDocument(
                page_content=doc.get_content(),
                metadata={
                    "source": doc.metadata.get("file_path", ""),
                    "file_name": os.path.basename(doc.metadata.get("file_path", "")),
                }
            )
            langchain_documents.append(langchain_doc)
        
        return langchain_documents

    def setup_retrieval_chain(self):
        """
        Set up the retrieval chain for processing queries using the vectorstore.
        Configures the prompt template and processing pipeline.
        """
        # Define the prompt template for context-based question answering
        template = """
        Use the following pieces of context to answer the question at the end.
        Keep the answer short and precise.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context: {context}
        
        Question: {question}
        
        Answer:"""
        
        # Create prompt template from the template string
        prompt = PromptTemplate.from_template(template)
        # Configure retriever to fetch relevant documents from vectorstore
        retriever = self.vectorstore.as_retriever()
        
        # Setup the processing chain:
        # 1. Retrieve context and pass question
        # 2. Format with prompt template
        # 3. Send to language model
        # 4. Parse output as string
        self.retrieval_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def initialize_pipeline(self):
        """
        Initialize the pipeline by either loading an existing vectorstore
        or creating a new one from documents.
        """
        if os.path.exists("../chroma_db"):
            print("Loading existing vectorstore...")
            # Load existing vectorstore if it exists
            self.vectorstore = Chroma(
                embedding_function=self.embeddings,
                collection_name="collection1",
                persist_directory="../chroma_db"
            )
        else:
            print("Creating new vectorstore...")
            # Load and process documents
            documents = self.load_and_parse_documents()
            # Split documents into chunks
            texts = self.text_splitter.split_documents(documents)
            
            # Create and persist a new vectorstore
            self.vectorstore = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,
                collection_name="collection1",
                persist_directory="../chroma_db"
            )
        
        # Set up the retrieval chain
        self.setup_retrieval_chain()

    def query(self, question: str) -> str:
        """
        Process a query through the retrieval chain.
        
        Args:
            question (str): The question to answer
            
        Returns:
            str: The generated answer based on document context
        """
        response = self.retrieval_chain.invoke(question)
        return response

# Initialize the RAG pipeline with default settings
pipeline = RAGPipeline()

@app.route('/chat', methods=['POST'])
def chat():
    """
    Flask endpoint for handling chat requests.
    Expects a JSON payload with a 'question' field.
    
    Returns:
        JSON: Contains the question and generated answer or error message
    """
    try:
        # Parse the JSON request data
        data = request.json
        if not data or 'question' not in data:
            # Return error if question is missing
            return jsonify({
                "status": "error",
                "message": "Question is required in the request body"
            }), 400
        
        # Process the question through the RAG pipeline
        response = pipeline.query(data['question'])
        # Return successful response with the answer
        return jsonify({
            "status": "success",
            "question": data['question'],
            "answer": response
        }), 200
    except Exception as e:
        # Handle any exceptions and return error response
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Run the Flask application when script is executed directly
    app.run(host='0.0.0.0', port=5000, debug=True)
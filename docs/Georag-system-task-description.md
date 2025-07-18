# Background
Retrieval Augmented Generation (RAG) is a technique that enhances Large Language Models (LLMs) by retrieving relevant information from external knowledge sources before generating responses.

Think of RAG as giving an AI the ability to "look things up" before answering questions. Here's a simple breakdown of how it works:

1. When a user asks a question, the system first searches through a database of documents to find relevant information
2. It then provides this information to the language model as extra context
3. The language model uses this context to generate a more accurate and informed response

This approach helps improve the accuracy, relevance, and factuality of LLM outputs by grounding responses in retrieved information. It's especially useful when dealing with specialized knowledge or information that might be outside the model's training data.

# Task Objective
Build a working RAG system that can:
1. Take the open street map source data of restaurants, cafe, attractions, and shopping centers in Karlsruhe, Germany (Focus of the task).
2. Store the description of the geo data in a searchable way in vector database.
3. Answer user questions by recommending the best route based on the user query and location and generating helpful responses.

# What You'll Learn
By completing this task, you'll learn about:
- Vector databases and semantic search
- Embedding models that convert text to numerical vectors
- Large Language Models (LLMs) and how to use them effectively
- How to combine retrieval and generation for better AI responses
- Practical Python implementation of an AI system

# Technology Components (Explained)

## Vector Database: Milvus
Milvus is a database specially designed to store and search through vectors (which are essentially lists of numbers). In our RAG system, we'll convert text into these vectors and use Milvus to quickly find similar vectors when we need to retrieve information.

## RAG Framework: LlamaIndex
LlamaIndex is a data framework that makes it easier to build RAG applications. It handles many of the complex tasks involved in document processing, indexing, and retrieval, so you don't have to build everything from scratch.

## Language Model: Mistral
Mistral is an open-source Large Language Model (LLM) that we'll use to generate responses based on retrieved information. The 7B parameter version is powerful enough for good results while being manageable on standard hardware.

## Embedding Model: Sentence Transformers
This is the model that converts text into numerical vectors (embeddings). We'll specifically use the `all-MiniLM-L6-v2` model, which is efficient and produces good quality embeddings for similarity search.

# Deliverables
1. A working RAG system with the following capabilities:
   - Document ingestion pipeline (ability to load and process documents)
   - Vector indexing using Milvus (storing document embeddings)
   - Query processing with context retrieval (finding relevant information)
   - Response generation using Mistral (creating answers based on retrieved context)

2. Code repository including:
   - Well-structured, documented code with comments explaining what each part does
   - Requirements file for easy installation
   - README with clear setup and usage instructions

3. Command-line interface (CLI) for interacting with the system

4. Example queries and their outputs showing the system in action
   - Include at least 5 example queries
   - Show both the retrieved contexts and the final generated answers
   - Include examples with different types of questions (see Evaluation)

# Implementation Steps (With Explanations)

## 1. Environment Setup
- Create a Python virtual environment (this keeps your project dependencies separate from other projects)
- Install required libraries:
  ```
  pip install llama-index pymilvus sentence-transformers transformers torch argparse
  ```
  - llama-index: The main RAG framework
  - pymilvus: Python client for Milvus vector database
  - sentence-transformers: For creating text embeddings
  - transformers: To work with the Mistral model
  - torch: Required for machine learning models
  - argparse: For building the command line interface

## 2. Document Ingestion (Getting Data In)
- Research on how to find descriptions of places from open street map database.
- Write code to create these descriptions as text with metadata (this is called document in LlamaIndex)
- Split documents into smaller chunks (this makes retrieval more precise)
  - Recommended: Split into 512 token chunks with 50 token overlap
  - A "token" is roughly equivalent to 3/4 of a word (there is online tools that visualize tokens in words)
- Generate embeddings (vector representations) for each chunk using Sentence Transformers

## 3. Milvus Setup (Vector Storage)
- Install Milvus (https://milvus.io/docs/milvus_lite.md)
- Create a collection in Milvus to store your document embeddings
- Write functions to:
  - Store document chunks, their embeddings and their metadata in Milvus
  - Search for similar chunks based on a query
  - Keep track of which document and position each chunk came from

## 4. RAG Pipeline (Putting It All Together)
- Use LlamaIndex to connect all the components:
  - Document loading
  - Text chunking
  - Embedding generation
  - Vector storage in Milvus
  - Query processing
  - Response generation

## 5. LLM Integration (Making It Smart)
- Set up the Mistral model for generating responses
- Create good prompts that tell Mistral:
  - What the user's question is
  - What context information was retrieved
  - How to format a helpful response

## 6. Command-Line Interface (Making It Usable)
- Create a simple command-line program that lets users:
  - Add documents to the system
  - Ask questions and get answers
  - See which sources were used to generate the answer

# Evaluation

1. Try the example queries and see if they give reasonable answers
2. Document what works well and what could be improved
3. Include screenshots or text outputs of your example queries and responses
4. For testing you can use any point in Karlsruhe as the user location

# Example Queries to Test With

1. Restaurant type Queries
Example Query: I am looking for the best sushi restaurant in Europaplatz.

2. Situation type Queries
Example Query: Where can I bring my 2 kids to visit in Karlsruhe?

3. Shopping type Queries
Example Query: I want to buy a new washing machine and where can I go to check in the city?

For each tested query, save:
- The original query
- What context was retrieved from the documents
- The final response generated
- Visualization of the best routes
- How well the response answered the query

# Documentation Links
- [LlamaIndex Beginner's Guide](https://docs.llamaindex.ai/en/stable/getting_started/starter_example.html)
- [Milvus Quick Start](https://milvus.io/docs/install-python.md)
- [Sentence Transformers Examples](https://www.sbert.net/examples/applications/computing-embeddings/README.html)
- [Hugging Face Transformers Quick Tour](https://huggingface.co/docs/transformers/quicktour)


# Project Documentation

## Overview

This project implements a Retrieval-Augmented Generation (RAG) system for educational content. It consists of several Python scripts that work together to generate, process, retrieve, and serve educational content for children of different age groups.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/qa_chatbot.git
   cd qa_chatbot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Files Description

### 1. `generate_data.py`

This script is responsible for generating educational content using the GPT-4o-mini model.

**Key Features:**
- Generates educational questions across various topics (Science, Technology, History, Life Skills, Health)
- Creates age-appropriate answers for different age groups (Kindergarten, P1-P3, P4-P6)
- Formats and saves the generated content as JSON files
- Implements error handling and rate limiting for API requests

**Main Functions:**
- `get_answers_gpt()`: Sends requests to the OpenAI API to generate content
- `clean_json_response()`: Cleans JSON responses from the API
- `generate_educational_content()`: Orchestrates the content generation process

### 2. `preprocess_data.py`

This script preprocesses the generated educational content to prepare it for the vector database.

**Key Features:**
- Transforms the raw JSON data into a format suitable for RAG systems
- Creates individual documents for each question-answer pair
- Adds metadata (topic, question, age group) to each document
- Saves the processed data for later use

**Main Functions:**
- `preprocess_educational_content()`: Converts the educational content into a format suitable for vector embedding

### 3. `create_vectordb.py`

This script creates a vector database from the preprocessed documents using Chroma and OpenAI embeddings.

**Key Features:**
- Loads preprocessed documents from JSON files
- Converts data into LangChain Document objects
- Creates vector embeddings using OpenAI's text-embedding-3 model
- Stores the vector database locally for efficient retrieval

**Main Functions:**
- `create_vector_database()`: Creates and persists a vector database from preprocessed documents

### 4. `intention_classifier.py`

This script classifies user queries into one of five educational categories using a prompt-based approach.

**Key Features:**
- Classifies queries into health, history, life_skills, science, or technology categories
- Uses a language model to perform the classification
- Handles edge cases and provides fallback classifications
- Offers reliable categorization for the retrieval system

**Main Functions:**
- `classify_query()`: Takes a user query and returns its classified category

### 5. `app.py`

This script serves as the main application, providing a user interface and handling the RAG pipeline.

**Key Features:**
- Provides a web interface for users to interact with the educational content
- Handles query processing and response generation
- Integrates classification, retrieval, and generation components
- Supports age-appropriate responses based on user selection

**Main Functions:**
- UI components for user interaction
- Query processing pipeline
- RAG system integration with streaming responses

## Retrieval Process

The retrieval process follows these steps:

1. **Query Classification**: When a user submits a question, `intention_classifier.py` analyzes it and assigns one of the five educational categories.

2. **Contextual Retrieval**: Based on the classified category and the exact query, the system searches the vector database for the most relevant documents.
   - The query is converted to an embedding using the same model used to create the database
   - Semantic similarity search finds the most relevant documents
   - Metadata filtering can be applied based on the classified category and selected age group

3. **Context Augmentation**: The retrieved documents are combined to form a comprehensive context.

4. **Response Generation**: The context and original query are sent to the language model, which generates an age-appropriate response.

5. **Streaming**: The response is streamed back to the user for a better user experience.

## Workflow

1. **Content Generation**: `generate_data.py` creates educational content using GPT-4o-mini
2. **Data Preprocessing**: `preprocess_data.py` transforms the content into a format suitable for vector embedding
3. **Vector Database Creation**: `create_vectordb.py` creates embeddings and stores them in a Chroma database
4. **Query Classification**: `intention_classifier.py` categorizes user queries
5. **Response Generation**: `app.py` handles the end-to-end RAG pipeline and user interface

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Generate educational content:
   ```bash
   python generate_data.py
   ```

3. Preprocess the generated data:
   ```bash
   python preprocess_data.py
   ```

4. Create the vector database:
   ```bash
   python create_vectordb.py
   ```

5. Run RAG UI and service:
   ```bash
   python app.py
   ```

The resulting system provides an interactive interface where users can ask educational questions and receive age-appropriate answers retrieved from the knowledge base.



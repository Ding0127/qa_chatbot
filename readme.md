# Project Documentation

## Overview

This project implements a Retrieval-Augmented Generation (RAG) system for educational content. It consists of three main Python scripts that work together to generate, process, and retrieve educational content for children of different age groups.

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

## Workflow

1. **Content Generation**: `generate_data.py` creates educational content using GPT-4o-mini
2. **Data Preprocessing**: `preprocess_data.py` transforms the content into a format suitable for vector embedding
3. **Vector Database Creation**: `create_vectordb.py` creates embeddings and stores them in a Chroma database

## Usage

1. Generate educational content:
   ```bash
   python generate_data.py
   ```

2. Preprocess the generated data:
   ```bash
   python preprocess_data.py
   ```

3. Create the vector database:
   ```bash
   python create_vectordb.py
   ```

4. Run RAG UI and service:
   ```bash
   python app.py
   ```

The resulting vector database can be used for semantic search and retrieval of educational content based on user queries, enabling a RAG system that provides age-appropriate educational answers.


# qa_chatbot

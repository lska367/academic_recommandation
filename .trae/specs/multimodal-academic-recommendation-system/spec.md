# Multimodal Academic Recommendation System Spec

## Why
Current academic recommendation systems are limited to text-based search and lack the ability to leverage multimodal content (figures, tables, equations) from papers. This system provides intelligent, conversational recommendations with comprehensive academic reports by combining multimodal understanding and LLM capabilities.

## What Changes
- Create Python backend with uv environment management
- Implement arXiv paper crawler
- Build PDF processing pipeline (reading, chunking)
- Implement multimodal embedding using doubao-embedding-vision-250615
- Add vector store with persistent storage
- Build multimodal reranking module using doubao-seed-2-0-lite-260215
- Create React frontend with conversational UI
- Implement automatic data check/fetch on startup
- Integrate OpenAI library for Volcengine ARK API

## Impact
- Affected specs: New system
- Affected code: All new files

## ADDED Requirements
### Requirement: Data Collection
The system SHALL automatically check for existing papers on startup and fetch new papers from arXiv if insufficient data exists.

#### Scenario: Startup data check
- **WHEN** system starts
- **THEN** check if at least 50 papers exist
- **THEN** if not, crawl arXiv for recent papers in CS.AI, CS.LG, CS.CL categories

### Requirement: PDF Processing
The system SHALL process PDF papers by reading content, extracting text and images, and chunking into manageable pieces.

#### Scenario: PDF processing success
- **WHEN** a PDF paper is added
- **THEN** extract text content, figures, and tables
- **THEN** create content chunks with context
- **THEN** store chunks for embedding

### Requirement: Multimodal Embedding
The system SHALL encode text and image chunks using doubao-embedding-vision-250615 model via Volcengine ARK API.

#### Scenario: Embedding generation
- **WHEN** content chunks are available
- **THEN** generate multimodal embeddings for each chunk
- **THEN** store embeddings in persistent vector database

### Requirement: Reranking
The system SHALL use doubao-seed-2-0-lite-260215 to rerank candidate papers based on user query and multimodal content.

#### Scenario: Reranking success
- **WHEN** user submits a query
- **THEN** retrieve initial candidate papers via vector search
- **THEN** rerank candidates using LLM with multimodal understanding
- **THEN** return top recommended papers

### Requirement: Academic Report Generation
The system SHALL generate a comprehensive academic report based on recommended papers.

#### Scenario: Report generation
- **WHEN** papers are recommended
- **THEN** synthesize content from papers
- **THEN** generate structured academic report with citations
- **THEN** display report in frontend

### Requirement: Frontend Interaction
The system SHALL provide a React-based conversational UI for users to interact with the recommendation system.

#### Scenario: User conversation
- **WHEN** user sends a message
- **THEN** display conversation history
- **THEN** show paper recommendations with metadata
- **THEN** display generated academic report

# RAG Retriever API for SQL Assistant

A FastAPI microservice that provides intelligent context retrieval for RAG-based SQL assistants. This service combines vector search with hybrid filtering to find relevant SQL logic examples and database schema information.

## 🚀 Features

- **Domain-Specific Italian Model**: Uses proven Italian BERT for consistent embeddings
- **Dual Strategy Retrieval**: Logic-driven retrieval with schema fallback
- **Hybrid Search**: Vector similarity + keyword boosting + metadata filtering  
- **Domain-Specific Configuration**: Customizable thresholds per business domain
- **Single Proven Model**: Italian BERT tested and optimized for SQL domain
- **Auto-Join Inclusion**: Automatically includes related tables based on foreign keys
- **Async Architecture**: Built on FastAPI with full async/await support

## 📋 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  RAG Retriever   │───▶│   LLM Context   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Hybrid Searcher    │
                    └─────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
            ┌──────────────┐    ┌──────────────┐
            │   ChromaDB   │    │   MongoDB    │
            │   (Vector)   │    │ (Metadata)   │
            └──────────────┘    └──────────────┘
```

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework
- **ChromaDB**: Vector database for embeddings
- **MongoDB**: Document store for metadata  
- **Italian BERT**: Proven embedding model for Italian SQL domain
- **Docker**: Containerization
- **Async I/O**: Full async stack

## 📁 Project Structure

```
rmanager-v1/
├── app/
│   ├── core/
│   │   ├── config.py           # Enhanced configuration
│   │   ├── errors.py           # Custom errors
│   │   └── meta.py             # Meta classes
│   ├── database/
│   │   ├── chroma.py           # ChromaDB client
│   │   └── mongo.py            # MongoDB client
│   ├── retriever/
│   │   ├── rag_retriever.py    # Main retriever logic
│   │   └── hybrid_searcher.py  # Hybrid search implementation
│   ├── models/
│   │   └── api_models.py       # Pydantic models
│   ├── services/
│   │   └── embedding_service.py # Embedding service
│   └── routers/
│       └── search.py           # API routes
├── main.py                     # FastAPI application
├── requirements.txt            # Dependencies
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Multi-service setup
├── local.env.example           # Environment template
└── README.md                   # This file
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

1. **Clone and setup**:
```bash
git clone <repository>
cd rmanager-v1
cp local.env.example local.env
# Edit local.env with your settings
```

2. **Start all services**:
```bash
docker-compose up -d
```

3. **Test the API**:
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "ordini per cliente", "domain": "ordini"}'
```

### Option 2: Local Development

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Start dependencies** (MongoDB + ChromaDB):
```bash
docker-compose up mongo chromadb -d
```

3. **Run the API**:
```bash
python main.py
```

## 📚 API Endpoints

### Core Endpoints

#### `POST /api/v1/search`
Main search endpoint for context retrieval.

**Request**:
```json
{
  "query": "trova tutti gli ordini per il cliente X",
  "domain": "ordini",
  "max_logics": 3,
  "max_schemas": 5,
  "logic_threshold": 0.4,
  "schema_threshold": 0.5
}
```

**Response**:
```json
{
  "retrieval_metadata": {
    "strategy": "logic_driven",
    "domain": "ordini",  // Auto-detected from metadata!
    "total_logics": 2,
    "total_schemas": 4,
    "processing_time_ms": 156.7,
    "referenced_tables": ["SORDER", "SORDERQ"]
  },
  "context": {
    "logics": [
      {
        "natural_query": "dammi il totale dell'ordinato per l'ordine ODV25IT00100001",
        "sql_query": "SELECT sp.NETPRINOT_0 * SQ.QTY_0...",
        "tables": ["SORDERP", "SORDERQ"],
        "x3_context": "ordini"
      }
    ],
    "schemas": [
      {
        "table_name": "SORDERQ",
        "description": "Tabella relativa i dati di riga...",
        "columns": [...],
        "table_joins_processed": "JOIN SORDER ON..."
      }
    ],
    "detected_domains": ["ordini"]  // Shows what domains were auto-detected
  }
}
```

#### `GET /api/v1/health`
Health check endpoint.

#### `GET /api/v1/domains`
Get available domains and their configurations.

#### `GET /api/v1/models/info`
Get information about loaded embedding models.

### Development Endpoints

#### `POST /api/v1/search/debug`
Debug version with detailed retrieval information (only in debug mode).

#### `GET /metrics`
Service metrics and statistics.

## ⚙️ Configuration

### Domain Configuration

Configure different domains in `config.py`:

```python
domain_configs: Dict[str, DomainConfig] = {
    "ordini": DomainConfig(
        logic_distance_threshold=0.35,
        schema_distance_threshold=0.45,
        max_schemas=7,
        max_logics=3
    ),
    "magazzino": DomainConfig(
        logic_distance_threshold=0.45,
        max_logics=2
    ),
    "default": DomainConfig()
}
```

### Environment Variables

Key environment variables in `local.env`:

```bash
# Core settings
DEBUG=true
APP_NAME=RAG-Retriever

# Databases
MONGO_URI=mongodb://localhost:27017
CHROMA_HOST=localhost
CHROMA_PORT=8080

# Models
LOGIC_EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
SCHEMA_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 🔍 Retrieval Strategy

### Two-Path Strategy

1. **Logic-Driven Path**: 
   - Search for similar SQL logic examples
   - Extract referenced table names
   - Include related schemas (with auto-joins)
   - Add additional schemas via vector search

2. **Schema-Only Path**:
   - Used when no relevant logic found
   - Direct vector search on schema collection
   - Includes related tables via joins

### Hybrid Search Features

- **Vector Similarity**: Core semantic matching
- **Keyword Boosting**: Boost based on exact keyword matches
- **Metadata Filtering**: Domain-specific filtering
- **Auto-Join Inclusion**: Automatically include related tables

## 🎯 Use Cases

### SQL Assistant Integration

```python
# Example integration with LLM
response = await search_context({
    "query": "How do I get total revenue by customer?",
    "domain": "ordini"
})

llm_prompt = f"""
You are an SQL expert. Use this context to help answer the user's question:

SIMILAR EXAMPLES:
{response.context.logics}

AVAILABLE TABLES:
{response.context.schemas}

User Question: {user_question}
"""
```

### Domain-Specific Queries

- **ordini**: Orders, customers, sales
- **magazzino**: Inventory, warehouse, stock
- **clienti**: Customer management, CRM
- **contabilita**: Accounting, financial data

## 🧪 Testing

### Manual Testing

```bash
# Test health
curl http://localhost:8000/api/v1/health

# Test search with auto-domain detection
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mostra ordini per articolo"
  }'

# Test search with explicit domain (optional)
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mostra ordini per articolo",
    "domain": "ordini", 
    "max_logics": 2
  }'

# Test domains
curl http://localhost:8000/api/v1/domains
```

### Unit Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=app tests/
```

## 📊 Monitoring

### Metrics

Access metrics at `/metrics`:
- Database statistics
- Model information
- Performance counters
- Collection sizes

### Logging

Structured logging with different levels:
- `INFO`: General operations
- `DEBUG`: Detailed search information  
- `ERROR`: Error conditions

### Health Checks

- Database connectivity
- Model loading status
- Service dependencies

## 🚀 Performance

### Optimization Tips

1. **Model Caching**: Models are cached locally
2. **Connection Pooling**: Async database connections
3. **Batch Processing**: Efficient embedding generation
4. **Threshold Tuning**: Adjust per domain for optimal results

### Scaling

- **Horizontal**: Multiple API instances
- **Vertical**: Increase model cache and memory
- **Database**: MongoDB sharding, ChromaDB clustering

## 🔧 Development

### Adding New Domains

1. Add domain config in `config.py`
2. Update test cases
3. Tune thresholds based on data

### Custom Embedding Models

1. Update model names in config
2. Ensure models are sentence-transformer compatible
3. Test with your domain data

### Extending Search Logic

1. Modify `HybridSearcher` for new features
2. Update boost calculation logic
3. Add new metadata filtering options

## 📝 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI**: http://localhost:8000/openapi.json

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

[Your License Here]

## 🆘 Support

For issues and questions:
- Create GitHub issues for bugs
- Check logs at `/metrics` endpoint
- Use debug mode for troubleshooting
- Monitor health at `/api/v1/health`
```
app/
├── agent/               # Agent
│   └── agent.py      
├── core/               # Core functionality
│   ├── config.py      # Application settings
│   ├── errors.py      # Custom exceptions
│   └── meta.py        # Metaclasses and logging
├── models/            # Pydantic schemas
│   ├── model.py      # LLM model schemas
│   └── prompt.py     # Prompt schemas
├── routers/           # API endpoints
│   ├── models.py     # Model CRUD endpoints
│   └── prompts.py    # Prompt CRUD endpoints
├── services/          # Business logic
│   ├── model_service.py
│   └── prompt_service.py
├── utils/             # Utilities
│   └── validators.py  # Business validation
└── main.py           # FastAPI application
```
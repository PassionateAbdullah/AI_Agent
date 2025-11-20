#Architecture Diagram for JD Generation Engine
#                   ┌──────────────────────────┐
#                   │ Knowledge Base (Optional) │
#                   │ - DEI policy              │
#                   │ - EVP                     │
#                   │ - Benefits list           │
#                   │ - Internal competencies   │
#                   └───────────┬──────────────┘
#                              │ (RAG Retrieval)
#                              ▼
#┌──────────────────────────────────────────────────────────────────┐
#│                    JD Generation Engine (Hybrid)                 │
#│  - Always prompt-driven                                          │
#│  - If KB exists, enrich the context                              │
#│  - If KB missing, fallback gracefully                            │
#└──────────────────────────────────────────────────────────────────┘ 

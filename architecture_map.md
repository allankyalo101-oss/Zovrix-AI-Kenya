# CloudStaff System Architecture Map

Generated: Sat Mar 14 11:37:30 EAT 2026

```mermaid
graph TD
User --> API[FastAPI Server]
API --> WhatsApp[Twilio WhatsApp Gateway]
API --> AI[AI Reasoning Engine]
AI --> GOV[Governance Layer]
GOV --> ORCH[Orchestrator]
GOV --> LEDGER[Decision Ledger]
AI --> PDF[Report Generator]
```

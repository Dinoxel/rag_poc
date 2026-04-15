## Agentic Task Execution System (POC)

This project demonstrates an agentic AI system that can:

* Handle Q&A via Retrieval-Augmented Generation (RAG)
* Execute task-oriented requests (invoices, quotes, payment checks)
* Use clarification and human-in-the-loop when information is missing
* Validate and normalize user inputs
* **Escalate to human support when needed** ⭐

---

## Architecture Overview

**Multi-agent, graph-based workflow** using LangGraph with specialized agents:

1. **Planner Agent** - Routes to Q&A, Task Execution, or Direct Escalation
2. **Q&A Path** - RAG-based retrieval and answer generation
3. **Task Execution Path** - Clarification → Validation → Scheduling → Confirmation
4. **Escalation Node** - Human support handoff with ticket generation

### Workflow

```
START → Planner
  ├→ Q&A: retrieval → answer → END
  ├→ Task: clarify (loop/escalate) → scheduler → confirm → answer → END
  └→ Escalate: escalation → END (direct)
```

![System Architecture](./graph_diagram.png)

---

## Escalation System ⭐

**Two escalation paths:**

### 1. Direct from Planner
Immediate escalation when user:
- Explicitly requests human support ("I want to talk to someone")
- Expresses frustration ("This is ridiculous")
- Requests sensitive operations (account deletion, refunds)

### 2. After Clarification
Automatic escalation when:
- Max clarification rounds reached (3)
- Confidence too low (< 0.3)
- Unsupported action type
- Persistent ambiguity (2+ rounds)

**Each escalation generates:**
- Unique ticket ID (e.g., TICKET-3C7D406B)
- Full context for support team
- User-friendly explanation

---

## Supported Actions

### 1. Create Invoice
**Required:** customer_name, amount, invoice_date, description  
**Optional:** customer_id, currency (EUR/USD/GBP), due_date, reference

### 2. Send Quote
**Required:** customer_name, customer_email, items  
**Optional:** customer_id, total_amount, valid_until, currency, notes

### 3. Check Payment Status
**Required (at least one):** payment_id, invoice_id, customer_name  
**Optional:** date_from, date_to

All fields are validated and normalized (dates → YYYY-MM-DD, emails → lowercase, amounts → decimal).

---

## Quick Start

### Setup
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # Add your API_KEY
```

### Run
```bash
python -m app.graph.graph_running
```

### Test
```bash
python test_clarification.py    # Clarification tests
python test_escalation.py        # Escalation tests
python test_direct_escalation.py # Direct escalation tests
```

---

## Example Usage

### Q&A
```
User: "How do I change the bank account for vendor payments?"
→ Retrieves documentation → Provides step-by-step answer
```

### Task Execution (Complete)
```
User: "Create an invoice for Acme Corp for €5000 dated 2024-03-15 for consulting"
→ Extracts all fields → Generates plan → Confirms with user
```

### Task Execution (Incomplete)
```
User: "Send a quote to john@example.com"
→ Clarifies: "What's the customer name and items?"
→ User provides info → Proceeds
```

### Direct Escalation
```
User: "I want to speak to a human"
→ Immediate escalation → Ticket generated → Support handoff
```

### Escalation After Clarification
```
User: "Create an invoice" 
→ 3 rounds of unclear responses
→ Escalates with full context
📋 Ticket: TICKET-3C7D406B
```

---

## Technical Notes

### Data Models
Task models (`app/data_models/task_models.py`) are defined locally for POC. In production, consider:
- Auto-generating from OpenAPI/Swagger
- Using shared schema repository
- Implementing CI/CD schema validation

### Type System
Centralized types in `app/types/types.py`:
- `StateModeType`: q&a | task_execution | escalate
- `EscalationReasonType`: 7 escalation triggers
- `SeverityType`: low | medium | high

---

## Project Structure

```
app/
├── agent_nodes/      # Planner, clarify, scheduler, escalation
├── data_models/      # Pydantic models (tasks, escalation)
├── graph/            # Graph design and routing
├── prompts/          # LLM prompts
├── state/            # Graph state management
├── tools/            # Field validators
└── types/            # Type definitions

docs/                 # Documentation
test_*.py            # Test suites
```

---

## Key Features

✅ **Smart Clarification** - Detects action type, extracts fields, asks structured questions  
✅ **Validation** - Email, date, amount, currency validators with normalization  
✅ **Two-level Escalation** - Direct from planner OR after failed clarification  
✅ **Context Preservation** - Full history provided to support on escalation  
✅ **Type Safety** - Pydantic models with strict validation  
✅ **Human-in-the-Loop** - Clarification and confirmation points  
✅ **Loop Protection** - Max 3 clarification rounds  

For detailed examples and architecture documentation, see `docs/` folder.

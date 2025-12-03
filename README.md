# SolRiver Project Finance Platform (MVP)
**Author:** Ryan Loveless  
**Role Targeted:** Clean Energy Financial Analyst – SolRiver Capital  

---

## 🌞 Overview
This repository contains a modular, scalable underwriting MVP designed to demonstrate how SolRiver can centralize project assumptions, standardize financial modeling, accelerate deal screening, and automate written investment summaries.  

The platform uses **Python + SQL + a command-line interface** to mirror how a lightweight internal underwriting system could be built from the ground up. It is intentionally small but architected with production scalability in mind.

The included **Analyst Technical Memo** provides a detailed written explanation of the project, its purpose, what has been completed, and a roadmap for future expansion.

---

## 🚀 Key Features

### **1. SQL Project Database**
Centralized storage for:
- Capacity, capex, opex  
- PPA pricing  
- Degradation  
- Debt structure  
- COD year & project metadata  

SQLite is used for the MVP, but the database layer is already configured to migrate to **Postgres (AWS RDS)** via a single configuration variable.

---

### **2. Modular Financial Model**
Computes all core underwriting metrics:
- Levered IRR  
- NPV at configurable discount rate  
- DSCR (annual minimum)  
- Simple payback  
- 25-year cash flow profile  

The entire financial logic is isolated in a dedicated module for clarity, auditability, and extension.

---

### **3. Automated Report Generator**
Outputs clean, memo-ready Markdown summaries containing:
- Project attributes  
- Assumptions  
- Financial metrics  
- Interpretable results  

This directly reduces analyst writing time and ensures consistent project summaries.

---

### **4. Sensitivity Analysis Engine**
Quick scenario evaluation for:
- PPA price changes  
- Capex variations  
- Leverage adjustments  

Ideal for early-stage deal screening and partner evaluation.

---

### **5. Command-Line Interface (CLI)**
User-friendly CLI commands allow analysts to run the entire model pipeline without touching code:

```

python -m src.cli run-model --project-id 1
python -m src.cli summarize --project-id 1
python -m src.cli sensitivity --project-id 1
python -m src.cli all --project-id 1

```

---

## 🧱 Architecture Overview

**Core modules:**
- `database.py` — Database engine & ORM models  
- `model.py` — Financial modeling logic  
- `report.py` — Summary & memo generator  
- `sensitivity.py` — Scenario engine  
- `cli.py` — Analyst-facing command interface  
- `config.yaml` — Environment configuration (SQLite ↔ Postgres-ready)  

The architecture follows clean separation of concerns and matches how internal investment tools are structured within project finance teams.

---

## 🔧 Installation & Usage

### **Install dependencies**
```

pip install -r requirements.txt

```

### **Run a complete underwriting workflow**
```

python -m src.cli all --project-id 1

```

### **Run only the financial model**
```

python -m src.cli run-model --project-id 1

```

### **Generate project memo**
```

python -m src.cli summarize --project-id 1

```

### **Run sensitivity analysis**
```

python -m src.cli sensitivity --project-id 1

```

---

## 📈 Future Enhancements (Roadmap)
This MVP is the foundation for a full underwriting system. Planned extensions include:

### **Financial Modeling**
- MACRS depreciation  
- ITC/PTC vs merchant curve modeling  
- Tax equity partnership structures  
- Storage adders / hybridization  
- Opex escalation curves  

### **Database Extensions**
- Interconnection data  
- Land lease terms  
- EPC contract metadata  
- PPA documents and contract flags  
- Multi-project batch underwriting  

### **Analytics & Output**
- Excel export for traditional workflows  
- PowerBI/Metabase dashboard  
- Portfolio-level analytics  
- Modeled vs actual performance tracking  

### **Automation & Cloud**
- Full Postgres migration (AWS RDS)  
- Nightly automated underwriting  
- S3 storage integration  
- Logging and monitoring  

---

## 📄 Included Documentation

### **1. Analyst Technical Memo**
This memo explains:
- What the MVP does  
- Solves which pain points  
- What remains to be built  
- How the architecture supports scalability  
- Why this design is appropriate for SolRiver  
- How this system fits into pipeline evaluation and deal screening  

The memo is located in the `/docs` folder and included with this repository as a core writing sample.

---

## 🧩 Purpose of This Project
This MVP was created to showcase:
- Technical engineering (SQL, Python, modeling)  
- Clean and persuasive writing  
- Financial analysis capabilities  
- Understanding of renewable project economics  
- Ability to design and build internal tools from scratch  
- Initiative, ownership, and problem-solving  

It reflects the exact competencies required for the **Clean Energy Financial Analyst role at SolRiver**.

---

## 📬 Contact
If you would like to discuss the project, walk through the architecture, or see future planned enhancements:

**Ryan Loveless**  
Email: LovelessRyanMitchell@gmail.com  
LinkedIn: https://linkedin.com/in/ryanmloveless  

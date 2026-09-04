# 📧 Gmail Spend Intelligence

An AI-powered personal finance application that securely analyzes Gmail transaction emails and converts them into structured spending insights.

The application connects to Gmail using OAuth, identifies financial emails, extracts transaction details using an LLM, and provides spending analytics and recurring-payment insights through an interactive Streamlit dashboard.

---

## 🚀 Features

* 🔐 **Secure Gmail OAuth Authentication**

  * Connects to Gmail using read-only access.
  * Uses Google OAuth 2.0 authentication.

* 📩 **Financial Email Detection**

  * Scans recent Gmail messages.
  * Identifies transaction-related emails using financial keywords and contextual filtering.
  * Excludes irrelevant emails such as newsletters, job alerts, and promotional messages.

* 🤖 **AI Transaction Extraction**

  * Uses Groq LLM to extract structured transaction information from email content.
  * Converts unstructured email text into structured financial records.
  * Uses Pydantic validation for reliable structured output.

* 📊 **Spending Analytics**

  * Total spending
  * Spending by category
  * Spending by merchant
  * Spending over time
  * Transaction-level details

* 🔄 **Recurring Payment Detection**

  * Identifies merchants with repeated transactions.
  * Estimates recurring monthly expenses.
  * Helps users identify subscriptions and regular payments.

* 💡 **Spending Insights**

  * Highlights total spending.
  * Identifies the highest spending category.
  * Identifies the highest spending merchant.
  * Highlights high-value transactions.
  * Provides recurring-payment observations and potential areas for savings.

* 🌐 **Streamlit Web Application**

  * Interactive dashboard
  * Simple user interface
  * Deployable on Streamlit Community Cloud

---

## 🏗️ System Architecture

```text
                    ┌──────────────────┐
                    │      Gmail       │
                    │ Transaction      │
                    │     Emails       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Google OAuth   │
                    │  Gmail Read Only │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Financial Email  │
                    │    Detection     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Groq LLM       │
                    │ Transaction      │
                    │   Extraction     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Pydantic         │
                    │ Validation       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Pandas           │
                    │ Data Processing   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐   ┌───────────┐   ┌──────────┐
        │Analytics │   │ Recurring │   │ Insights │
        │          │   │ Payments  │   │          │
        └────┬─────┘   └─────┬─────┘   └────┬─────┘
             │               │               │
             └───────────────┼───────────────┘
                             ▼
                    ┌──────────────────┐
                    │    Streamlit     │
                    │    Dashboard     │
                    └──────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend

* Streamlit

### Backend

* Python
* Pandas

### AI / LLM

* Groq
* `openai/gpt-oss-20b`

### Data Validation

* Pydantic

### Google Integration

* Gmail API
* Google OAuth 2.0

### Deployment

* GitHub
* Streamlit Community Cloud

---

## 📁 Project Structure

```text
gmail-spend-intelligence/
│
├── app.py
├── gmail_service.py
├── extractor.py
├── analytics.py
├── insights.py
├── requirements.txt
├── .gitignore
└── README.md
```

### File Responsibilities

**`app.py`**

Main Streamlit application. Handles the user interface, Gmail connection flow, email processing, transaction display, analytics, recurring payments, and spending insights.

**`gmail_service.py`**

Handles Gmail OAuth authentication, Gmail API communication, email retrieval, email-body extraction, and financial-email detection.

**`extractor.py`**

Uses the Groq LLM to extract structured transaction information from financial emails and validates the result using Pydantic.

**`analytics.py`**

Processes extracted transactions using Pandas and generates spending statistics, merchant/category analysis, spending trends, and recurring-payment information.

**`insights.py`**

Generates meaningful spending observations from transaction and recurring-payment data.

---

The application requests only:

```text
https://www.googleapis.com/auth/gmail.readonly
```

so it does not request permission to modify or delete Gmail messages.

---

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/gmail-spend-intelligence.git

cd gmail-spend-intelligence
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment/secrets

For local development, configure the required Groq and Google OAuth credentials securely.

For deployment, use Streamlit Secrets.

### 5. Run the application

```bash
streamlit run app.py
```

---

## 🔄 Application Workflow

### Step 1 — Connect Gmail

The user authenticates through Google OAuth.

### Step 2 — Fetch Emails

The application retrieves recent Gmail messages using the Gmail API.

### Step 3 — Detect Financial Emails

The system filters emails using financial keywords and contextual checks.

### Step 4 — Extract Transactions

Financial email content is sent to the Groq LLM.

The model extracts structured fields such as:

```text
Date
Merchant
Amount
Category
Transaction Type
```

### Step 5 — Validate Data

Pydantic validates the extracted transaction structure.

### Step 6 — Analyze Spending

Pandas is used to calculate:

* Total spending
* Category spending
* Merchant spending
* Spending trends

### Step 7 — Detect Recurring Payments

Repeated transactions from the same merchant are analyzed to identify potential recurring expenses.

### Step 8 — Generate Insights

The application presents concise observations about the user's spending behavior.

---

## 🎯 Problem Statement

Transaction information is often scattered across emails from banks, e-commerce platforms, payment providers, and subscription services.

Manually reviewing these emails to understand spending patterns is time-consuming.

Gmail Spend Intelligence automates this process by converting unstructured transaction emails into structured financial data and meaningful spending insights.

---

## 💡 Key Learning Outcomes

This project demonstrates practical experience with:

* Gmail API integration
* OAuth 2.0 authentication
* LLM-based information extraction
* Structured output generation
* Pydantic data validation
* Pandas data processing
* Financial email classification
* Recurring transaction analysis
* Streamlit application development
* Secure secret management
* Cloud deployment

---

## 🚀 Future Improvements

Possible future improvements include:

* More sophisticated transaction classification
* Multi-account support
* Persistent transaction storage
* Automated monthly reports

---

## 👨‍💻 Author

**Harshith Kumar**

AI/ML & Generative AI Enthusiast

Skills: Python | GenAI | LLMs | RAG | LangChain | FastAPI | Streamlit | Pandas

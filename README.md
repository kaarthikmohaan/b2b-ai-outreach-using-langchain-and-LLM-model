# B2B AI Outreach Using Langchain and LLM Model

## 📋 Overview

AI-powered B2B outreach tool that automates job opportunity identification and generates personalized cold emails. Uses LLMs, vector search, and web scraping to analyze job postings, match role requirements against company portfolios, and create tailored outreach highlighting service alignment.

---

## ✨ Features

### 1. End-to-End Job Opportunity Analyzer
- Accepts a URL to a public job posting (including JS-heavy websites)
- Uses Playwright to asynchronously fetch and render dynamic job descriptions
- Extracts clean readable text via BeautifulSoup
- Highlights job role, expected skills, and years of experience required using LLM parsing

### 2. Role and Skill Extraction with LLM
- Uses a robust prompt-based Groq LLaMA 3.1 model to extract key job fields: role, skills, experience, and responsibilities
- Ensures reliable parsing even when the job post structure varies
- Always outputs valid JSON with predefined keys, enabling consistent downstream processing

### 3. Portfolio Relevance Matching
- Loads a structured CSV portfolio of services/technologies (tech stack and reference link)
- Normalizes both job-required skills and portfolio keywords using a synonyms dictionary
- Performs skill-based filtering and returns matching portfolio links if at least one skill overlaps
- Links are passed to the email generator to support content relevance

### 4. Cold Email Generator with Dynamic Tone
- Generates personalized cold emails using Groq's LLM
- Email content reflects the extracted job details and matched services
- Integrates up to 4 most relevant portfolio links into the email text
- Offers tone customization (e.g., Formal, Friendly, Technical, Concise) using a select box
- Supports regeneration of emails if tone changes or if a new draft is desired

### 5. Email Preview and Utilities
- Displays email subject and content using Markdown rendering
- Provides one-click buttons for:
  - Copy to clipboard
  - Open in Gmail
  - Open in Outlook
- Embeds email body inside mailto-compatible deep links

### 6. Job Summary Generation
- Uses summarization prompts to display a 60-word preview of the job description
- Ideal for quick understanding without reading the entire post

### 7. Vector Database Integration (ChromaDB)
- Stores the internal company tech portfolio in a persistent vector store
- Indexes tech stacks as documents with metadata (URL links)
- Can be expanded to support semantic search in future versions

### 8. Experience Inference Engine
- Uses multiple regex patterns to extract years of experience mentioned in text
- Handles variants like "5+ years of experience in backend engineering" or "Minimum of 3 years required"
- Displays inferred experience level alongside role and skills

### 9. Skill Normalization Engine
- Uses a pre-defined synonyms dictionary to standardize skill names (e.g., "js" → "JavaScript")
- Applied both during job extraction and portfolio querying
- Ensures robust skill matching even when different terminologies are used

### 10. Streamlit Web App Frontend
- Responsive layout with wide screen format
- All outputs and interactions are reactive (Streamlit reruns statefully)
- Uses HTML injection for icon-styled buttons (Gmail, Outlook, Copy)

---

## 🗂️ Code Modules

| Module | Description |
|--------|-------------|
| **main.py** | Entry point of the Streamlit app. Handles user input, HTML parsing, state management, and rendering. |
| **chains.py** | Defines prompt templates and LLM call logic. Separates out three chains: `extract_jobs()`, `summarize()`, `write_mail()` |
| **portfolio.py** | Loads the internal service portfolio from CSV. Uses ChromaDB to store and retrieve vector-matched examples. Supports fuzzy skill matching using normalization. |
| **utils.py** | Provides functions to normalize skills. Cleans and sanitizes raw HTML text. |

---

## 🛠️ Tech Stack

### 🧠 AI & LLM Integration
| Technology | Purpose |
|------------|---------|
| **LangChain** | Framework for orchestrating LLM prompts, chaining inputs/outputs |
| **ChatGroq** | Access to Groq's LLaMA 3.1 LLM, optimized for speed + cost |
| **LLM Models** | Model: llama-3.1-8b-instant for job extraction, summarization, emails |

### 💻 Frontend & UI
| Technology | Purpose |
|------------|---------|
| **Streamlit** | Main web framework to build the interactive UI (forms, toggles, output) |
| **Streamlit HTML** | Custom rendering of buttons, email previews, Gmail/Outlook links |
| **JavaScript** | Used inside embedded HTML for clipboard copying functionality |

### 🌐 Web Scraping & Content Extraction
| Technology | Purpose |
|------------|---------|
| **Playwright (async)** | Headless browser automation to load and scrape JavaScript-heavy sites |
| **BeautifulSoup** | HTML parsing and job description extraction |
| **Asyncio** | Handles async Playwright scraping operations |

### 📊 Portfolio Matching & Vector Search
| Technology | Purpose |
|------------|---------|
| **Pandas** | Reads and processes the company_portfolio.csv |
| **ChromaDB** | Lightweight vector DB for fuzzy matching of job skills vs portfolio |
| **uuid** | Unique ID generation for vector documents |

### 🔎 Text Processing & NLP Utilities
| Technology | Purpose |
|------------|---------|
| **Regex (re)** | Custom experience/years extraction, section parsing |
| **Skill Normalization** | Synonym mapping (e.g., "py" → "Python") for consistent matching |

---

## 📁 Project Structure

```
.
├── .env                        # Stores API keys securely (e.g., GROQ_API_KEY)
├── main.py                     # Entry-point for Streamlit app with UI logic
├── chains.py                   # Contains logic for LLM prompting
├── portfolio.py                # Portfolio vector matching engine
├── utils.py                    # Text cleaning and skill synonym normalization
└── company_portfolio.csv       # Tech stack → portfolio link mappings
```

---

## 🧪 Test Cases

### ✅ Test Case 1: Job Description Extraction
**Purpose:** Verify if the application can extract job title, description, skills, and experience from a live job posting URL.

| Test Step | Description |
|-----------|-------------|
| **Input** | Paste a live job URL with structured job description (e.g., Microsoft Careers, Google Jobs) |
| **Expected Output** | Extracted JSON with fields: role, skills[], description, experience. Role and experience should be inferred even if not explicitly labeled |
| **Validation** | Check Streamlit output for Job Title, Expected Skills, Experience, and Job Summary |
| **Notes** | Use roles like "Data Scientist", "DevOps Engineer", "Embedded Developer" for variety |

### ✅ Test Case 2: Skill Matching with Portfolio
**Purpose:** Validate that relevant portfolio links are matched based on skills extracted from job posts.

| Test Step | Description |
|-----------|-------------|
| **Input** | A job post that includes skills like Python, AWS, Docker, Terraform |
| **Expected Output** | Matching links from company_portfolio.csv that include these keywords in Techstack |
| **Validation** | Ensure portfolio.query_links() returns list with at least 1 relevant link |
| **Notes** | Test edge cases like skills written in lowercase, hyphenated, or abbreviated (e.g., "py", "terraform") |

### ✅ Test Case 3: Email Generation (Cold Outreach)
**Purpose:** Ensure that the LLM generates a coherent, personalized outreach email aligned with job context and matched portfolio.

| Test Step | Description |
|-----------|-------------|
| **Input** | Extracted job + 3–4 matching portfolio links. Tone = "Formal" |
| **Expected Output** | Subject line inferred. Email body explains how your company's capabilities map to job requirements. Embedded job link + portfolio links. Ends with 3-line signature |
| **Validation** | Check if tone is formal and paragraphs include at least 2–3 matched services naturally |
| **Notes** | Repeat for tone = "Friendly", "Technical", "Concise" to validate tone switching |

### ✅ Test Case 4: Regenerate Logic
**Purpose:** Validate that clicking "Regenerate" always fetches a different version of the email with same tone.

| Test Step | Description |
|-----------|-------------|
| **Input** | Click "Regenerate" multiple times |
| **Expected Output** | New variations of email are produced with different wording. Tone remains consistent unless changed |
| **Validation** | Confirm no reuse of previous phrasing or same sentence structure |
| **Notes** | Enable temp=0.8+ to enforce creative variation in LLM output |

### ✅ Test Case 5: No Skill Match Warning
**Purpose:** Confirm the app warns when portfolio doesn't match job skills.

| Test Step | Description |
|-----------|-------------|
| **Input** | Job with rare stack (e.g., COBOL, Perl, Mainframes) not present in portfolio |
| **Expected Output** | Streamlit shows: "⚠️ No strong match, but including job 'X' due to partial skill overlap" |
| **Validation** | Email is still generated, but without portfolio links |

### ✅ Test Case 6: Clipboard Copy + Gmail/Outlook Buttons
**Purpose:** Validate export of email content to third-party email clients.

| Test Step | Description |
|-----------|-------------|
| **Input** | After email is generated, click "Copy Email", "Open in Gmail", or "Open in Outlook" |
| **Expected Output** | Email body copied to clipboard. Gmail/Outlook pre-fill the body and subject in compose window |
| **Validation** | Manual test by pasting in Gmail/Outlook and checking structure |
| **Notes** | Ensure mailto: encoding works as expected (special characters, newlines, quotes, etc.) |

### ✅ Test Case 7: Multi-Tone Switching
**Purpose:** Test if changing tone triggers correct re-generation.

| Test Step | Description |
|-----------|-------------|
| **Input** | Switch from "Formal" → "Technical" → "Friendly" |
| **Expected Output** | New email reflects tone (technical keywords, casual tone, etc.). No reuse of prior output |
| **Validation** | Observe tone style in email (greeting, wording, paragraph structure) |

### ✅ Test Case 8: Scraper Timeout or Empty Page
**Purpose:** Handle slow or broken pages gracefully.

| Test Step | Description |
|-----------|-------------|
| **Input** | A very slow-loading or minimal HTML job posting page |
| **Expected Output** | If fetch fails: "An error occurred: …". If no job text: warning about missing job info |
| **Validation** | No crash. App remains usable |

---

## 🚀 Getting Started

### Prerequisites
```bash
pip install streamlit langchain langchain-groq playwright beautifulsoup4 chromadb pandas python-dotenv
playwright install
```

### Setup
1. Clone the repository
2. Create a `.env` file with your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```
3. Prepare your `company_portfolio.csv` with columns: `Techstack`, `Links`

### Run the Application
```bash
streamlit run main.py
```

---

## 📝 Conclusion

This application successfully transforms manual outreach into an intelligent, scalable, and user-friendly workflow for business development teams. With further enhancements like user authentication, usage tracking, multi-user dashboards, and CRM integration, this tool can evolve into a powerful platform for enterprise-grade outreach automation.

---

# AI-Powered Data Analytics Assistant

## Overview

AI-Powered Data Analytics Assistant is an intelligent Streamlit application designed to simplify data exploration, business analytics, customer feedback analysis, and executive reporting.

The platform automatically adapts to different dataset types and combines traditional analytics with Large Language Models (LLMs) to generate insights, answer business questions, classify sentiment, and produce executive-ready reports.

---

## Key Features

### 📊 Data Analytics

* Upload CSV and Excel datasets
* Automated Exploratory Data Analysis (EDA)
* Missing value detection
* Duplicate record identification
* Data cleaning and transformation
* Dataset quality assessment
* Download cleaned datasets

### 📈 Interactive Visualizations

* Distribution analysis
* Correlation analysis
* Category-wise insights
* Trend analysis
* Business performance visualization

### 🤖 AI Analytics Assistant

* Natural language querying of datasets
* Dataset-aware responses
* Contextual business insights
* Automated trend interpretation
* Large dataset optimization for faster responses

### 💬 Customer Feedback Analytics

* Sentiment classification

  * Positive
  * Neutral
  * Negative
* Topic extraction
* Customer opinion analysis
* Review trend identification
* Feedback summarization

### 📄 Executive Report Generation

* Automated executive summaries
* Key findings extraction
* Actionable recommendations
* Business-focused reporting
* Downloadable reports

---

## Supported Dataset Types

The application automatically adapts its analytics workflow based on the uploaded dataset.

### Customer Feedback Datasets

Examples:

* Product reviews
* Service reviews
* Survey responses
* Customer comments

### Sales & Business Datasets

Examples:

* Retail sales
* Revenue reports
* Transaction data
* Business performance records

### Operational Datasets

Examples:

* Inventory management
* Logistics operations
* Process monitoring
* Organizational metrics

### Generic Tabular Datasets

Any structured CSV or Excel dataset.

---

## Technology Stack

### Frontend

* Streamlit

### Data Processing

* Pandas
* NumPy

### Visualization

* Plotly
* Matplotlib

### Artificial Intelligence

* Groq API
* Mistral API

### Analytics

* Automated EDA
* Sentiment Analysis
* Topic Extraction
* Business Insight Generation

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd <repository-name>
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment:

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key
MISTRAL_API_KEY=your_api_key
```

Run the application:

```bash
streamlit run app.py
```

---

## Project Workflow

1. Upload a dataset
2. Perform automated data analysis
3. Clean and transform data
4. Generate visual insights
5. Ask questions through the AI Assistant
6. Analyze customer feedback (if applicable)
7. Generate executive reports
8. Export cleaned data and reports

---

## Project Structure

```text
├── app.py
├── pages/
│   ├── Data_Analytics.py
│   ├── AI_Assistant.py
│   ├── Feedback_Analytics.py
│   └── Report_Generation.py
│
├── utils/
├── assets/
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Future Enhancements

* Advanced predictive analytics and forecasting
* Multi-dataset analytics and comparison
* AI-powered anomaly detection
* Automated KPI discovery
* Interactive dashboard builder
* Custom report templates
* Real-time data source integration
* Cloud-based scalable analytics
* Enhanced business intelligence capabilities
* Enterprise reporting workflows

---

## Use Cases

* Customer Feedback Analysis
* Business Intelligence
* Sales Performance Evaluation
* Data Quality Assessment
* Executive Reporting
* Exploratory Data Analysis
* AI-Assisted Decision Making

---

## Author

**Rohith Mora**

Data Analytics | Artificial Intelligence | Business Intelligence

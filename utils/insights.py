# utils/insights.py

import streamlit as st


def generate_eda_summary(df):
    """
    Generate an automated EDA (Exploratory Data Analysis) summary string.
    Returns a concise text summary of the dataset.
    """
    from utils.data_cleaning import summarize_dataset
    
    summary = summarize_dataset(df)
    
    summary_text = (
        f"**Dataset Overview:**\n\n"
        f"- **Total Records:** {summary['total_records']}\n"
        f"- **Total Columns:** {summary['num_columns']}\n"
        f"- **Missing Values:** {summary['missing_values']}\n"
        f"- **Duplicate Rows:** {summary['duplicate_rows']}\n"
        f"- **Average Rating:** {summary['average_rating'] if summary['average_rating'] is not None else 'N/A'}\n\n"
        f"**Data Quality:** The dataset contains {summary['total_records']} records across {summary['num_columns']} columns. "
        f"There are {summary['missing_values']} missing values and {summary['duplicate_rows']} duplicate rows. "
        f"Detected rating field: {summary.get('rating_column', 'none') or 'none'}."
    )
    
    return summary_text


def generate_report_sections(df, stats, sentiment_df, categories, topics, rating_column=None):
    """
    Generate report sections as a dictionary with heading:body pairs.
    Used for executive summary and downloadable reports.
    """
    top_categories = categories.value_counts().head(5).to_dict() if not categories.empty else {}
    sentiment_counts = sentiment_df['sentiment'].value_counts().to_dict() if not sentiment_df.empty else {}
    
    findings = (
        f"The dataset contains {stats['total_records']} rows with {stats['num_columns']} columns. "
        f"There are {stats['missing_values']} missing values and {stats['duplicate_rows']} duplicates. "
    )
    if rating_column:
        findings += f"Detected rating field: {rating_column} with average score {stats['average_rating']}. "
    
    recommendations = (
        "Focus on resolving the most frequent issues by category, strengthen support response workflows, "
        "and optimize pricing communication for customers. "
    )
    
    return {
        "Executive Summary": (
            f"This report summarizes customer feedback analytics for {stats['total_records']} records. "
            f"The dataset shows {sentiment_counts.get('Positive', 0)} positive, {sentiment_counts.get('Neutral', 0)} neutral, "
            f"and {sentiment_counts.get('Negative', 0)} negative customer comments."
        ),
        "Key Findings": (
            f"Top categories include {', '.join(str(k) for k in top_categories.keys()) if top_categories else 'none'}. "
            f"Common topics extracted from feedback: {', '.join(str(t) for t in topics[:6]) if topics else 'no strong topics identified'}."
        ),
        "Sentiment Overview": (
            f"The sentiment profile is dominated by {max(sentiment_counts, key=sentiment_counts.get) if sentiment_counts else 'balanced'} responses. "
            f"Negative sentiment should be monitored in areas associated with delivery, product quality, support, and pricing."
        ),
        "Major Issues": (
            f"Customers most frequently mention {', '.join(str(k) for k in top_categories.keys()) if top_categories else 'general experience issues'}. "
            "Delivery delays and support responsiveness are high-priority areas for improvement."
        ),
        "Recommendations": recommendations,
    }


def query_groq(prompt, api_key):
    """
    Query Groq API with the latest working model
    """
    from groq import Groq
    
    try:
        client = Groq(api_key=api_key)
        
        message = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # ✅ CORRECT - Not decommissioned
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.7
        )
        
        return message.choices[0].message.content
    
    except Exception as e:
        raise Exception(f"Groq API Error: {str(e)}")


def query_mistral(prompt, api_key):
    """
    Query Mistral API with the latest API format
    """
    from mistralai import Mistral  # ✅ CORRECT NEW IMPORT
    
    try:
        client = Mistral(api_key=api_key)
        
        message = client.chat.complete(  # ✅ CORRECT METHOD
            model="mistral-small-latest",  # ✅ CORRECT MODEL
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.7
        )
        
        return message.choices[0].message.content
    
    except Exception as e:
        raise Exception(f"Mistral API Error: {str(e)}")


def get_ai_response(prompt, prefer_groq=True):
    """
    Universal function to get AI response
    Try preferred service first, fallback to other
    """
    import os
    
    groq_key = os.getenv("GROQ_API_KEY")
    mistral_key = os.getenv("MISTRAL_API_KEY")
    
    if prefer_groq:
        # Try Groq first
        if groq_key:
            try:
                return query_groq(prompt, groq_key), "✅ Groq"
            except Exception as groq_error:
                st.warning(f"Groq failed: {groq_error}")
                # Fallback to Mistral
                if mistral_key:
                    try:
                        return query_mistral(prompt, mistral_key), "✅ Mistral (fallback)"
                    except Exception as mistral_error:
                        return None, f"❌ Both failed - Groq: {groq_error} | Mistral: {mistral_error}"
                else:
                    return None, f"❌ Groq failed and no Mistral key"
        
        # If no Groq, try Mistral
        elif mistral_key:
            try:
                return query_mistral(prompt, mistral_key), "✅ Mistral"
            except Exception as e:
                return None, f"❌ Mistral failed: {e}"
        
        else:
            return None, "❌ No API keys configured"
    
    else:
        # Try Mistral first
        if mistral_key:
            try:
                return query_mistral(prompt, mistral_key), "✅ Mistral"
            except Exception as mistral_error:
                st.warning(f"Mistral failed: {mistral_error}")
                # Fallback to Groq
                if groq_key:
                    try:
                        return query_groq(prompt, groq_key), "✅ Groq (fallback)"
                    except Exception as groq_error:
                        return None, f"❌ Both failed - Mistral: {mistral_error} | Groq: {groq_error}"
                else:
                    return None, f"❌ Mistral failed and no Groq key"
        
        # If no Mistral, try Groq
        elif groq_key:
            try:
                return query_groq(prompt, groq_key), "✅ Groq"
            except Exception as e:
                return None, f"❌ Groq failed: {e}"
        
        else:
            return None, "❌ No API keys configured"
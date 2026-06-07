import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import pandas as pd


def plot_histogram(df, column, nbins=30):
    fig = px.histogram(
        df,
        x=column,
        nbins=nbins,
        title=f"Distribution of {column}",
        template="plotly_white",
        color_discrete_sequence=["#2563eb"],
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig


def plot_bar_chart(df, x, y, title=None):
    title = title or f"{y} by {x}"
    if x == "index" and "index" not in df.columns:
        fig = px.bar(
            df,
            x=df.index,
            y=y,
            title=title,
            template="plotly_white",
            color_discrete_sequence=["#1f78b4"],
        )
    else:
        fig = px.bar(
            df,
            x=x,
            y=y,
            title=title,
            template="plotly_white",
            color_discrete_sequence=["#1f78b4"],
        )
    fig.update_layout(xaxis_title=x if x != "index" else "index", yaxis_title=y, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def plot_sentiment_distribution(sentiment_counts):
    fig = px.pie(
        sentiment_counts,
        names=sentiment_counts.columns[0],
        values=sentiment_counts.columns[1],
        title="Sentiment distribution",
        color_discrete_sequence=["#0d6efd", "#198754", "#dc3545"],
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig


def plot_category_donut(category_counts):
    """
    Create a Donut chart for issue categories with percentages and counts.
    
    Args:
        category_counts: DataFrame with 'category' and 'count' columns
    
    Returns:
        Plotly figure object
    """
    if category_counts.empty:
        return None
    
    total = category_counts['count'].sum()
    category_counts['percentage'] = (category_counts['count'] / total * 100).round(1)
    
    # Create hover text with count and percentage
    hover_text = category_counts.apply(
        lambda row: f"<b>{row['category']}</b><br>Count: {row['count']}<br>Percentage: {row['percentage']}%",
        axis=1
    )
    
    fig = go.Figure(data=[go.Pie(
        labels=category_counts['category'],
        values=category_counts['count'],
        hole=0.4,
        hovertext=hover_text,
        hoverinfo='text',
        marker=dict(
            colors=['#d4af37', '#3498db', '#e74c3c', '#2ecc71'],
            line=dict(color='#f8f9fa', width=2)
        ),
        textposition='inside',
        textinfo='label+percent',
        textfont=dict(size=12, color='#0f172a'),
    )])
    
    fig.update_layout(
        title=dict(
            text="Issue Categories Distribution",
            font=dict(size=16, color='#0f172a')
        ),
        font=dict(family='Arial', size=12, color='#0f172a'),
        margin=dict(l=20, r=20, t=60, b=20),
        height=500,
        showlegend=True,
        legend=dict(
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='left',
            x=1.0
        )
    )
    
    return fig


def plot_topics_horizontal_bar(topics_list, top_n=10):
    """
    Create a Horizontal Bar chart for Top N most mentioned keywords.
    
    Args:
        topics_list: List of topics/keywords
        top_n: Number of top topics to display (default: 10)
    
    Returns:
        Plotly figure object
    """
    if not topics_list:
        return None
    
    # Count frequency of each topic
    from collections import Counter
    topic_counts = Counter(topics_list)
    
    # Get top N topics
    top_topics = dict(sorted(topic_counts.most_common(top_n), key=lambda x: x[1], reverse=True))
    
    df_topics = pd.DataFrame(list(top_topics.items()), columns=['Topic', 'Frequency'])
    df_topics = df_topics.sort_values('Frequency', ascending=True)  # Sort ascending for horizontal bar
    
    fig = px.bar(
        df_topics,
        y='Topic',
        x='Frequency',
        orientation='h',
        title=f"Top {min(top_n, len(df_topics))} Most Mentioned Keywords",
        template='plotly_white',
        color='Frequency',
        color_continuous_scale=['#3498db', '#2980b9'],
        text='Frequency'
    )
    
    fig.update_traces(
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Frequency: %{x}<extra></extra>',
        marker=dict(line=dict(color='#0f172a', width=0.5))
    )
    
    fig.update_layout(
        yaxis_title='Keywords',
        xaxis_title='Frequency (Mentions)',
        margin=dict(l=150, r=20, t=60, b=20),
        height=max(400, 30 * len(df_topics)),
        font=dict(family='Arial', size=11, color='#0f172a'),
        hovermode='closest',
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0')
    fig.update_yaxes(showgrid=False)
    
    return fig


def plot_trend_line(trend_df, date_col, value_col, title='Trend Over Time'):
    """
    Create a Line chart for trend analysis with markers and hover info.
    
    Args:
        trend_df: DataFrame with date and value columns
        date_col: Name of date column
        value_col: Name of value column (e.g., review count or average rating)
        title: Chart title
    
    Returns:
        Plotly figure object
    """
    if trend_df.empty:
        return None
    
    # Ensure date column is datetime
    trend_df = trend_df.copy()
    trend_df[date_col] = pd.to_datetime(trend_df[date_col], errors='coerce')
    trend_df = trend_df.dropna(subset=[date_col])
    trend_df = trend_df.sort_values(date_col)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=trend_df[date_col],
        y=trend_df[value_col],
        mode='lines+markers',
        name=value_col,
        line=dict(
            color='#d4af37',
            width=3,
            dash='solid'
        ),
        marker=dict(
            size=8,
            color='#d4af37',
            line=dict(color='#f8f9fa', width=2),
            symbol='circle'
        ),
        fill='tozeroy',
        fillcolor='rgba(212, 175, 55, 0.2)',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>' + f'{value_col}: %{{y}}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='#0f172a')
        ),
        xaxis_title='Date',
        yaxis_title=value_col,
        template='plotly_white',
        margin=dict(l=60, r=20, t=60, b=60),
        height=450,
        font=dict(family='Arial', size=11, color='#0f172a'),
        hovermode='x unified',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#e0e0e0',
            tickformat='%Y-%m-%d',
            tickangle=-45
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#e0e0e0'
        )
    )
    
    return fig


def create_wordcloud_image(text):
    if not text or len(text.strip()) == 0:
        return None
    
    # Filter out empty strings from text entries
    cleaned_text = " ".join([t for t in text.split() if t.strip()])
    
    if not cleaned_text or len(cleaned_text.strip()) == 0:
        return None
    
    try:
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            max_words=80,
            colormap="Blues",
        ).generate(cleaned_text)
        return wordcloud.to_image()
    except ValueError:
        return None

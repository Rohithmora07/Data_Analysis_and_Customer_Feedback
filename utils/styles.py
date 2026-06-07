import streamlit as st

PREMIUM_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

* {
    font-family: 'Poppins', sans-serif;
}

body {
    color: #0f172a;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

section.main {
    background: linear-gradient(135deg, #ffffff 0%, #fffbf0 100%);
    border-radius: 22px;
    padding: 1.5rem 1.25rem;
    border: 2.5px solid;
    border-image: linear-gradient(135deg, #d4af37 0%, #f4e4c1 50%, #d4af37 100%) 1;
    box-shadow:
        0 8px 32px rgba(212, 175, 55, 0.15),
        0 0 1px rgba(212, 175, 55, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(10px);
}

section.main .element-container,
section.main .stExpander,
section.main .stDataFrame,
section.main .stPlotlyChart,
section.main .stMarkdown,
section.main .stButton > button,
section.main [data-testid="metric-container"],
section.main [data-testid="fileUploader"],
section.main [data-testid="stExpander"] {
    border: 2px solid #d4af37 !important;
    border-radius: 18px;
    box-shadow: 0 4px 15px rgba(212, 175, 55, 0.1);
    transition: all 0.3s ease;
}

section.main .element-container:hover,
section.main .stExpander:hover {
    box-shadow: 0 8px 25px rgba(212, 175, 55, 0.2);
    border-color: #f4e4c1;
}

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #fef9f3 0%, #fffbf0 100%);
    border-radius: 16px;
    padding: 20px;
    color: #0f172a;
    border: 2px solid #d4af37 !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.6),
        0 8px 16px rgba(212, 175, 55, 0.2),
        0 0 20px rgba(212, 175, 55, 0.1);
    position: relative;
    overflow: hidden;
}

[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    animation: shine 3s infinite;
    pointer-events: none;
}

@keyframes shine {
    0% { left: -100%; }
    100% { left: 100%; }
}

.dashboard-card {
    background: linear-gradient(135deg, #fef9f3 0%, #fffbf0 100%);
    border-radius: 18px;
    padding: 24px;
    box-shadow:
        0 10px 30px rgba(212, 175, 55, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.5);
    border: 2px solid #d4af37;
    margin-bottom: 24px;
    transition: all 0.3s ease;
}

.dashboard-card:hover {
    box-shadow:
        0 15px 40px rgba(212, 175, 55, 0.18),
        inset 0 1px 0 rgba(255, 255, 255, 0.5);
    transform: translateY(-2px);
}

.clean-summary {
    background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
    border: 2px solid #d4af37;
    border-radius: 18px;
    padding: 20px;
    color: #0f5132;
    margin-bottom: 24px;
    box-shadow:
        0 6px 20px rgba(212, 175, 55, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.stButton > button {
    background: linear-gradient(135deg, #d4af37 0%, #e8c547 100%);
    color: #0f172a;
    font-weight: 600;
    border: 2px solid #b8941f;
    border-radius: 12px;
    padding: 10px 24px;
    transition: all 0.3s ease;
    box-shadow: 0 6px 20px rgba(212, 175, 55, 0.3);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #e8c547 0%, #f0d555 100%);
    box-shadow: 0 8px 28px rgba(212, 175, 55, 0.5);
    transform: translateY(-2px);
}

.stButton > button:active {
    transform: translateY(0px);
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
}

.comparison-table {
    width: 100%;
    border-collapse: collapse;
    border: 2px solid #d4af37;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(212, 175, 55, 0.1);
}

.comparison-table th {
    background: linear-gradient(90deg, #d4af37 0%, #f4e4c1 100%);
    color: #0f172a;
    padding: 12px;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid #b8941f;
}

.comparison-table td {
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid #d4af37;
    background: rgba(244, 228, 193, 0.02);
}

.comparison-table tr:last-child td {
    border-bottom: none;
}

.comparison-table tr:hover td {
    background: rgba(212, 175, 55, 0.08);
}

.stExpander {
    border: 2px solid #d4af37 !important;
    border-radius: 18px;
    box-shadow: 0 4px 15px rgba(212, 175, 55, 0.1);
}

.streamlit-expanderHeader {
    background: linear-gradient(90deg, rgba(212, 175, 55, 0.1) 0%, rgba(212, 175, 55, 0.05) 100%);
    border-radius: 16px;
    transition: all 0.3s ease;
}

.streamlit-expanderHeader:hover {
    background: linear-gradient(90deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.08) 100%);
}

section.sidebar {
    background: linear-gradient(180deg, #fef9f3 0%, #fffbf0 100%);
    border-right: 2.5px solid #d4af37;
}

.stAlert {
    border-radius: 16px;
    border: 2px solid #d4af37 !important;
    box-shadow: 0 4px 15px rgba(212, 175, 55, 0.1);
    border-left: 4px solid #d4af37;
}

[role="grid"] {
    border-radius: 16px !important;
    border: 2px solid #d4af37 !important;
}

h1 {
    background: linear-gradient(135deg, #d4af37 0%, #f4e4c1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
    letter-spacing: 0.5px;
}

h2, h3 {
    color: #0f172a;
    font-weight: 600;
    border-bottom: 2px solid #d4af37;
    padding-bottom: 10px;
    margin-top: 20px;
}

.stSelectbox > div > div {
    border: 2px solid #d4af37 !important;
    border-radius: 12px;
    background: linear-gradient(135deg, #ffffff 0%, #fffbf0 100%);
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.1);
}

[data-testid="fileUploader"] {
    border: 2px dashed #d4af37 !important;
    border-radius: 16px;
    padding: 20px;
    background: linear-gradient(135deg, rgba(244, 228, 193, 0.3) 0%, rgba(212, 175, 55, 0.1) 100%);
}

hr {
    border: 1px solid #d4af37;
    opacity: 0.3;
}

.success {
    color: #0f5132;
}

.warning {
    color: #664d03;
}

.error {
    color: #842029;
}

* {
    transition: color 0.2s ease, background-color 0.2s ease;
}
</style>
"""


def apply_premium_style():
    st.markdown(PREMIUM_STYLE, unsafe_allow_html=True)

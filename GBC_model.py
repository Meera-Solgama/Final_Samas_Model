import streamlit as st
import pandas as pd
import re
import joblib
import os

# Load trained model with compatibility handling
def load_model(model_path):
    try:
        return joblib.load(model_path)  # Load model safely
    except ModuleNotFoundError as e:
        if "_loss" not in str(e):  # Ignore '_loss' module error
            st.error(f"Error loading model: {e}. Try using the same scikit-learn version used for training.")
        return None
    except Exception as e:
        st.error(f"Unexpected error loading model: {e}")
        return None

model_path = "gbc_best_model.pkl"
model_data = load_model(model_path)

# Load dataset safely
file_path = "samas_dataset.xlsx"
if os.path.exists(file_path):
    df = pd.read_excel(file_path, engine="openpyxl")
else:
    st.error(f"Dataset file '{file_path}' not found. Please check the file path.")
    df = None

# Mapping of abbreviations to full Samas names
samas_mapping = {
    "D": "દ્વંદ્વ સમાસ",
    "T": "તત્પુરૂષ સમાસ",
    "M": "માધ્યમપદલોપી સમાસ",
    "U": "ઉપપદ સમાસ",
    "K": "કર્મધારય સમાસ",
    "B": "બહુવ્રિહી સમાસ",
    "DV": "દ્વીગુ સમાસ"
}

# Function to find compound words in a given text
def find_compound_words(text):
    if df is None:
        return []
    words = re.findall(r'\b[^\s]+\b', text)
    return [word for word in words if word in df["Word"].values]

# Function to replace compound words with their meanings
def replace_compound_words(text):
    compound_words = find_compound_words(text)
    replaced_text = text
    
    if df is not None:
        for word in compound_words:
            row = df[df["Word"] == word]
            if not row.empty:
                meaning = f"{row['sangna1'].values[0]} {row['Middle'].values[0]} {row['sangna2'].values[0]}"
                replaced_text = replaced_text.replace(word, meaning)
    
    return replaced_text, compound_words

# Function to list compound words with their Samas type
def list_compound_words_with_types(compound_words):
    if df is None:
        return ""
    
    compound_info = []
    for word in compound_words:
        row = df[df["Word"] == word]
        if not row.empty:
            label = row["Label"].values[0]
            full_samas_name = samas_mapping.get(label, label)
            compound_info.append(f"{word}: {full_samas_name}")
    
    return "\n".join(compound_info)

# Streamlit UI with styling
st.markdown(
    """
    <style>
        body {
            background: linear-gradient(135deg, #ff9a9e, #fad0c4);
            font-family: Arial, sans-serif;
        }
        .stApp {
            background: linear-gradient(135deg, #ff9a9e, #fad0c4);
            animation: gradientAnimation 10s infinite alternate;
        }
        @keyframes gradientAnimation {
            0% { background: linear-gradient(135deg, #ff9a9e, #fad0c4); }
            100% { background: linear-gradient(135deg, #a18cd1, #fbc2eb); }
        }
        .stTextArea textarea {
            background: white !important;
            border-radius: 10px;
            padding: 10px;
        }
        .stButton button {
            background: #4CAF50;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            transition: 0.3s;
        }
        .stButton button:hover {
            background: #45a049;
            transform: scale(1.05);
        }
        .stMarkdown h1 {
            color: #333366;
            text-align: center;
            font-size: 32px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }
        .marquee {
            width: 100%;
            overflow: hidden;
            white-space: nowrap;
            box-sizing: border-box;
            animation: marquee 10s linear infinite;
            font-size: 32px;
            font-weight: bold;
            color: #333366;
            text-align: center;
        }
        @keyframes marquee {
            from { transform: translateX(100%); }
            to { transform: translateX(-100%); }
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <div class='marquee'>મારો સમાસ ઓળખાવો?</div>
    """, unsafe_allow_html=True)

input_text = st.text_area("Enter Gujarati text:", height=150)

if st.button("Process Text"):
    if input_text.strip():
        replaced_text, compound_words = replace_compound_words(input_text)
        compound_list = list_compound_words_with_types(compound_words)
        
        st.subheader("Modified Text:")
        st.write(replaced_text)
        
        st.subheader("Identified Compound Words and Their Types:")
        if compound_list:
            st.text(compound_list)
        else:
            st.write("No compound words found.")
    else:
        st.warning("Please enter some text.")

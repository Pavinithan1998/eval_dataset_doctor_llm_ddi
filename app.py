import streamlit as st
import json
import random
from supabase import create_client, Client

SUPABASE_URL = "https://fektbbejaujrmedfltvp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZla3RiYmVqYXVqcm1lZGZsdHZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMwNjg3NzIsImV4cCI6MjA2ODY0NDc3Mn0.02SrZX0x_ZWTa0_stwWRwrAbJy7pTLgNGTu8svpXSVs"


TABLE_NAME = "doctor_evaluations"
DATA_FILE = "01_cleaned.jsonl"
NUM_SAMPLES = 200

# Connect to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load data
@st.cache_data
def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]
    random.shuffle(data)
    return data[:NUM_SAMPLES]

data = load_data()

if "index" not in st.session_state:
    st.session_state.index = 0

# Load already reviewed indices from Supabase
@st.cache_data
def get_reviewed_indices():
    response = supabase.table(TABLE_NAME).select("index").execute()
    return set(row["index"] for row in response.data)

logged_indices = get_reviewed_indices()

# Skip reviewed
while st.session_state.index in logged_indices and st.session_state.index < NUM_SAMPLES - 1:
    st.session_state.index += 1

if st.session_state.index >= NUM_SAMPLES:
    st.markdown("### ✅ All 200 entries reviewed.")
    st.stop()

entry = data[st.session_state.index]

# Display
st.markdown(f"### 🔬 Entry #{st.session_state.index + 1}")
st.markdown("#### 🧪 User Prompt")
st.markdown(f"```\n{entry['user']}\n```")
st.markdown("#### 🤖 Assistant Prediction")
st.markdown(f"```\n{entry['assistant']}\n```")

# Input
decision = st.radio("Is the reasoning correct?", ["Approve ✅", "Reject ❌"], key=f"decision_{st.session_state.index}")
comment = st.text_area("Comment (Optional)", key=f"comment_{st.session_state.index}")

# Submit
if st.button("✅ Save & Next"):
    result = {
        "index": st.session_state.index,
        "decision": decision,
        "comment": comment,
        "user": entry["user"],
        "assistant": entry["assistant"]
    }

    supabase.table(TABLE_NAME).insert(result).execute()
    st.success("Saved to Supabase!")

    st.session_state.index += 1
    st.experimental_rerun()

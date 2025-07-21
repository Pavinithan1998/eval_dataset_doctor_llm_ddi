import streamlit as st
import json
import random
import os

# Config
DATA_FILE = "01_cleaned.jsonl"
LOG_FILE = "doctor_evaluation_log.jsonl"
NUM_SAMPLES = 200

# Load and shuffle data
@st.cache_data
def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]
    random.shuffle(data)
    return data[:NUM_SAMPLES]

data = load_data()

# Maintain session index
if "index" not in st.session_state:
    st.session_state.index = 0

# Load previously evaluated indices
def load_logged_indices():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return set(int(json.loads(line)["index"]) for line in f)

logged_indices = load_logged_indices()

# Skip to next unevaluated entry
while st.session_state.index in logged_indices and st.session_state.index < NUM_SAMPLES - 1:
    st.session_state.index += 1

# If finished
if st.session_state.index >= NUM_SAMPLES:
    st.markdown("### ✅ All 200 entries have been reviewed.")
    st.stop()

# Current entry
entry = data[st.session_state.index]

# Display entry
st.markdown(f"### 🔬 Drug Interaction Evaluation #{st.session_state.index + 1}")
st.markdown("#### 🧪 **User Prompt**")
st.markdown(f"```\n{entry['user']}\n```")

st.markdown("#### 🤖 **Model Prediction**")
st.markdown(f"```\n{entry['assistant']}\n```")

# Doctor input
st.markdown("### 🩺 Doctor Evaluation")
decision = st.radio("Is the reasoning correct?", ["Approve ✅", "Reject ❌"], key=f"decision_{st.session_state.index}")
comment = st.text_area("Comments (Optional)", key=f"comment_{st.session_state.index}")

# Save & Next button
if st.button("✅ Save & Next"):
    result = {
        "index": st.session_state.index,
        "decision": decision,
        "comment": comment,
        "user": entry["user"],
        "assistant": entry["assistant"]
    }

    # Append to file (persistent storage)
    with open(LOG_FILE, "a", encoding="utf-8") as logf:
        logf.write(json.dumps(result, ensure_ascii=False) + "\n")

    st.success(f"Evaluation for entry #{st.session_state.index + 1} saved.")

    st.session_state.index += 1
    st.experimental_rerun()

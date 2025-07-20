import streamlit as st
import json
import random

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

# Persistent state
if "index" not in st.session_state:
    st.session_state.index = 0

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

# Save and next
if st.button("✅ Save & Next"):
    result = {
        "index": st.session_state.index,
        "decision": decision,
        "comment": comment,
        "user": entry["user"],
        "assistant": entry["assistant"]
    }

    # Append to log
    with open(LOG_FILE, "a", encoding="utf-8") as logf:
        logf.write(json.dumps(result, ensure_ascii=False) + "\n")

    st.success("Saved evaluation.")

    if st.session_state.index < NUM_SAMPLES - 1:
        st.session_state.index += 1
        st.experimental_rerun()
    else:
        st.markdown("### ✅ All 200 entries have been reviewed.")

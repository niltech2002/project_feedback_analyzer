# app.py

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import sqlite3

# =====================================================
# CONFIGURATION
# =====================================================

API_URL = "http://localhost:8000/analyze"

st.set_page_config(
    page_title="Customer Review Analyzer",
    page_icon="⭐",
    layout="wide"
)

# =====================================================
# SQLITE CONNECTION (COMMENTED FOR NOW)
# =====================================================

conn = sqlite3.connect(
    "reviews.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_text TEXT,
    label TEXT,
    score INTEGER,
    theme TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# =====================================================
# SESSION STATE
# =====================================================

if "history" not in st.session_state:
    st.session_state.history = []

# =====================================================
# HEADER
# =====================================================

st.title("⭐ AI Customer Review Analyzer")

st.markdown("""
Analyze customer reviews using **Gemini + FastAPI + Streamlit**
""")

st.divider()

# =====================================================
# MAIN LAYOUT
# =====================================================

left_col, right_col = st.columns([3, 1])

with left_col:

    review_text = st.text_area(
        "Enter Customer Review",
        height=200,
        placeholder="""
Example:

The product quality was excellent and delivery was very fast.
Customer service was responsive and helpful.
"""
    )

with right_col:

    st.info(
        """
### Analysis Includes

✅ Sentiment

✅ Score (1-10)

✅ Theme Detection

✅ JSON Output
"""
    )

# =====================================================
# ANALYZE BUTTON
# =====================================================

if st.button("🔍 Analyze Review", use_container_width=True):

    if not review_text.strip():

        st.warning("Please enter a review.")

    else:

        with st.spinner("Analyzing review..."):

            try:

                response = requests.post(
                    API_URL,
                    json={
                        "text": review_text
                    },
                    timeout=30
                )

                if response.status_code == 200:

                    result = response.json()

                    label = result.get("label", "N/A")
                    score = result.get("score", 0)
                    theme = result.get("theme", "N/A")

                    st.success("Analysis Completed Successfully")

                    st.divider()

                    # =====================================
                    # METRICS
                    # =====================================

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        emoji = "😐"

                        if label.lower() == "positive":
                            emoji = "😊"

                        elif label.lower() == "negative":
                            emoji = "😞"

                        st.metric(
                            "Sentiment",
                            f"{emoji} {label.upper()}"
                        )

                    with col2:

                        st.metric(
                            "Score",
                            f"{score}/10"
                        )

                    with col3:

                        st.metric(
                            "Theme",
                            theme
                        )

                    # =====================================
                    # SCORE PROGRESS BAR
                    # =====================================

                    st.subheader("Review Score")

                    st.progress(score / 10)

                    st.write(
                        f"Overall Rating: **{score}/10**"
                    )

                    # =====================================
                    # RAW JSON
                    # =====================================

                    with st.expander("View Raw JSON Response"):

                        st.json(result)

                    # =====================================
                    # SAVE HISTORY IN SESSION
                    # =====================================

                    history_record = {
                        "Timestamp": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "Review": review_text,
                        "Label": label,
                        "Score": score,
                        "Theme": theme
                    }

                    st.session_state.history.append(
                        history_record
                    )

                    # =====================================
                    # SAVE TO SQLITE (COMMENTED)
                    # =====================================

                    cursor.execute("""
                    INSERT INTO reviews
                    (
                        review_text,
                        label,
                        score,
                        theme
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        review_text,
                        label,
                        score,
                        theme
                    ))
                    
                    conn.commit()

                else:

                    st.error(
                        f"Backend returned status code {response.status_code}"
                    )

                    st.code(response.text)

            except requests.exceptions.ConnectionError:

                st.error(
                    """
Unable to connect to FastAPI backend.

Start backend using:

uvicorn main:app --reload
"""
                )

            except Exception as e:

                st.error(str(e))

# =====================================================
# HISTORY SECTION
# =====================================================

st.divider()

st.subheader("📜 Analysis History")

if st.session_state.history:

    history_df = pd.DataFrame(
        st.session_state.history
    )

    st.dataframe(
        history_df,
        use_container_width=True
    )

    csv_data = history_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇ Download History",
        data=csv_data,
        file_name="review_analysis_history.csv",
        mime="text/csv"
    )

else:

    st.info("No reviews analyzed yet.")

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("📊 Project Details")

    st.write("""
**Frontend**
- Streamlit

**Backend**
- FastAPI

**LLM**
- Gemini 3.5 Flash

**Database**
- SQLite3 (optional)

**Output**
- Sentiment
- Score
- Theme
""")

    st.divider()

    if st.button("🗑 Clear History"):

        st.session_state.history = []

        st.rerun()

    st.divider()

    st.caption(
        "Customer Review Analyzer v1.0"
    )
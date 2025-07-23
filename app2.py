import streamlit as st
from openai import OpenAI
import numpy as np
import pandas as pd


openai_api_key = st.secrets["OPENAI_API_KEY"]
ft_model        = st.secrets["FT_MODEL"]

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# ------------------------------------------
# App Layout
# ------------------------------------------
st.set_page_config(page_title="PHQ-9 Prediction App", layout="centered")
st.title("🧠 PHQ-9 Prediction with Explanation & Confidence")

# ------------------------------------------
# User Inputs
# ------------------------------------------
st.header("Enter Participant Transcripts")
happy   = st.text_area("Experience of Happiness:", height=150)
distress= st.text_area("Experience of Distress:", height=150)

# ------------------------------------------
# Prediction Trigger
# ------------------------------------------
if st.button("Predict Depression"):
    if not happy or not distress:
        st.error("Both transcripts are required to make a prediction.")
        st.stop()

    # Build system and user messages
    system_msg = (
        "You will be given a transcript of a participant talking about "
        "the topics of happiness and distress.\n"
        "1. Classify the transcript into one of the PHQ-9 scores (0–27).\n"
        "2. Write a brief explanation for your prediction by referring to evidence from the transcript.\n"
        "3. Highlight all significant words or phrases that influenced your decision, separated by commas."
    )
    user_prompt = (
        f"The following transcript describes an experience of happiness: {happy} "
        f"The following transcript describes an experience of distress: {distress} "
        "PHQ-9 score:"
    )

    # Call fine-tuned model
    response = client.chat.completions.create(
        model=ft_model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=0,
        top_p=1,
        logprobs=20,
        max_tokens=2000,
    )

    # --------------------------------------
    # Parse Model Output
    # --------------------------------------
    content = response.choices[0].message.content
    lines   = content.splitlines()
    try:
        score = int(lines[0].strip())
    except ValueError:
        score = None

    explanation = ""
    significant = ""
    for line in lines:
        if line.startswith("Explanation:"):
            explanation = line.split("Explanation:",1)[1].strip()
        if line.startswith("Significant words/phrases:"):
            significant = line.split("Significant words/phrases:",1)[1].strip()

    # --------------------------------------
    # Token-level probabilities
    # --------------------------------------
    top_logprobs = response.choices[0].logprobs.content[0].top_logprobs
    token_probs  = [[entry.token, float(np.exp(entry.logprob)*100)] for entry in top_logprobs]
    df_probs     = pd.DataFrame(token_probs, columns=["Token","Prob (%)"])

    # --------------------------------------
    # Grouped probability & confidence
    # --------------------------------------
    def safe_int(x):
        try: return int(x)
        except: return None

    grp0_4 = sum(p for t,p in token_probs if isinstance(safe_int(t),int) and 0 <= safe_int(t) <= 4)
    grp5_27= sum(p for t,p in token_probs if isinstance(safe_int(t),int) and 5 <= safe_int(t) <= 27)
    tot    = grp0_4 + grp5_27
    pct0_4 = (grp0_4/tot*100) if tot else 0
    pct5_27= (grp5_27/tot*100) if tot else 0
    confidence = abs(pct5_27-50)/50 if tot else 0
    depression = pct5_27 >= 50

    # --------------------------------------
    # Display Results
    # --------------------------------------
    st.subheader(f"Predicted PHQ-9 Score: {score}")
    st.markdown(f"**Explanation:** {explanation}")
    st.markdown(f"**Significant words/phrases:** {significant}")
    st.markdown("---")
    st.write("**Top token probabilities:**")
    st.dataframe(df_probs)
    st.write(f"**Grouped probability** (0–4 vs 5–27): {pct0_4:.2f}% vs {pct5_27:.2f}%")
    st.write(f"**Confidence:** {confidence:.2f}")
    st.write(f"**Depression predicted?** {'Yes' if depression else 'No'}")

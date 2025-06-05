import streamlit as st
from groq import Groq
from pathlib import Path

# -- GROQ SETTINGS --
API_KEY = "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"
GROQ_MODEL = "llama3-70b-8192"
groq_client = Groq(api_key=API_KEY)

st.set_page_config(page_title="Learning Objectives Generator", layout="wide")
st.title("🎓 Academic Learning Objectives Generator")

# -- Session state setup --
if "objectives" not in st.session_state:
    st.session_state.objectives = []
if "selected_objectives" not in st.session_state:
    st.session_state.selected_objectives = []
if "slides" not in st.session_state:
    st.session_state.slides = ""

# -- Topic input --
topic = st.text_input("Enter a topic:", placeholder="e.g., Matter")

# -- Generate Objectives --
if st.button("Generate Objectives") and topic.strip():
    with st.spinner("Generating objectives..."):
        prompt = (
            f"List concise academic learning objectives for the topic {topic}. "
            f"Each objective must be written as a single, complete sentence and contain no more than 10 words. "
            f"Do not use any sub-bullet points. Objectives should reflect the style and depth of university-level textbooks "
            f"while remaining clear, precise, and academically rigorous."
        )
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.choices[0].message.content
            st.session_state.objectives = [
                line.partition(".")[2].strip()
                for line in content.splitlines()
                if line.strip().startswith(tuple("123456789"))
            ]
            st.session_state.selected_objectives = []

        except Exception as e:
            st.error(f"❌ GROQ API error: {e}")

# -- Objective checkboxes --
if st.session_state.objectives:
    st.subheader("✅ Select Objectives to Build Slides:")
    for obj in st.session_state.objectives:
        if st.checkbox(obj, key=obj):
            if obj not in st.session_state.selected_objectives:
                st.session_state.selected_objectives.append(obj)
        else:
            if obj in st.session_state.selected_objectives:
                st.session_state.selected_objectives.remove(obj)

# -- Submit and generate slides --
if st.button("Submit Selected Objectives") and st.session_state.selected_objectives:
    with st.spinner("Generating slides..."):
        slide_prompt = (
            f"Thoroughly understand all the central themes of each objective below and extract the key ideas to develop two slides per objective. "
            f"Slides must be logically organized, information-rich, and easy to comprehend. "
            f"The structure should resemble a coherent mini-lecture, with smooth flow and logical sequence.\n\n"
            f"For each slide:\n"
            f"- Use two subheaders with emojis\n"
            f"- Under each, include one fully justified paragraph, consistently indented with no hanging indents\n"
            f"- Repeat the same large, bold title for each slide (Sitka Heading 24, no emojis)\n"
            f"- All content text in Aptos (Body) 14\n"
            f"- Format using outline or numbered styles\n"
            f"- Use bold or color for emphasis\n"
            f"- Clean spacing, no duplicate bullets, no image descriptions\n"
            f"- Language: clear, academic, freshman science level\n\n"
            f"Objectives:\n" + "\n".join(f"- {obj}" for obj in st.session_state.selected_objectives)
        )

        try:
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": slide_prompt}]
            )
            st.session_state.slides = response.choices[0].message.content
            st.markdown("---")
            st.subheader("🧑‍🏫 Generated Slides")
            st.markdown(st.session_state.slides)

        except Exception as e:
            st.error(f"❌ Slide generation failed: {e}")

# -- Generate HTML file --
if "slides" in st.session_state and st.session_state.slides:
    try:
        html_template = Path("live.html").read_text(encoding="utf-8")
        html_prompt = (
            "Place the text slides you generated in the working HTML code below. "
            "Make sure all the slides are inserted in this code.\n\n"
            "✳️ Only update the part inside const slides = [...].✳️ Do not alter any other part of the HTML, CSS, or JavaScript.✳️ Keep the formatting and styles identical, including bullet indentation (padding-left: 24px) and heading hierarchy.\n\n"
            "Build ONE responsive HTML file that displays the slides as flash-cards navigated by **Prev / Next** buttons.\n\n"
            "Everything must be inline (CSS + JS).\n\n"
            "All text slides must be encoded in the correct JSON format under const slides = [...].\n"
            "Each slide must contain: • \"title\" (string) • \"sections\" (array of { header: string, bullets: string[] })\n"
            "Preserve special characters (e.g., subscripts like H₂O, emojis, arrows) properly.\n"
            "Embed the entire JavaScript object inline into the final HTML file.\n"
            "Generate a single html file that contains every slide at once; do not create only a few slides and then prompt the user to generate the remainder.\n\n"
            "HTML:\n\n" + html_template + "\n\nSlides:\n\n" + st.session_state.slides
        )

        html_response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": html_prompt}]
        )

        final_html = html_response.choices[0].message.content
        Path("flashcards.html").write_text(final_html, encoding="utf-8")

        st.download_button("📥 Download Flashcard HTML", data=final_html, file_name="flashcards.html", mime="text/html")

    except Exception as e:
        st.error(f"❌ Failed to build flashcard site: {e}")

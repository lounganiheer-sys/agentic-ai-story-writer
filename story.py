import streamlit as st
import google.generativeai as genai      
import os
import requests
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph  #TO GIVE STRUCTURE TO PDF
from reportlab.lib.styles import getSampleStyleSheet     # For styling the PDF readymade
from reportlab.lib.pagesizes import letter

# ================================
# GEMINI API CONFIGURATION
# ================================
API_KEY = os.getenv("Gen_API")
if not API_KEY:
    st.error("API Key is missing! Set Gen_API as an environment variable.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash") #gemini-2.5-flash

# ================================
# AGENT FUNCTIONS (AGENTIC AI)
# ================================

def planner_agent(goal, genre, style):
    """Creates an outline and chapter plan"""
    prompt = f"""
    You are a planning AI.
    Goal: {goal}
    Genre: {genre}
    Style: {style}
    Create a clear 5-chapter outline with titles.
    """
    return model.generate_content(prompt).text


def writer_agent(outline):
    """Writes the full story based on outline"""
    prompt = f"""
    You are a story writer AI.
    Write a complete story using this outline:
    {outline}
    """
    return model.generate_content(prompt).text


def reviewer_agent(story):
    """Reviews and improves the story"""
    prompt = f"""
    You are a reviewer AI.
    Improve clarity, flow, and creativity of the story below:
    {story}
    """
    return model.generate_content(prompt).text

# ================================
# STREAMLIT UI
# ================================
st.title("🤖 Agentic AI Story Writer")
st.subheader("Goal → Plan → Write → Review (Autonomous AI)")

# User inputs ONLY GOAL
story_goal = st.text_area("Enter your story goal:", "Write a fantasy story for teenagers")

genres = ["Fantasy", "Science Fiction", "Mystery", "Horror", "Romance"]
styles = ["Classic", "Modern", "Poetic", "Descriptive"]

selected_genre = st.selectbox("Choose Genre", genres)
selected_style = st.selectbox("Choose Writing Style", styles)

# ================================
# SESSION MEMORY                                      #Is memory mein data page refresh hone par bhi safe rehta hai.
# ================================
if "outline" not in st.session_state:    
    st.session_state.outline = ""
if "story" not in st.session_state:
    st.session_state.story = ""

# ================================
# AGENTIC EXECUTION
# ================================
if st.button("🚀 Run Agentic AI"):
    with st.spinner("Planning..."):
        st.session_state.outline = planner_agent(story_goal, selected_genre, selected_style)

    with st.spinner("Writing story..."):
        st.session_state.story = writer_agent(st.session_state.outline)

    with st.spinner("Reviewing & improving..."):
        st.session_state.story = reviewer_agent(st.session_state.story)

    st.success("Story generated autonomously!")

# ================================
# DISPLAY RESULTS
# ================================
if st.session_state.outline:
    st.subheader("🧠 AI Plan (Outline)")
    st.write(st.session_state.outline)

if st.session_state.story:
    st.subheader("📖 Final Story")
    st.text_area("Edit if you want:", st.session_state.story, height=300)

# ================================
# PDF EXPORT
# ================================

def save_story_as_pdf():
    font_path = "NotoSans-Regular.ttf"

    if not os.path.exists(font_path):
        url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"
        r = requests.get(url)
        with open(font_path, "wb") as f:
            f.write(r.content)

    pdfmetrics.registerFont(TTFont("NotoSans", font_path))

    pdf = SimpleDocTemplate("story.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = "NotoSans"

    story_flow = [Paragraph(st.session_state.story.replace("\n", "<br/>") , style)]
    pdf.build(story_flow)

if st.button("📥 Download PDF"):
    save_story_as_pdf()
    with open("story.pdf", "rb") as f:
        st.download_button("Download Story as PDF", f, "story.pdf")
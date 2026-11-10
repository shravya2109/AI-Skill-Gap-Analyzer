import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from dotenv import load_dotenv
from resume_parser import parse_resume
from jd_parser import parse_jd
from llm_client import LLMClient
from skills_compare import compare_skills
from visualizations import render_advanced_visualizations

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="Resume Skill Gap Analyzer", layout="wide")

# Custom CSS for Professional UI
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        padding: 2rem 3rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #6c757d;
        font-size: 1.2rem;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    /* Card Styling */
    .upload-card, .jd-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        margin-bottom: 2rem;
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* File Uploader */
    .stFileUploader>div>div>div {
        background: #f8f9fa;
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader>div>div>div:hover {
        background: #e7f3ff;
        border-color: #764ba2;
    }
    
    /* Select Box and Toggle */
    .stSelectbox>div>div>div, .stToggle>div {
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    
    /* Text Area */
    .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 1px solid #dee2e6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        margin: 2rem 0;
    }
    
    .score-excellent {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
    }
    
    .score-good {
        background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        color: white;
    }
    
    .score-poor {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        color: white;
    }
    
    /* Skill Tags */
    .skill-matched {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        display: inline-block;
        font-weight: 500;
        box-shadow: 0 2px 10px rgba(72, 187, 120, 0.3);
    }
    
    .skill-missing {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        display: inline-block;
        font-weight: 500;
        box-shadow: 0 2px 10px rgba(245, 101, 101, 0.3);
    }
    
    .skill-extra {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        display: inline-block;
        font-weight: 500;
        box-shadow: 0 2px 10px rgba(66, 153, 225, 0.3);
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    /* Results Section */
    .results-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        margin: 2rem 0;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        border: none;
        border-radius: 10px;
    }
    
    .stError {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        border: none;
        border-radius: 10px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f8f9fa;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    
    /* Loading Spinner */
    .stSpinner {
        text-align: center;
    }
    
    /* Info Messages */
    .stInfo {
        background: linear-gradient(135deg, #e6fffa 0%, #b2f5ea 100%);
        border: none;
        border-radius: 10px;
        border-left: 4px solid #38b2ac;
    }
    
    /* Columns spacing */
    .stColumn > div {
        padding: 0 1rem;
    }

    body {
        background: #f4f6fb;
    }

    .hero-section {
        background: linear-gradient(135deg, #101828 0%, #1d2a44 100%);
        color: #f8fafc;
        padding: 3rem;
        border-radius: 24px;
        box-shadow: 0 30px 80px rgba(15, 23, 42, 0.35);
        margin-bottom: 2.5rem;
    }

    .hero-badge {
        display: inline-block;
        padding: 0.25rem 1rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.1);
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .hero-stats {
        margin-top: 2rem;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
    }

    .hero-stat-card {
        background: rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.15);
    }

    .hero-stat-card h3 {
        margin: 0;
        font-size: 1.8rem;
        color: #f8fafc;
    }

    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 15px 40px rgba(15, 23, 42, 0.08);
        border: 1px solid #edf2f7;
        height: 100%;
    }

    .info-card h4 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .step-card {
        background: #fff;
        border-radius: 18px;
        padding: 1.75rem;
        border: 1px solid #e4e7ec;
        box-shadow: 0 20px 45px rgba(15, 23, 42, 0.06);
        text-align: center;
    }

    .step-number {
        width: 48px;
        height: 48px;
        border-radius: 16px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    .action-card {
        background: #fff;
        border: 1px solid #e4e7ec;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
    }

    /* AI Analysis Styling */
    .ai-analysis-container {
        background: linear-gradient(135deg, #667eea 10%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        color: white;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
    }
    
    .analysis-section {
        background: rgba(255, 255, 255, 0.95);
        color: #2d3748;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }
    
    .analysis-header {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #667eea;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .skill-gap-item {
        background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #f56565;
    }
    
    .learning-item {
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #48bb78;
    }
    
    .project-item {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #4299e1;
    }
    
    .platform-link {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 500;
        margin: 0.25rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .platform-link:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        text-decoration: none;
        color: white;
    }
    
    .progress-bar {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        height: 8px;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: white;
    }
    
    .stat-label {
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.9rem;
    }

    /* Visualization Containers */
    .viz-container {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
    }
    
    .viz-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1.5rem;
        text-align: center;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    .chart-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .metric-viz {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        border-left: 4px solid #667eea;
    }
    
    .skill-category {
        background: rgba(102, 126, 234, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 3px solid #667eea;
    }

    /* Divider */
    hr {
        margin: 3rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state before rendering views
if "show_analyzer" not in st.session_state:
    st.session_state.show_analyzer = False

# Main Content will be rendered via dedicated views below


def render_home():
    st.markdown(
        """
        <section class="hero-section">
            <span class="hero-badge">New · AI Career Companion</span>
            <h1 style="font-size: 3.2rem; margin: 0.5rem 0;">Bridge the gap between your resume and dream role.</h1>
            <p style="font-size: 1.2rem; max-width: 720px; color: #e2e8f0;">
                Upload your resume, paste a job description, and let our Gemini-powered engine instantly detect matched skills,
                highlight gaps, and craft a personalized growth roadmap.
            </p>
            <div class="hero-stats">
                <div class="hero-stat-card">
                    <h3>500+</h3>
                    <p>Skills tracked</p>
                </div>
                <div class="hero-stat-card">
                    <h3>60s</h3>
                    <p>Average turnaround</p>
                </div>
                <div class="hero-stat-card">
                    <h3>100%</h3>
                    <p>AI-assisted insights</p>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    feature_cols = st.columns(3)
    feature_data = [
        ("⚡ Real-time analysis", "Extract and compare skills on the fly with enterprise-grade NLP."),
        ("🧠 AI coaching", "Receive curated project ideas, learning paths, and resume phrasing."),
        ("📊 Insightful visuals", "Beautiful scorecards that recruiters would love to see."),
    ]
    for col, data in zip(feature_cols, feature_data):
        with col:
            st.markdown(
                f"""
                <div class="info-card">
                    <div style='font-size: 2rem;'>{data[0][0]}</div>
                    <h4>{data[0][2:]}</h4>
                    <p>{data[1]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("""<p style='margin-top:2rem; font-weight:600;'>How it works</p>""", unsafe_allow_html=True)
    step_cols = st.columns(3)
    steps = [
        ("Upload", "Drop your resume and JD"),
        ("Compare", "See matches & gaps in seconds"),
        ("Grow", "Follow tailored AI guidance"),
    ]
    for idx, (col, (title, subtitle)) in enumerate(zip(step_cols, steps), start=1):
        with col:
            st.markdown(
                f"""
                <div class="step-card">
                    <div class="step-number">{idx}</div>
                    <h4>{title}</h4>
                    <p>{subtitle}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    cta_cols = st.columns([1, 1, 1])
    with cta_cols[1]:
        if st.button("Get Started →", key="cta_get_started"):
            st.session_state.show_analyzer = True
            st.rerun()


def render_analyzer():
    st.markdown('<h1 class="main-header">Resume Skill Gap Analyzer</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Upload your resume and job description to discover strengths, gaps, and tailored AI recommendations.</p>',
        unsafe_allow_html=True,
    )

    resume_text = ""
    jd_text = ""

    # Resume Upload Section
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-header">📄 Upload Resume</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        resume_file = st.file_uploader("Choose your resume file", type=["pdf", "docx", "txt"], help="Supported formats: PDF, DOCX, TXT")
    with col2:
        experience_level = st.selectbox("📊 Experience Level", ["Entry Level", "Mid Level", "Senior Level"], key="experience_level")
    
    if resume_file:
        with st.spinner("🔄 Parsing resume..."):
            resume_text = parse_resume(resume_file)
            st.success("✅ Resume parsed successfully!")
            with st.expander("📋 Show Extracted Text"):
                st.text_area("Resume Content", resume_text, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

    # Job Description Section
    st.markdown('<div class="jd-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-header">🎯 Job Description</h3>', unsafe_allow_html=True)
    jd_input_method = st.radio("📥 Input Method", ["Paste Text", "Upload File"], horizontal=True)
    if jd_input_method == "Paste Text":
        jd_text = st.text_area("📝 Paste Job Description Here", height=300, placeholder="Paste requirements, responsibilities, and culture notes...")
    else:
        jd_file = st.file_uploader("📁 Upload JD File", type=["pdf", "docx", "txt"], help="Upload job description file", key="jd_file")
        if jd_file:
            with st.spinner("🔄 Parsing job description..."):
                jd_text = parse_jd(jd_file)
                st.success("✅ Job description parsed successfully!")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="action-card">
            <h4 style='margin-top:0;'>Ready for AI Analysis</h4>
            <p style='margin-bottom:1rem;'>Upload your resume and job description, then click Analyze to get your skill match score, gap analysis, and comprehensive AI career coaching recommendations.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Analyze Skill Gap 🔍", key="analyze_button", use_container_width=True):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("❌ Gemini API Key not found. Please add your API key to the .env file.")
            st.code("GEMINI_API_KEY=your_api_key_here", language="bash")
            st.info("💡 Get your free API key from [Google AI Studio](https://aistudio.google.com/)")
        elif not resume_text:
            st.error("Please upload a resume.")
        elif not jd_text:
            st.error("Please provide a job description.")
        else:
            try:
                llm = LLMClient(provider="Gemini", api_key=api_key)

                with st.spinner("Extracting skills using AI..."):
                    resume_skills = llm.extract_skills(resume_text)
                    jd_skills = llm.extract_skills(jd_text)

                if not resume_skills or not jd_skills:
                    st.error("Could not extract skills. Please check the input text.")
                else:
                    comparison = compare_skills(resume_skills, jd_skills)

                    st.divider()
                    st.header("📊 Analysis Results")

                    score_class = "score-excellent" if comparison['score'] >= 70 else "score-good" if comparison['score'] >= 40 else "score-poor"
                    st.markdown(
                        f"""
                        <div class="metric-card {score_class}">
                            <h2 style=\"margin: 0; font-size: 1.2rem;\">🎯 Match Score</h2>
                            <h1 style=\"margin: 10px 0; font-size: 3rem; font-weight: 700;\">{comparison['score']}%</h1>
                            <p style=\"margin: 0; opacity: 0.9;\">{'Excellent Match!' if comparison['score'] >= 70 else 'Good Match!' if comparison['score'] >= 40 else 'Needs Improvement'}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown('<div class="results-container">', unsafe_allow_html=True)
                    res_col1, res_col2, res_col3 = st.columns(3)

                    with res_col1:
                        st.markdown('<h3 class="section-header">✅ Matched Skills</h3>', unsafe_allow_html=True)
                        if comparison['matched']:
                            skills_html = "".join([f'<span class="skill-matched">{skill}</span>' for skill in comparison['matched']])
                            st.markdown(skills_html, unsafe_allow_html=True)
                        else:
                            st.info("No direct matches found.")

                    with res_col2:
                        st.markdown('<h3 class="section-header">❌ Missing Skills</h3>', unsafe_allow_html=True)
                        if comparison['missing']:
                            skills_html = "".join([f'<span class="skill-missing">{skill}</span>' for skill in comparison['missing']])
                            st.markdown(skills_html, unsafe_allow_html=True)
                        else:
                            st.success("🎉 No missing skills!")

                    with res_col3:
                        st.markdown('<h3 class="section-header">➕ Extra Skills</h3>', unsafe_allow_html=True)
                        if comparison['extra']:
                            skills_html = "".join([f'<span class="skill-extra">{skill}</span>' for skill in comparison['extra']])
                            st.markdown(skills_html, unsafe_allow_html=True)
                        else:
                            st.info("No additional skills found.")
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Add advanced visualizations
                    st.divider()
                    render_advanced_visualizations(comparison, resume_skills, jd_skills, experience_level)

                    # Always run AI analysis automatically
                    st.divider()
                    st.markdown(
                        f"""
                        <div class="ai-analysis-container">
                            <h2 style="margin: 0; text-align: center; font-size: 2.2rem;">🤖 AI Career Coach Analysis</h2>
                            <p style="text-align: center; margin: 0.5rem 0; opacity: 0.9;">Comprehensive insights powered by advanced AI</p>
                            <div class="stat-grid">
                                <div class="stat-card">
                                    <div class="stat-number">{len(resume_skills)}</div>
                                    <div class="stat-label">Resume Skills</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-number">{len(jd_skills)}</div>
                                    <div class="stat-label">Required Skills</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-number">{len(comparison['missing'])}</div>
                                    <div class="stat-label">Skills to Learn</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-number">{comparison['score']}%</div>
                                    <div class="stat-label">Match Score</div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    with st.spinner("🧠 Generating comprehensive career analysis and recommendations..."):
                        suggestions = llm.get_suggestions(
                            comparison['matched'],
                            jd_skills,
                            comparison['missing'],
                            experience_level
                        )
                        st.markdown('<div class="results-container">', unsafe_allow_html=True)
                        st.markdown(suggestions, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")


# Initialize session state
if 'show_analyzer' not in st.session_state:
    st.session_state.show_analyzer = False

if not st.session_state.show_analyzer:
    render_home()
else:
    render_analyzer()


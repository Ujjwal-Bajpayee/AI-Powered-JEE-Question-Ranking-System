import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import logging
from dotenv import load_dotenv
import time


from agents.reader_agent import ReaderAgent
from agents.relevance_agent import RelevanceAgent
from agents.depth_agent import DepthAgent
from agents.judge_agent import JudgeAgent


from langchain_groq import ChatGroq



try:
    load_dotenv()
except:
    pass 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


st.set_page_config(
    page_title="Ujjwal Submission",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
<style>
    /* Set overall soft day theme */
    .stApp {
        background: linear-gradient(135deg, #fafafa 0%, #f5f7fa 50%, #f0f4f8 100%);
        color: #2d3748;
        min-height: 100vh;
    }
    
    .main-title {
        text-align: center;
        color: #2d3748;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
        text-shadow: none;
        background: linear-gradient(45deg, #4a5568, #718096, #a0aec0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .subtitle {
        text-align: center;
        color: #4a5568;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    .step-box {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        color: #2d3748;
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
    }
    
    .step-box h3 {
        color: #2b6cb0 !important;
        margin-bottom: 1rem;
        font-weight: 500;
        font-size: 1.4rem;
    }
    
    .step-box p {
        color: #4a5568 !important;
        margin: 0.5rem 0;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Upload section styling */
    .upload-section {
        background: linear-gradient(135deg, #f0fff4 0%, #f7fafc 100%);
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border: 1px solid #c6f6d5;
        text-align: center;
    }
    
    .upload-section h4 {
        color: #2b6cb0 !important;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    .upload-section p {
        color: #4a5568 !important;
        margin: 0.5rem 0;
    }
    
    .question-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        color: #2d3748;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    .question-card h4 {
        color: #2b6cb0 !important;
        margin-bottom: 1rem;
        font-weight: 500;
        font-size: 1.2rem;
    }
    
    .question-card p {
        color: #4a5568 !important;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .rank-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        color: #2d3748;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border-left: 4px solid;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
    }
    
    .rank-card h3 {
        color: #2d3748 !important;
        margin-bottom: 1rem;
        font-weight: 500;
        font-size: 1.3rem;
    }
    
    .rank-card p {
        color: #4a5568 !important;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .rank-1 { 
        border-left-color: #d69e2e;
        background: linear-gradient(135deg, #fffbeb 0%, #fefcbf 100%);
    }
    
    .rank-2 { 
        border-left-color: #718096;
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
    }
    
    .rank-3 { 
        border-left-color: #c05621;
        background: linear-gradient(135deg, #fffaf0 0%, #feebc8 100%);
    }
    
    .info-box {
        background: linear-gradient(135deg, #e6fffa 0%, #f0fff4 100%);
        border: 1px solid #9ae6b4;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        color: #2d3748;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    .info-box h4 {
        color: #22543d !important;
        margin-bottom: 1rem;
        font-weight: 500;
        font-size: 1.2rem;
    }
    
    .info-box p {
        color: #2d3748 !important;
        margin: 0.5rem 0;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fffaf0 0%, #feebc8 100%);
        border: 1px solid #fbb040;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        color: #2d3748;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    .warning-box h4 {
        color: #7c2d12 !important;
        margin-bottom: 1rem;
        font-weight: 500;
        font-size: 1.2rem;
    }
    
    .warning-box p {
        color: #2d3748 !important;
        margin: 0.5rem 0;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .success-box {
        background: linear-gradient(135deg, #f0fff4 0%, #dcfce7 100%);
        border: 1px solid #9ae6b4;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        color: #2d3748;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    .success-box h4 {
        color: #22543d !important;
        margin-bottom: 1rem;
        font-weight: 500;
        font-size: 1.2rem;
    }
    
    .success-box p {
        color: #2d3748 !important;
        margin: 0.5rem 0;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .metric-box {
        background: linear-gradient(135deg, #fdf2f8 0%, #fce7f3 100%);
        border: 1px solid #f687b3;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: #2d3748;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    .metric-box h4 {
        color: #97266d !important;
        margin-bottom: 1rem;
        font-weight: 500;
        font-size: 1.1rem;
    }
    
    .metric-box h2 {
        color: #2d3748 !important;
        margin: 1rem 0;
        font-weight: 600;
        font-size: 2.2rem;
    }
    
    .metric-box p {
        color: #4a5568 !important;
        margin: 0;
        font-size: 0.9rem;
        font-weight: 400;
    }
    
    /* Streamlit overrides for soft theme */
    .stMarkdown p {
        color: #2d3748 !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #2d3748 !important;
    }
    
    .stMarkdown strong {
        color: #2b6cb0 !important;
        font-weight: 600;
    }
    
    .stMarkdown em {
        color: #4a5568 !important;
        font-style: italic;
    }
    
    /* Simple button styling */
    .stButton button {
        color: #ffffff !important;
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%) !important;
        border: 1px solid #3182ce !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 1rem !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Simple slider styling */
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%) !important;
    }
    
    /* Clean background for main content */
    .main .block-container {
        background: transparent;
        padding-top: 2rem;
        max-width: 1000px;
    }
    
    /* Simple progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%) !important;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background: #ffffff !important;
        color: #2d3748 !important;
        border: 1px solid #cbd5e0 !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4299e1 !important;
        box-shadow: 0 0 0 1px #4299e1 !important;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border: 2px dashed #cbd5e0 !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background: linear-gradient(135deg, #f0fff4 0%, #dcfce7 100%) !important;
        color: #2d3748 !important;
        border-radius: 8px !important;
        border: 1px solid #9ae6b4 !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%) !important;
        color: #2d3748 !important;
        border-radius: 8px !important;
        border: 1px solid #fc8181 !important;
    }
    
    /* Remove decorative elements */
    .stApp::before {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

class SimpleJEEAnalyzer:
    
    def __init__(self):
        self.setup_session_state()
        self.load_questions()
        
    def setup_session_state(self):
        """Initialize session state variables."""
        if 'analysis_complete' not in st.session_state:
            st.session_state.analysis_complete = False
        if 'reader_analyses' not in st.session_state:
            st.session_state.reader_analyses = []
        if 'relevance_scores' not in st.session_state:
            st.session_state.relevance_scores = []
        if 'depth_scores' not in st.session_state:
            st.session_state.depth_scores = []
        if 'final_ranking' not in st.session_state:
            st.session_state.final_ranking = {}
        if 'current_questions' not in st.session_state:
            st.session_state.current_questions = []
        if 'question_source' not in st.session_state:
            st.session_state.question_source = "sample"
    
    def load_questions(self):
        """Load sample questions from JSON file."""
        try:
            with open('data/sample_questions.json', 'r') as f:
                self.sample_questions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            st.warning("""
            ⚠️ **Sample questions file not found.** 
            
            You can still use this app by uploading your own questions in JSON format.
            """)
            self.sample_questions = []
    
    def validate_questions_format(self, questions):
        """Validate the format of uploaded questions."""
        if not isinstance(questions, list):
            return False, "File should contain a list of questions."
        
        if len(questions) != 10:
            return False, f"Please upload exactly 10 questions. Found {len(questions)} questions."
        
        required_fields = ['id', 'question_text', 'topic', 'tags', 'bloom_level']
        
        for i, question in enumerate(questions, 1):
            if not isinstance(question, dict):
                return False, f"Question {i} should be an object/dictionary."
            
            for field in required_fields:
                if field not in question:
                    return False, f"Question {i} is missing required field: '{field}'"
                    
            # Additional validation
            if not isinstance(question['id'], int):
                return False, f"Question {i}: 'id' should be a number."
            if not isinstance(question['question_text'], str) or not question['question_text'].strip():
                return False, f"Question {i}: 'question_text' should be a non-empty string."
            if not isinstance(question['topic'], str) or not question['topic'].strip():
                return False, f"Question {i}: 'topic' should be a non-empty string."
            if not isinstance(question['tags'], list):
                return False, f"Question {i}: 'tags' should be a list."
        
        return True, "Valid format!"
    
    # Replace the upload_questions_interface method (around line 530) with this:
    def upload_questions_interface(self):
        """Interface for uploading custom questions."""
        st.markdown("""
        <div class="upload-section">
            <h4>Upload Your Own 10 Questions</h4>
            <p>Upload a JSON file with your own JEE physics questions to analyze</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a JSON file with your questions",
            type="json",
            help="Upload a JSON file containing exactly 10 JEE physics questions"
        )
        
        if uploaded_file is not None:
            try:
                uploaded_questions = json.load(uploaded_file)
                
                # Validate the format
                is_valid, message = self.validate_questions_format(uploaded_questions)
                
                if is_valid:
                    st.session_state.current_questions = uploaded_questions
                    st.session_state.question_source = "uploaded"
                    st.session_state.analysis_complete = False  # Reset analysis
                    
                    st.success(f"Successfully loaded {len(uploaded_questions)} questions!")
                    
                    # Preview uploaded questions
                    st.markdown("#### Preview of Your Questions:")
                    for i, q in enumerate(uploaded_questions[:3], 1):
                        st.markdown(f"**Q{q['id']}:** {q['question_text'][:80]}...")
                    if len(uploaded_questions) > 3:
                        st.write(f"... and {len(uploaded_questions) - 3} more questions")
                else:
                    st.error(f"{message}")
                    
            except json.JSONDecodeError:
                st.error("Invalid JSON file. Please upload a valid JSON file.")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
        # Show required format
        with st.expander("Required JSON Format (Click to see example)"):
            st.markdown("Your JSON file should look exactly like this:")
            sample_format = [
                {
                    "id": 1,
                    "question_text": "A block of mass 2 kg slides down a frictionless incline of angle 30°. Find the acceleration of the block.",
                    "topic": "Mechanics",
                    "tags": ["forces", "inclined plane", "acceleration"],
                    "bloom_level": "Apply"
                },
                {
                    "id": 2,
                    "question_text": "A uniform rod of length L and mass M is pivoted at one end. Find the moment of inertia about the pivot.",
                    "topic": "Rotational Mechanics",
                    "tags": ["moment of inertia", "rotation", "rigid body"],
                    "bloom_level": "Apply"
                }
            ]
            st.json(sample_format)
            st.markdown("**Important:** Make sure you have exactly 10 questions with IDs 1-10")
    
    # Replace the question_source_selector method (around line 580) with this:
    def question_source_selector(self):
        """Allow user to choose between sample and uploaded questions."""
        st.markdown("---")
        st.header("Choose Your Question Set")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="info-box">
                <h4>Use Sample Questions</h4>
                <p>Start with our carefully selected 10 JEE physics questions covering various topics</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Use Sample Questions", use_container_width=True):
                st.session_state.current_questions = self.sample_questions
                st.session_state.question_source = "sample"
                st.session_state.analysis_complete = False
                st.rerun()
        
        with col2:
            st.markdown("""
            <div class="warning-box">
                <h4>Upload My Questions</h4>
                <p>Upload your own 10 JEE physics questions in JSON format for personalized analysis</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Upload My Questions", use_container_width=True):
                st.session_state.question_source = "upload_mode"
                st.session_state.analysis_complete = False
                st.rerun()
    
    def display_current_question_info(self):
        """Display information about currently loaded questions."""
        if st.session_state.current_questions:
            if st.session_state.question_source == "sample":
                st.markdown("""
                <div class="success-box">
                    <h4>📖 Using Sample Questions</h4>
                    <p>Currently loaded: <strong>10 sample JEE physics questions</strong> covering mechanics, electricity, waves, and more.</p>
                </div>
                """, unsafe_allow_html=True)
            elif st.session_state.question_source == "uploaded":
                st.markdown("""
                <div class="success-box">
                    <h4>📤 Using Your Uploaded Questions</h4>
                    <p>Currently loaded: <strong>10 custom questions</strong> that you uploaded.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Option to change question set
            if st.button("🔄 Change Question Set", type="secondary"):
                st.session_state.question_source = "choose"
                st.session_state.analysis_complete = False
                st.rerun()
    
    def initialize_agents(self):
        """Initialize AI agents."""
        try:
            # Try to get API key from environment variables or Streamlit secrets
            api_key = os.getenv('GROQ_API_KEY')
            
            # If not found in environment, try Streamlit secrets
            if not api_key:
                try:
                    api_key = st.secrets["GROQ_API_KEY"]
                except:
                    pass
            
            if not api_key:
                st.error("""
                🔑 **API Key Required!**
                
                To use this app, you need to provide a GROQ API key. Here's how:
                
                **For Local Development:**
                - Create a `.env` file in your project folder
                - Add: `GROQ_API_KEY=your_api_key_here`
                
                **For Streamlit Cloud Deployment:**
                - Go to your app settings on Streamlit Cloud
                - Add `GROQ_API_KEY` in the Secrets section
                - Format: `GROQ_API_KEY = "your_api_key_here"`
                
                **Get a free API key:** Visit [console.groq.com](https://console.groq.com) to get your free API key.
                """)
                return None, None, None, None
            
            llm = ChatGroq(
                model="meta-llama/llama-4-scout-17b-16e-instruct",  
                temperature=0.1,
                groq_api_key=api_key,
                max_retries=2,
                request_timeout=30
            )
            
            reader = ReaderAgent(llm)
            relevance = RelevanceAgent(llm)
            depth = DepthAgent(llm)
            judge = JudgeAgent(llm)
            
            return reader, relevance, depth, judge
            
        except Exception as e:
            st.error(f"Failed to initialize AI system: {str(e)}")
            return None, None, None, None
    
    def run_analysis(self, importance_weight: float, difficulty_weight: float):
        """Run the analysis with simple progress tracking."""
        reader, relevance, depth, judge = self.initialize_agents()
        
        if not all([reader, relevance, depth, judge]):
            return
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Use current questions (either sample or uploaded)
            questions_to_analyze = st.session_state.current_questions
            
            # Step 1: Analyze questions
            status_text.markdown("### Step 1: Reading and understanding each question...")
            time.sleep(1)
            progress_bar.progress(25)
            
            reader_analyses = []
            for question in questions_to_analyze:
                analysis = reader.analyze_question(question)
                reader_analyses.append(analysis)
            
            st.session_state.reader_analyses = reader_analyses
            
            # Step 2: Score for exam importance
            status_text.markdown("### Step 2: Checking how likely each question is to appear in JEE...")
            time.sleep(1)
            progress_bar.progress(50)
            
            relevance_scores = []
            for analysis in reader_analyses:
                score = relevance.score_question(analysis)
                relevance_scores.append(score)
            
            st.session_state.relevance_scores = relevance_scores
            
            # Step 3: Score for difficulty
            status_text.markdown("### Step 3: Measuring how challenging each question is...")
            time.sleep(1)
            progress_bar.progress(75)
            
            depth_scores = []
            for analysis in reader_analyses:
                score = depth.score_question(analysis)
                depth_scores.append(score)
            
            st.session_state.depth_scores = depth_scores
            
            # Step 4: Make final decision
            status_text.markdown("### Step 4: Choosing the TOP 3 most important questions...")
            time.sleep(1)
            progress_bar.progress(90)
            
            try:
                final_ranking = judge.rank_questions(
                    reader_analyses, relevance_scores, depth_scores,
                    importance_weight, difficulty_weight
                )
            except:
                # Simple fallback if AI fails
                final_ranking = self.create_simple_ranking(
                    reader_analyses, relevance_scores, depth_scores,
                    importance_weight, difficulty_weight
                )
            
            st.session_state.final_ranking = final_ranking
            
            progress_bar.progress(100)
            status_text.markdown("### ✅ Done! Your TOP 3 questions are ready!")
            st.session_state.analysis_complete = True
            
            time.sleep(2)
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"❌ Something went wrong: {str(e)}")
            progress_bar.empty()
            status_text.empty()
    
    def create_simple_ranking(self, reader_analyses, relevance_scores, depth_scores, importance_weight, difficulty_weight):
        """Create a simple ranking when complex AI fails."""
        scores = []
        
        for i, reader_analysis in enumerate(reader_analyses):
            question_id = reader_analysis["original_question"]["id"]
            
            relevance_score = next((r for r in relevance_scores if r["question_id"] == question_id), None)
            depth_score = next((d for d in depth_scores if d["question_id"] == question_id), None)
            
            if relevance_score and depth_score:
                importance_val = relevance_score["overall_relevance_score"]
                difficulty_val = depth_score["overall_depth_score"]
                final_score = (importance_val * importance_weight) + (difficulty_val * difficulty_weight)
                
                scores.append({
                    "question_id": question_id,
                    "question_text": reader_analysis["original_question"]["question_text"],
                    "final_score": final_score,
                    "importance_score": importance_val,
                    "difficulty_score": difficulty_val
                })
        
        scores.sort(key=lambda x: x["final_score"], reverse=True)
        top_3 = scores[:3]
        
        return {
            "top_3_questions": [
                {
                    "rank": i + 1,
                    "question_id": q["question_id"],
                    "question_text": q["question_text"],
                    "final_score": q["final_score"],
                    "relevance_contribution": q["importance_score"] * importance_weight,
                    "depth_contribution": q["difficulty_score"] * difficulty_weight,
                    "selection_reasoning": f"This question earned rank #{i+1} due to its high exam importance score of {q['importance_score']:.1f}/10 and optimal difficulty level of {q['difficulty_score']:.1f}/10. {'This represents a high-priority JEE topic that appears frequently in exams.' if q['importance_score'] > 7 else 'This covers important JEE concepts worth practicing.'} The difficulty level {'provides appropriate challenge for JEE preparation' if q['difficulty_score'] > 6 else 'makes it accessible for building foundational understanding'}. Combined score: {q['final_score']:.2f}/10."
                } for i, q in enumerate(top_3)
            ],
            "overall_analysis": f"AI has analyzed all {len(scores)} questions based on their importance for JEE exam success and appropriate difficulty level for effective learning.",
            "methodology": f"Questions were evaluated using a weighted scoring system: {importance_weight*100:.0f}% exam importance (topic frequency, syllabus relevance) and {difficulty_weight*100:.0f}% difficulty level (conceptual depth, problem complexity)."
        }
    
    def display_questions(self):
        """Display the available questions in a user-friendly way."""
        if not st.session_state.current_questions:
            return
            
        st.markdown("---")
        st.header("📋 Questions Available for Analysis")
        
        question_source_text = "sample" if st.session_state.question_source == "sample" else "your uploaded"
        
        st.markdown(f"""
        <div class="info-box">
            <h4>📊 What you'll see below:</h4>
            <p><strong>10 JEE Physics questions</strong> from {question_source_text} question set that our AI will analyze to find the TOP 3 most important ones for your exam preparation.</p>
        </div>
        """, unsafe_allow_html=True)
        
        for i, question in enumerate(st.session_state.current_questions, 1):
            st.markdown(f"""
            <div class="question-card">
                <h4>📝 Question {i}</h4>
                <p><strong>Topic:</strong> {question.get('topic', 'Physics')}</p>
                <p><strong>Question:</strong> {question.get('question_text', 'Question text not available')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def display_simple_results(self):
        """Display results in a simple, easy-to-understand format."""
        if not st.session_state.analysis_complete:
            return
        
        st.markdown("---")
        st.header("🏆 Your TOP 3 Most Important Questions")
        
        question_source_text = "sample" if st.session_state.question_source == "sample" else "your uploaded"
        
        st.markdown(f"""
        <div class="success-box">
            <h4>🎉 Analysis Complete!</h4>
            <p>Our AI has analyzed all 10 questions from {question_source_text} question set and selected the <strong>TOP 3</strong> that are most important for your JEE preparation.</p>
        </div>
        """, unsafe_allow_html=True)
        
        ranking = st.session_state.final_ranking
        top_questions = ranking.get('top_3_questions', [])
        
        for question in top_questions:
            rank = question.get('rank', 0)
            
            # Choose emoji and color based on rank
            if rank == 1:
                emoji = "🥇"
                rank_class = "rank-1"
                rank_text = "1st Place"
            elif rank == 2:
                emoji = "🥈"
                rank_class = "rank-2"
                rank_text = "2nd Place"
            elif rank == 3:
                emoji = "🥉"
                rank_class = "rank-3"
                rank_text = "3rd Place"
            else:
                emoji = "🏅"
                rank_class = ""
                rank_text = f"{rank}th Place"
            
            st.markdown(f"""
            <div class="rank-card {rank_class}">
                <h3>{emoji} {rank_text} - Question {question.get('question_id', 'N/A')}</h3>
                <p><strong>Why this made the TOP 3:</strong> {question.get('selection_reasoning', 'This question scored highest in our analysis.')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### The Question:")
                st.markdown(f"*{question.get('question_text', 'Question not available')}*")
            
            with col2:
                st.markdown(f"""
                <div class="metric-box">
                    <h4>🤖 AI Score</h4>
                    <h2>{question.get('final_score', 0):.1f}/10</h2>
                    <p style="margin: 0; font-size: 0.9em; color: #666;">Combined Rating</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Simple score breakdown with better labels
                importance_score = question.get('relevance_contribution', 0)
                difficulty_score = question.get('depth_contribution', 0)
                
                st.markdown("**📊 Score Breakdown:**")
                st.markdown(f"**📈 Exam Frequency:** {importance_score:.1f}/10")
                st.markdown(f"**🧠 Challenge Level:** {difficulty_score:.1f}/10")
            
            st.markdown("---")
        
        # Show simple summary
        st.markdown("### 📊 AI Analysis Summary")
        
        summary_text = ranking.get('overall_analysis', 'Analysis completed successfully.')
        st.markdown(f"""
        <div class="info-box">
            <h4>🔍 What the AI Found:</h4>
            <p>{summary_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        methodology = ranking.get('methodology', 'Questions were evaluated based on exam frequency and challenge level.')
        st.markdown(f"""
        <div class="warning-box">
            <h4>⚙️ How We Picked These Questions:</h4>
            <p>{methodology}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def display_simple_chart(self):
        """Display a simple chart showing all question scores."""
        if not st.session_state.analysis_complete:
            return
        
        st.markdown("---")
        st.header("📈 See How All Questions Scored")
        
        st.markdown("""
        <div class="info-box">
            <h4>📊 Understanding the Chart Below:</h4>
            <p>• <strong>Blue bars</strong> = How likely each question is to appear in JEE exam</p>
            <p>• <strong>Red bars</strong> = How challenging each question is to solve</p>
            <p>• <strong>Taller bars</strong> = Higher scores (better for your study plan)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Prepare data for chart
        chart_data = []
        for analysis in st.session_state.reader_analyses:
            question_id = analysis["original_question"]["id"]
            question_text = analysis["original_question"]["question_text"]
            topic = analysis["original_question"]["topic"]
            
            relevance_score = next((r for r in st.session_state.relevance_scores if r["question_id"] == question_id), None)
            depth_score = next((d for d in st.session_state.depth_scores if d["question_id"] == question_id), None)
            
            if relevance_score and depth_score:
                chart_data.append({
                    "Question": f"Q{question_id}",
                    "Exam Likelihood": relevance_score["overall_relevance_score"],
                    "Challenge Level": depth_score["overall_depth_score"],
                    "Topic": topic
                })
        
        df = pd.DataFrame(chart_data)
        
        # Create simple bar chart with better colors
        fig = px.bar(
            df, 
            x="Question", 
            y=["Exam Likelihood", "Challenge Level"],
            title="📊 Complete Analysis: All Questions Scored",
            labels={"value": "AI Score (0-10)", "variable": "What We Measured"},
            color_discrete_map={"Exam Likelihood": "#3498db", "Challenge Level": "#e74c3c"}
        )
        fig.update_layout(
            height=450, 
            showlegend=True,
            title_font_size=16,
            xaxis_title="Questions",
            yaxis_title="AI Score (0-10)"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("💡 Higher bars mean higher scores")
    
    # Replace the beginning of the run method (around line 970) with this:
    def run(self):
        """Main application flow."""
        # Simple header
        st.markdown('<h1 class="main-title">JEE Physics Helper</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Find the 3 most important physics questions for your JEE exam</p>', unsafe_allow_html=True)
        
        # Simple explanation with steps
        st.markdown("""
        <div class="step-box">
            <h3>How This Works</h3>
            <p><strong>Step 1:</strong> Choose between sample questions or upload your own 10 questions</p>
            <p><strong>Step 2:</strong> Tell us what's more important: <em>Exam Frequency</em> or <em>Challenge Level</em></p>
            <p><strong>Step 3:</strong> AI analyzes all questions and picks the TOP 3 for your study</p>
            <p><strong>Step 4:</strong> Get your personalized study plan!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Question source selection or upload interface
        if st.session_state.question_source == "upload_mode":
            self.upload_questions_interface()
        elif st.session_state.question_source in ["choose", ""] or not st.session_state.current_questions:
            self.question_source_selector()
        else:
            # Show current question info and allow changing
            self.display_current_question_info()
        
        # If we have questions, proceed with analysis interface
        if st.session_state.current_questions:
            # Simple settings with better explanation
            st.markdown("---")
            st.header("Tell Us What's Important to You")
            
            st.markdown("""
            <div class="warning-box">
                <h4>Quick Question:</h4>
                <p>What should we focus on when picking your TOP 3 questions?</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                importance_weight = st.slider(
                    "Should we pick questions that appear frequently in JEE exams?",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.6,
                    step=0.1,
                    help="Move slider RIGHT for questions that often appear in JEE | Move slider LEFT for challenging questions that test deep thinking"
                )
            
            with col2:
                difficulty_weight = 1.0 - importance_weight
                st.markdown("### Challenge Focus")
                st.markdown(f"**{difficulty_weight:.1f}** points")
                st.caption("*This adjusts automatically as you move the slider*")
            
            # Simple explanation of choice
            if importance_weight > 0.7:
                st.markdown("""
                <div class="success-box">
                    <h4>Your Choice: Focus on Exam-Likely Questions</h4>
                    <p>Good choice! We'll pick questions that frequently appear in JEE exams. This helps you prepare for what you're most likely to see.</p>
                </div>
                """, unsafe_allow_html=True)
            elif importance_weight < 0.4:
                st.markdown("""
                <div class="success-box">
                    <h4>Your Choice: Focus on Challenging Questions</h4>
                    <p>Great approach! We'll pick the most challenging questions that really test your understanding. This helps build strong problem-solving skills.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="success-box">
                    <h4>Your Choice: Balanced Approach</h4>
                    <p>Perfect balance! We'll pick questions that are both likely to appear in exams AND challenging enough to strengthen your concepts.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Big analysis button
            st.markdown("---")
            st.header("Ready to Find Your TOP 3 Questions?")
            
            st.markdown("""
            <div class="info-box">
                <h4>What to Expect:</h4>
                <p>• Click the button below to start</p>
                <p>• AI will take <strong>1-2 minutes</strong> to analyze all questions</p>
                <p>• You'll see live updates as the AI works</p>
                <p>• You'll get your TOP 3 questions with explanations</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Start AI Analysis", type="primary", use_container_width=True):
                self.run_analysis(importance_weight, difficulty_weight)
            
            # Show questions
            self.display_questions()
            
            # Show results
            if st.session_state.analysis_complete:
                self.display_simple_results()
                self.display_simple_chart()
                
                # Simple save and try again options
                st.markdown("---")
                st.header("📋 What's Next?")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 💾 Save Your Results")
                    if st.button("📥 Download My TOP 3", use_container_width=True):
                        results = {
                            "top_3_questions": st.session_state.final_ranking.get('top_3_questions', []),
                            "analysis_summary": st.session_state.final_ranking.get('overall_analysis', ''),
                            "methodology": st.session_state.final_ranking.get('methodology', ''),
                            "question_source": st.session_state.question_source,
                            "settings_used": {
                                "exam_focus": importance_weight,
                                "challenge_focus": difficulty_weight
                            }
                        }
                        
                        st.download_button(
                            label="💾 Download Report",
                            data=json.dumps(results, indent=2),
                            file_name=f"my_jee_top3_questions.json",
                            mime="application/json"
                        )
                
                with col2:
                    st.markdown("#### 🔄 Try Different Settings")
                    if st.button("🔁 Analyze Again", use_container_width=True):
                        st.session_state.analysis_complete = False
                        st.session_state.reader_analyses = []
                        st.session_state.relevance_scores = []
                        st.session_state.depth_scores = []
                        st.session_state.final_ranking = {}
                        st.rerun()

def main():
    """Main entry point."""
    app = SimpleJEEAnalyzer()
    app.run()

if __name__ == "__main__":
    main()
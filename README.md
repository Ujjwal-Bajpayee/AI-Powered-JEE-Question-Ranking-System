# AI-Powered JEE Question Ranking System

A sophisticated multi-agent AI system that intelligently ranks JEE physics questions to help students focus on the most important questions for exam preparation.

## 🎯 Overview

This system employs four specialized AI agents to analyze and rank JEE questions:

- **Reader Agent**: Analyzes questions and extracts topic information, complexity metrics, and educational metadata
- **Relevance Agent**: Evaluates exam frequency, conceptual importance, and JEE syllabus alignment
- **Depth Agent**: Assesses cognitive complexity, problem-solving requirements, and learning value
- **Judge Agent**: Synthesizes all inputs to produce final TOP 3 rankings with detailed explanations

## 🌟 Key Features

- **🤖 Multi-Agent AI System**: Four specialized agents collaborate for comprehensive question analysis
- **📤 Custom Question Upload**: Students can upload their own 10 JEE physics questions in JSON format
- **📖 Pre-loaded Sample Questions**: 10 carefully curated JEE physics questions covering all major topics
- **⚖️ Configurable Scoring**: Balance between exam frequency and challenge level based on study goals
- **🎨 User-Friendly Interface**: Clean, professional Streamlit interface with soft colors and intuitive design
- **📊 Visual Analytics**: Interactive charts showing question scores and analysis breakdown
- **💾 Export Results**: Download TOP 3 rankings and analysis as JSON files
- **⚡ Optimized Performance**: Fast AI models with progress tracking and error handling

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Reader Agent  │───▶│ Relevance Agent │───▶│   Depth Agent   │
│                 │    │                 │    │                 │
│ • Topic parsing │    │ • Exam frequency│    │ • Cognitive     │
│ • Bloom levels  │    │ • Syllabus      │    │   complexity    │
│ • Question type │    │   alignment     │    │ • Problem-      │
│ • Complexity    │    │ • Conceptual    │    │   solving depth │
│   assessment    │    │   importance    │    │ • Learning value│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                      │
                                ▼                      ▼
                       ┌─────────────────────────────────────┐
                       │           Judge Agent               │
                       │                                     │
                       │ • Synthesizes all agent inputs      │
                       │ • Applies student preferences       │
                       │ • Produces TOP 3 with reasoning     │
                       │ • Provides detailed explanations    │
                       └─────────────────────────────────────┘
```

## 📋 Requirements

- Python 3.8+
- Groq API key
- Required Python packages (see requirements.txt)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd JEE
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

   Get your free Groq API key from: https://console.groq.com/

## 🎮 Usage

### Running the Streamlit Application

```bash
streamlit run streamlit.py
```

This launches a user-friendly web interface where you can:

#### 📚 Choose Your Question Set
- **Sample Questions**: Use 10 pre-loaded JEE physics questions
- **Upload Questions**: Upload your own 10 questions in JSON format

#### ⚙️ Configure Analysis Settings
- **Exam Focus**: Prioritize questions likely to appear in JEE exams
- **Challenge Focus**: Prioritize conceptually challenging questions
- **Balanced Approach**: Equal weight to both factors

#### 🤖 AI Analysis Process
- Real-time progress tracking
- Step-by-step analysis updates
- 1-2 minute analysis time
- Detailed explanations for TOP 3 selections

#### 📊 Results & Insights
- TOP 3 questions with detailed reasoning
- Score breakdowns (Exam Frequency + Challenge Level)
- Visual charts comparing all questions
- Download results as JSON

### Custom Question Upload Format

Upload a JSON file with exactly 10 questions in this format:

```json
[
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
  // ... 8 more questions with IDs 3-10
]
```

### Command Line Usage

```python
from agents.reader_agent import ReaderAgent
from agents.relevance_agent import RelevanceAgent
from agents.depth_agent import DepthAgent
from agents.judge_agent import JudgeAgent
from langchain_groq import ChatGroq
import json

# Initialize LLM and agents
llm = ChatGroq(model="llama3-8b-8192", temperature=0.1, groq_api_key="your_api_key")
reader = ReaderAgent(llm)
relevance = RelevanceAgent(llm)
depth = DepthAgent(llm)
judge = JudgeAgent(llm)

# Load questions
with open('data/sample_questions.json', 'r') as f:
    questions = json.load(f)

# Run analysis pipeline
reader_analyses = reader.analyze_all_questions(questions)
relevance_scores = relevance.score_all_questions(reader_analyses)
depth_scores = depth.score_all_questions(reader_analyses)
final_ranking = judge.rank_questions(
    reader_analyses, relevance_scores, depth_scores,
    relevance_weight=0.6, depth_weight=0.4
)

print(json.dumps(final_ranking, indent=2))
```

## 🎯 How the AI Evaluates Questions

### Relevance Agent Scoring (Exam Frequency)
- **JEE Exam Frequency**: How often similar questions appear in past JEE papers
- **Syllabus Alignment**: Direct coverage of JEE syllabus topics
- **Conceptual Foundation**: Importance for understanding other physics concepts
- **Problem-Solving Skills**: Development of essential JEE problem-solving techniques
- **Topic Priority**: Weightage of the topic in JEE examination pattern

### Depth Agent Scoring (Challenge Level)
- **Conceptual Integration**: Number of physics concepts that must be combined
- **Mathematical Complexity**: Level of mathematical skills and techniques required
- **Multi-Step Reasoning**: Complexity of logical reasoning and problem-solving steps
- **Abstract Understanding**: Requirement for deep conceptual understanding
- **Application Skills**: Ability to apply concepts to novel situations

### Judge Agent Final Decision
- **Weighted Synthesis**: Combines relevance and depth scores based on user preferences
- **Comparative Ranking**: Evaluates questions relative to each other
- **Detailed Reasoning**: Provides specific explanations for each ranking decision
- **Learning Value Assessment**: Considers overall educational benefit for JEE preparation

## 🔧 Advanced Configuration

### Customizing Analysis Weights

```python
# Prioritize exam-likely questions (recommended for final preparation)
final_ranking = judge.rank_questions(
    reader_analyses, relevance_scores, depth_scores,
    relevance_weight=0.8, depth_weight=0.2
)

# Prioritize challenging questions (recommended for concept building)
final_ranking = judge.rank_questions(
    reader_analyses, relevance_scores, depth_scores,
    relevance_weight=0.3, depth_weight=0.7
)

# Balanced approach (recommended for general preparation)
final_ranking = judge.rank_questions(
    reader_analyses, relevance_scores, depth_scores,
    relevance_weight=0.6, depth_weight=0.4
)
```

## 🎨 User Interface Features

### Clean, Professional Design
- **Soft Color Palette**: Easy on the eyes for extended study sessions
- **No Distracting Elements**: Clean interface without icons or animations
- **Responsive Layout**: Works well on desktop and tablet devices
- **Intuitive Navigation**: Simple, step-by-step user flow

### Interactive Elements
- **Progress Tracking**: Real-time updates during AI analysis
- **Visual Charts**: Bar charts comparing question scores
- **Expandable Sections**: Detailed format guides and explanations
- **Download Options**: Export results for offline review

### Error Handling
- **File Validation**: Comprehensive checks for uploaded question files
- **Graceful Degradation**: Fallback mechanisms when AI analysis fails
- **Clear Error Messages**: Helpful guidance when issues occur
- **Robust Recovery**: System continues working even with partial failures

## 🚀 Performance Optimizations

- **Fast AI Models**: Uses Groq's optimized meta-llama/llama-4-scout-17b-16e-instruct model for speed
- **Efficient Processing**: Streamlined analysis pipeline
- **Caching**: Results cached to avoid re-analysis of same questions
- **Timeout Protection**: Prevents hanging on slow API responses
- **Progress Feedback**: Real-time updates keep users informed


## 🔄 System Workflow

1. **Question Selection**: Choose between sample questions or upload custom set
2. **Preference Setting**: Configure balance between exam frequency and challenge level
3. **AI Analysis**: Four agents analyze all questions comprehensively
4. **Ranking Generation**: TOP 3 questions selected with detailed reasoning
5. **Results Review**: Examine scores, explanations, and visual analytics
6. **Export/Retry**: Download results or adjust settings for new analysis

## 📊 Output Format

The system provides comprehensive results including:

```json
{
  "top_3_questions": [
    {
      "rank": 1,
      "question_id": 3,
      "question_text": "Question content...",
      "final_score": 8.5,
      "selection_reasoning": "Detailed explanation of why this question ranked #1...",
      "relevance_contribution": 5.1,
      "depth_contribution": 3.4
    }
  ],
  "overall_analysis": "Summary of AI findings...",
  "methodology": "Explanation of ranking approach...",
  "question_source": "sample" or "uploaded",
  "settings_used": {
    "exam_focus": 0.6,
    "challenge_focus": 0.4
  }
}
```

## 🚨 Error Handling & Reliability

The system includes robust error handling:
- **API Failures**: Automatic fallback to rule-based scoring
- **File Upload Issues**: Clear validation and error messages
- **JSON Parsing Errors**: Graceful handling with helpful feedback
- **Network Timeouts**: Retry logic and timeout protection
- **Invalid Input**: Comprehensive validation with guided corrections







import json
import re
from typing import Dict, List, Any
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReaderAgent:
    """
    Reader Agent: Parses and analyzes JEE questions to extract topic information,
    Bloom's taxonomy level, and complexity metrics.
    """
    
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.name = "Reader Agent"
        
    def analyze_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single question and extract detailed information.
        
        Args:
            question: Dictionary containing question data
            
        Returns:
            Dictionary with analysis results
        """
        try:
            prompt = self._create_analysis_prompt(question["question_text"])
            
            messages = [
                SystemMessage(content="You are a Reader Agent specialized in analyzing JEE physics questions."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            analysis = self._parse_response(response.content)
            
            # Add original question data
            analysis["original_question"] = question
            analysis["agent"] = self.name
            
            logger.info(f"Reader Agent analyzed question {question['id']}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in Reader Agent analysis: {str(e)}")
            return self._fallback_analysis(question)
    
    def analyze_all_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze all questions in the dataset.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            List of analysis results
        """
        analyses = []
        for question in questions:
            analysis = self.analyze_question(question)
            analyses.append(analysis)
        
        return analyses
    
    def _create_analysis_prompt(self, question_text: str) -> str:
        """Create the prompt for question analysis."""
        return f"""
You are a Reader Agent specialized in analyzing JEE (Joint Entrance Examination) physics questions. Your task is to parse and extract detailed information from each question.

For the given question, identify and extract:
1. Main physics topic/concept
2. Sub-topics or related concepts
3. Bloom's taxonomy level (Remember, Understand, Apply, Analyze, Evaluate, Create)
4. Question type (numerical, conceptual, derivation, etc.)
5. Difficulty level (Easy, Medium, Hard)
6. Key physics principles involved

Question: {question_text}

Provide your analysis in the following JSON format:
{{
  "main_topic": "string",
  "sub_topics": ["list", "of", "subtopics"],
  "bloom_level": "string",
  "question_type": "string",
  "difficulty": "string",
  "key_principles": ["list", "of", "principles"],
  "complexity_score": number_1_to_10
}}

Respond with only the JSON, no additional text.
"""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response and extract JSON."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            return self._fallback_json()
    
    def _fallback_analysis(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback analysis if LLM fails."""
        return {
            "main_topic": question.get("topic", "Unknown"),
            "sub_topics": question.get("tags", []),
            "bloom_level": question.get("bloom_level", "Apply"),
            "question_type": "numerical",
            "difficulty": "Medium",
            "key_principles": question.get("tags", []),
            "complexity_score": 5,
            "original_question": question,
            "agent": self.name,
            "note": "Fallback analysis used"
        }
    
    def _fallback_json(self) -> Dict[str, Any]:
        """Provide fallback JSON structure."""
        return {
            "main_topic": "Physics",
            "sub_topics": ["general"],
            "bloom_level": "Apply",
            "question_type": "numerical",
            "difficulty": "Medium",
            "key_principles": ["basic principles"],
            "complexity_score": 5
        }

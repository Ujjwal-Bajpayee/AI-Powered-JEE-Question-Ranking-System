import json
import re
from typing import Dict, List, Any
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import logging

logger = logging.getLogger(__name__)

class RelevanceAgent:
    """
    Relevance Agent: Evaluates questions based on exam utility, conceptual importance,
    and overall relevance for JEE preparation.
    """
    
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.name = "Relevance Agent"
        
    def score_question(self, question_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a question based on relevance criteria.
        
        Args:
            question_analysis: Analysis from Reader Agent
            
        Returns:
            Dictionary with relevance scores and justifications
        """
        try:
            prompt = self._create_scoring_prompt(question_analysis)
            
            messages = [
                SystemMessage(content="You are a Relevance Agent that evaluates the importance and utility of JEE physics questions."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            relevance_data = self._parse_response(response.content)
            
            # Add metadata
            relevance_data["question_id"] = question_analysis["original_question"]["id"]
            relevance_data["agent"] = self.name
            
            logger.info(f"Relevance Agent scored question {question_analysis['original_question']['id']}")
            return relevance_data
            
        except Exception as e:
            logger.error(f"Error in Relevance Agent scoring: {str(e)}")
            return self._fallback_scoring(question_analysis)
    
    def score_all_questions(self, question_analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score all questions for relevance.
        
        Args:
            question_analyses: List of analyses from Reader Agent
            
        Returns:
            List of relevance scores
        """
        relevance_scores = []
        for analysis in question_analyses:
            score = self.score_question(analysis)
            relevance_scores.append(score)
        
        return relevance_scores
    
    def _create_scoring_prompt(self, question_analysis: Dict[str, Any]) -> str:
        """Create the prompt for relevance scoring."""
        question_text = question_analysis["original_question"]["question_text"]
        
        return f"""
You are a Relevance Agent that evaluates the importance and utility of JEE physics questions for exam preparation and conceptual understanding.

Evaluate the following question based on:
1. Frequency of appearance in JEE exams (how often similar questions appear)
2. Conceptual importance (fundamental physics concepts)
3. Application relevance (real-world applications)
4. Foundation building (prerequisite for other topics)
5. Problem-solving skills development

Question Analysis: {json.dumps(question_analysis, indent=2)}
Question Text: {question_text}

Rate each criterion on a scale of 1-10 and provide justification:

{{
  "exam_frequency": {{
    "score": number_1_to_10,
    "justification": "explanation"
  }},
  "conceptual_importance": {{
    "score": number_1_to_10,
    "justification": "explanation"
  }},
  "application_relevance": {{
    "score": number_1_to_10,
    "justification": "explanation"
  }},
  "foundation_building": {{
    "score": number_1_to_10,
    "justification": "explanation"
  }},
  "skill_development": {{
    "score": number_1_to_10,
    "justification": "explanation"
  }},
  "overall_relevance_score": number_1_to_10,
  "summary": "brief explanation of overall relevance"
}}

Respond with only the JSON, no additional text.
"""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response and extract JSON."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            logger.error(f"Error parsing relevance response: {str(e)}")
            return self._fallback_json()
    
    def _fallback_scoring(self, question_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback scoring if LLM fails."""
        base_score = 6  # Default medium relevance
        
        # Adjust based on known factors
        if question_analysis.get("bloom_level") in ["Analyze", "Create"]:
            base_score += 1
        if question_analysis.get("difficulty") == "Hard":
            base_score += 1
        if len(question_analysis.get("key_principles", [])) > 2:
            base_score += 1
            
        base_score = min(base_score, 10)
        
        return {
            "exam_frequency": {"score": base_score, "justification": "Estimated based on topic"},
            "conceptual_importance": {"score": base_score, "justification": "Estimated based on complexity"},
            "application_relevance": {"score": base_score - 1, "justification": "Estimated"},
            "foundation_building": {"score": base_score, "justification": "Estimated based on principles"},
            "skill_development": {"score": base_score, "justification": "Estimated based on bloom level"},
            "overall_relevance_score": base_score,
            "summary": "Fallback scoring used due to LLM error",
            "question_id": question_analysis["original_question"]["id"],
            "agent": self.name,
            "note": "Fallback scoring used"
        }
    
    def _fallback_json(self) -> Dict[str, Any]:
        """Provide fallback JSON structure."""
        return {
            "exam_frequency": {"score": 6, "justification": "Default estimation"},
            "conceptual_importance": {"score": 6, "justification": "Default estimation"},
            "application_relevance": {"score": 5, "justification": "Default estimation"},
            "foundation_building": {"score": 6, "justification": "Default estimation"},
            "skill_development": {"score": 6, "justification": "Default estimation"},
            "overall_relevance_score": 6,
            "summary": "Default relevance assessment"
        }

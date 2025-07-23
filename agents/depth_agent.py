import json
import re
from typing import Dict, List, Any
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import logging

logger = logging.getLogger(__name__)

class DepthAgent:
    """
    Depth Agent: Evaluates questions based on cognitive depth, reasoning complexity,
    and the sophistication of problem-solving required.
    """
    
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.name = "Depth Agent"
        
    def score_question(self, question_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a question based on depth and complexity criteria.
        
        Args:
            question_analysis: Analysis from Reader Agent
            
        Returns:
            Dictionary with depth scores and explanations
        """
        try:
            prompt = self._create_scoring_prompt(question_analysis)
            
            messages = [
                SystemMessage(content="You are a Depth Agent that evaluates the cognitive depth and reasoning complexity of JEE physics questions."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            depth_data = self._parse_response(response.content)
            
            # Add metadata
            depth_data["question_id"] = question_analysis["original_question"]["id"]
            depth_data["agent"] = self.name
            
            logger.info(f"Depth Agent scored question {question_analysis['original_question']['id']}")
            return depth_data
            
        except Exception as e:
            logger.error(f"Error in Depth Agent scoring: {str(e)}")
            return self._fallback_scoring(question_analysis)
    
    def score_all_questions(self, question_analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score all questions for depth and complexity.
        
        Args:
            question_analyses: List of analyses from Reader Agent
            
        Returns:
            List of depth scores
        """
        depth_scores = []
        for analysis in question_analyses:
            score = self.score_question(analysis)
            depth_scores.append(score)
        
        return depth_scores
    
    def _create_scoring_prompt(self, question_analysis: Dict[str, Any]) -> str:
        """Create the prompt for depth scoring."""
        question_text = question_analysis["original_question"]["question_text"]
        
        return f"""
You are a Depth Agent that evaluates the cognitive depth and reasoning complexity required for JEE physics questions.

Analyze the following question for:
1. Number of concepts that need to be integrated
2. Mathematical complexity required
3. Multi-step reasoning requirement
4. Abstract thinking level
5. Problem-solving strategy sophistication

Question Analysis: {json.dumps(question_analysis, indent=2)}
Question Text: {question_text}

Evaluate each aspect on a scale of 1-10:

{{
  "concept_integration": {{
    "score": number_1_to_10,
    "explanation": "how many concepts need to be combined"
  }},
  "mathematical_complexity": {{
    "score": number_1_to_10,
    "explanation": "level of mathematical skills required"
  }},
  "reasoning_steps": {{
    "score": number_1_to_10,
    "explanation": "number and complexity of logical steps"
  }},
  "abstract_thinking": {{
    "score": number_1_to_10,
    "explanation": "level of abstract conceptual understanding needed"
  }},
  "strategy_sophistication": {{
    "score": number_1_to_10,
    "explanation": "sophistication of problem-solving approach"
  }},
  "overall_depth_score": number_1_to_10,
  "depth_summary": "explanation of cognitive demands"
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
            logger.error(f"Error parsing depth response: {str(e)}")
            return self._fallback_json()
    
    def _fallback_scoring(self, question_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback scoring if LLM fails."""
        base_score = 5  # Default medium depth
        
        # Adjust based on known factors
        complexity_score = question_analysis.get("complexity_score", 5)
        base_score = max(base_score, complexity_score)
        
        if question_analysis.get("bloom_level") in ["Analyze", "Evaluate", "Create"]:
            base_score += 2
        if question_analysis.get("difficulty") == "Hard":
            base_score += 1
        if len(question_analysis.get("key_principles", [])) > 3:
            base_score += 1
            
        base_score = min(base_score, 10)
        
        return {
            "concept_integration": {"score": base_score, "explanation": "Estimated based on key principles"},
            "mathematical_complexity": {"score": base_score - 1, "explanation": "Estimated based on question type"},
            "reasoning_steps": {"score": base_score, "explanation": "Estimated based on complexity"},
            "abstract_thinking": {"score": base_score, "explanation": "Estimated based on bloom level"},
            "strategy_sophistication": {"score": base_score - 1, "explanation": "Estimated based on difficulty"},
            "overall_depth_score": base_score,
            "depth_summary": "Fallback scoring used due to LLM error",
            "question_id": question_analysis["original_question"]["id"],
            "agent": self.name,
            "note": "Fallback scoring used"
        }
    
    def _fallback_json(self) -> Dict[str, Any]:
        """Provide fallback JSON structure."""
        return {
            "concept_integration": {"score": 5, "explanation": "Default estimation"},
            "mathematical_complexity": {"score": 5, "explanation": "Default estimation"},
            "reasoning_steps": {"score": 5, "explanation": "Default estimation"},
            "abstract_thinking": {"score": 5, "explanation": "Default estimation"},
            "strategy_sophistication": {"score": 5, "explanation": "Default estimation"},
            "overall_depth_score": 5,
            "depth_summary": "Default depth assessment"
        }

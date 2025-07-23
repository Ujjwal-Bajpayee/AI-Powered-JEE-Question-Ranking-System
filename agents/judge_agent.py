import json
import re
from typing import Dict, List, Any, Tuple
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import logging

logger = logging.getLogger(__name__)

class JudgeAgent:
    """
    Judge Agent: Makes final decisions on question ranking by synthesizing inputs
    from all other agents and applying weighting factors.
    """
    
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.name = "Judge Agent"
        
    def rank_questions(self, 
                      reader_analyses: List[Dict[str, Any]], 
                      relevance_scores: List[Dict[str, Any]], 
                      depth_scores: List[Dict[str, Any]],
                      relevance_weight: float = 0.6,
                      depth_weight: float = 0.4) -> Dict[str, Any]:
        """
        Make final ranking decisions based on all agent inputs.
        
        Args:
            reader_analyses: Output from Reader Agent
            relevance_scores: Output from Relevance Agent
            depth_scores: Output from Depth Agent
            relevance_weight: Weight for relevance in final score (0-1)
            depth_weight: Weight for depth in final score (0-1)
            
        Returns:
            Dictionary with top 3 ranked questions and explanations
        """
        try:
            # Calculate composite scores
            composite_scores = self._calculate_composite_scores(
                reader_analyses, relevance_scores, depth_scores, 
                relevance_weight, depth_weight
            )
            
            # Check if we should use fallback due to potential token limits
            prompt = self._create_ranking_prompt(
                reader_analyses, relevance_scores, depth_scores,
                relevance_weight, depth_weight, composite_scores
            )
            
            # Estimate token count (rough approximation)
            estimated_tokens = len(prompt.split()) * 1.3  # Conservative estimate
            
            if estimated_tokens > 5000:  # Stay well below 6000 limit
                logger.warning(f"Prompt too large ({estimated_tokens} estimated tokens), using fallback ranking")
                return self._fallback_ranking(composite_scores, reader_analyses)
            
            messages = [
                SystemMessage(content="You are a Judge Agent for ranking JEE physics questions."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            try:
                ranking_data = self._parse_response(response.content)
            except Exception as parse_error:
                logger.warning(f"Failed to parse LLM response, using fallback ranking: {str(parse_error)}")
                return self._fallback_ranking(composite_scores, reader_analyses)
            
            # Add calculation details
            ranking_data["calculation_details"] = {
                "relevance_weight": relevance_weight,
                "depth_weight": depth_weight,
                "composite_scores": composite_scores,
                "agent": self.name
            }
            
            logger.info("Judge Agent completed final ranking")
            return ranking_data
            
        except Exception as e:
            logger.error(f"Error in Judge Agent ranking: {str(e)}")
            return self._fallback_ranking(composite_scores, reader_analyses)
    
    def _calculate_composite_scores(self, 
                                   reader_analyses: List[Dict[str, Any]], 
                                   relevance_scores: List[Dict[str, Any]], 
                                   depth_scores: List[Dict[str, Any]],
                                   relevance_weight: float,
                                   depth_weight: float) -> List[Dict[str, Any]]:
        """Calculate composite scores for all questions."""
        composite_scores = []
        
        for i, reader_analysis in enumerate(reader_analyses):
            question_id = reader_analysis["original_question"]["id"]
            
            # Find corresponding scores
            relevance_score = next((r for r in relevance_scores if r["question_id"] == question_id), None)
            depth_score = next((d for d in depth_scores if d["question_id"] == question_id), None)
            
            if relevance_score and depth_score:
                relevance_val = relevance_score["overall_relevance_score"]
                depth_val = depth_score["overall_depth_score"]
                
                composite_score = (relevance_val * relevance_weight) + (depth_val * depth_weight)
                
                composite_scores.append({
                    "question_id": question_id,
                    "question_text": reader_analysis["original_question"]["question_text"],
                    "relevance_score": relevance_val,
                    "depth_score": depth_val,
                    "composite_score": composite_score,
                    "relevance_contribution": relevance_val * relevance_weight,
                    "depth_contribution": depth_val * depth_weight
                })
        
        # Sort by composite score
        composite_scores.sort(key=lambda x: x["composite_score"], reverse=True)
        return composite_scores
    
    def _create_ranking_prompt(self, 
                              reader_analyses: List[Dict[str, Any]], 
                              relevance_scores: List[Dict[str, Any]], 
                              depth_scores: List[Dict[str, Any]],
                              relevance_weight: float,
                              depth_weight: float,
                              composite_scores: List[Dict[str, Any]]) -> str:
        """Create a concise prompt for final ranking to avoid token limits."""
        
        # Get top 5 candidates only to reduce data size
        top_candidates = composite_scores[:5]
        
        # Create simplified data for prompt - only essential information
        simplified_data = []
        for candidate in top_candidates:
            question_id = candidate["question_id"]
            
            # Get only essential data from each agent
            reader_data = next((r for r in reader_analyses if r["original_question"]["id"] == question_id), {})
            relevance_data = next((r for r in relevance_scores if r["question_id"] == question_id), {})
            depth_data = next((d for d in depth_scores if d["question_id"] == question_id), {})
            
            simplified_data.append({
                "question_id": question_id,
                "question_text": candidate["question_text"][:100] + "...",  # Truncate long questions
                "topic": reader_data.get("topic", "Unknown"),
                "relevance_score": candidate["relevance_score"],
                "depth_score": candidate["depth_score"], 
                "composite_score": candidate["composite_score"],
                "key_concepts": reader_data.get("key_concepts", [])[:3],  # Only top 3 concepts
                "relevance_reasons": relevance_data.get("reasoning", "")[:150] + "...",  # Truncate
                "depth_reasons": depth_data.get("reasoning", "")[:150] + "..."  # Truncate
            })
        
        return f"""Judge Agent: Analyze and rank TOP 3 JEE physics questions with detailed reasoning.

Your task: Select the 3 most important questions for JEE exam preparation.

Analysis Weights: Relevance {relevance_weight*100}% | Depth {depth_weight*100}%

Candidate Questions:
{json.dumps(simplified_data, indent=2)}

Instructions:
1. Evaluate each question's importance for JEE Physics exam
2. Consider relevance to JEE syllabus, depth of concepts, and exam frequency
3. Provide detailed reasoning for WHY each question earned its rank
4. Explain how the scores influenced your decision

Return JSON with detailed explanations:
{{"top_3_questions": [{{"rank": 1, "question_id": X, "question_text": "full text", "final_score": X.X, "relevance_contribution": X.X, "depth_contribution": X.X, "selection_reasoning": "Detailed explanation: Why this question is #1 - mention specific concepts, relevance to JEE pattern, difficulty appropriateness, and learning value (3-4 sentences)"}}, {{"rank": 2, "question_id": Y, "selection_reasoning": "Detailed explanation for rank #2 (3-4 sentences)"}}, {{"rank": 3, "question_id": Z, "selection_reasoning": "Detailed explanation for rank #3 (3-4 sentences)"}}], "overall_analysis": "Summary of ranking methodology and key factors", "methodology": "How weights and scores determined final ranking"}}
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
            logger.error(f"Error parsing judge response: {str(e)}")
            # Instead of returning default JSON, we need to return None and let the calling function handle it
            raise e
    
    def _fallback_ranking(self, composite_scores: List[Dict[str, Any]], reader_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Provide fallback ranking with detailed explanations if LLM fails."""
        top_3 = composite_scores[:3]
        
        result = {
            "top_3_questions": [],
            "overall_analysis": "Ranking based on composite scores calculated from relevance and depth analysis",
            "methodology": "Weighted average combining relevance and depth scores with detailed reasoning"
        }
        
        rank_descriptions = [
            "This question achieved the highest composite score, indicating excellent balance of JEE relevance and conceptual depth. It represents core physics concepts frequently tested in JEE exams.",
            "This question ranked second due to strong performance in both relevance and depth metrics. It covers important JEE topics with appropriate difficulty level for effective preparation.",
            "This question earned third place with solid scores across evaluation criteria. It provides valuable practice for JEE physics concepts and enhances understanding of key principles."
        ]
        
        for i, question in enumerate(top_3):
            # Get topic information from reader analysis
            reader_data = next((r for r in reader_analyses if r["original_question"]["id"] == question["question_id"]), {})
            topic = reader_data.get("topic", "Physics")
            
            detailed_reasoning = f"{rank_descriptions[i]} The question focuses on {topic} with a relevance score of {question['relevance_score']:.1f}/10 and depth score of {question['depth_score']:.1f}/10, resulting in a composite score of {question['composite_score']:.2f}."
            
            result["top_3_questions"].append({
                "rank": i + 1,
                "question_id": question["question_id"],
                "question_text": question["question_text"],
                "final_score": question["composite_score"],
                "relevance_contribution": question["relevance_contribution"],
                "depth_contribution": question["depth_contribution"],
                "selection_reasoning": detailed_reasoning
            })
        
        return result

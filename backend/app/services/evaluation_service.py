from typing import Dict, Any, Optional
from textblob import TextBlob
import re


class EvaluationService:
    """Service for evaluating LLM responses"""
    
    @staticmethod
    def evaluate_sentiment(text: str) -> Dict[str, Any]:
        """
        Evaluate sentiment of the text
        Returns score from -1 (negative) to 1 (positive)
        """
        if not text:
            return {"score": 0.0, "details": {"error": "Empty text"}}
        
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment
            
            return {
                "score": sentiment.polarity,
                "details": {
                    "polarity": sentiment.polarity,
                    "subjectivity": sentiment.subjectivity,
                    "classification": (
                        "positive" if sentiment.polarity > 0.1 else
                        "negative" if sentiment.polarity < -0.1 else
                        "neutral"
                    )
                }
            }
        except Exception as e:
            return {"score": 0.0, "details": {"error": str(e)}}
    
    @staticmethod
    def evaluate_clarity(text: str) -> Dict[str, Any]:
        """
        Evaluate clarity of the text based on readability metrics
        Returns score from 0 to 1 (higher is clearer)
        """
        if not text:
            return {"score": 0.0, "details": {"error": "Empty text"}}
        
        try:
            # Calculate average sentence length
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return {"score": 0.0, "details": {"error": "No sentences found"}}
            
            words = text.split()
            avg_sentence_length = len(words) / len(sentences)
            
            # Calculate average word length
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            # Simple clarity score (inverted complexity)
            # Shorter sentences and shorter words = higher clarity
            # Normalize to 0-1 scale
            sentence_score = max(0, min(1, 1 - (avg_sentence_length - 10) / 30))
            word_score = max(0, min(1, 1 - (avg_word_length - 4) / 6))
            clarity_score = (sentence_score + word_score) / 2
            
            return {
                "score": round(clarity_score, 2),
                "details": {
                    "avg_sentence_length": round(avg_sentence_length, 2),
                    "avg_word_length": round(avg_word_length, 2),
                    "sentence_count": len(sentences),
                    "word_count": len(words)
                }
            }
        except Exception as e:
            return {"score": 0.0, "details": {"error": str(e)}}
    
    @staticmethod
    def evaluate_accuracy(text: str, expected_keywords: Optional[list] = None) -> Dict[str, Any]:
        """
        Evaluate accuracy based on presence of expected keywords/topics
        This is a simple heuristic-based evaluation
        Returns score from 0 to 1
        """
        if not text:
            return {"score": 0.0, "details": {"error": "Empty text"}}
        
        try:
            text_lower = text.lower()
            
            # If no expected keywords provided, use basic heuristics
            if not expected_keywords:
                # Check for common indicators of accurate responses
                positive_indicators = [
                    "based on", "according to", "research shows", 
                    "studies indicate", "evidence suggests", "data shows"
                ]
                negative_indicators = [
                    "i don't know", "not sure", "unclear", 
                    "cannot determine", "insufficient information"
                ]
                
                positive_count = sum(1 for indicator in positive_indicators if indicator in text_lower)
                negative_count = sum(1 for indicator in negative_indicators if indicator in text_lower)
                
                # Simple scoring
                if negative_count > 0:
                    score = 0.3
                elif positive_count > 0:
                    score = 0.8
                else:
                    score = 0.5
                
                return {
                    "score": score,
                    "details": {
                        "positive_indicators": positive_count,
                        "negative_indicators": negative_count,
                        "note": "Heuristic-based evaluation without ground truth"
                    }
                }
            
            # If keywords provided, check presence
            found_keywords = [kw for kw in expected_keywords if kw.lower() in text_lower]
            score = len(found_keywords) / len(expected_keywords) if expected_keywords else 0.5
            
            return {
                "score": round(score, 2),
                "details": {
                    "expected_keywords": expected_keywords,
                    "found_keywords": found_keywords,
                    "coverage": f"{len(found_keywords)}/{len(expected_keywords)}"
                }
            }
        except Exception as e:
            return {"score": 0.0, "details": {"error": str(e)}}
    
    def evaluate(self, text: str, evaluation_type: str, **kwargs) -> Dict[str, Any]:
        """
        Perform evaluation based on type
        """
        evaluators = {
            "sentiment": self.evaluate_sentiment,
            "clarity": self.evaluate_clarity,
            "accuracy": self.evaluate_accuracy
        }
        
        evaluator = evaluators.get(evaluation_type)
        if not evaluator:
            raise ValueError(f"Unsupported evaluation type: {evaluation_type}")
        
        if evaluation_type == "accuracy":
            return evaluator(text, kwargs.get("expected_keywords"))
        else:
            return evaluator(text)

import pytest
from app.services.evaluation_service import EvaluationService


def test_sentiment_evaluation_positive():
    service = EvaluationService()
    result = service.evaluate_sentiment("This is a great and wonderful product!")
    
    assert result["score"] > 0
    assert result["details"]["classification"] == "positive"


def test_sentiment_evaluation_negative():
    service = EvaluationService()
    result = service.evaluate_sentiment("This is terrible and awful.")
    
    assert result["score"] < 0
    assert result["details"]["classification"] == "negative"


def test_sentiment_evaluation_neutral():
    service = EvaluationService()
    result = service.evaluate_sentiment("This is a product.")
    
    assert -0.1 <= result["score"] <= 0.1
    assert result["details"]["classification"] == "neutral"


def test_clarity_evaluation():
    service = EvaluationService()
    text = "This is a clear sentence. It is easy to understand."
    result = service.evaluate_clarity(text)
    
    assert 0 <= result["score"] <= 1
    assert "avg_sentence_length" in result["details"]
    assert "avg_word_length" in result["details"]


def test_clarity_evaluation_empty():
    service = EvaluationService()
    result = service.evaluate_clarity("")
    
    assert result["score"] == 0.0
    assert "error" in result["details"]


def test_accuracy_evaluation_with_keywords():
    service = EvaluationService()
    text = "Python is a programming language used for data science."
    keywords = ["python", "programming", "data"]
    result = service.evaluate_accuracy(text, keywords)
    
    assert result["score"] == 1.0
    assert len(result["details"]["found_keywords"]) == 3


def test_accuracy_evaluation_without_keywords():
    service = EvaluationService()
    text = "Based on research, this approach is effective."
    result = service.evaluate_accuracy(text)
    
    assert 0 <= result["score"] <= 1
    assert "positive_indicators" in result["details"]


def test_evaluate_method():
    service = EvaluationService()
    text = "This is a test message."
    
    # Test sentiment
    result = service.evaluate(text, "sentiment")
    assert "score" in result
    
    # Test clarity
    result = service.evaluate(text, "clarity")
    assert "score" in result
    
    # Test accuracy
    result = service.evaluate(text, "accuracy")
    assert "score" in result


def test_evaluate_invalid_type():
    service = EvaluationService()
    
    with pytest.raises(ValueError):
        service.evaluate("test", "invalid_type")

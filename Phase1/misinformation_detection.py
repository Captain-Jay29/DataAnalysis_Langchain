from langchain_community.chat_models import ChatOpenAI
from typing import Dict, Any, List
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MisinformationDetector:
    """
    A class to detect misinformation in social media posts using an LLM model.
    """

    # Define threshold parameters
    CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence to accept LLM's decision
    MISINFO_THRESHOLD = 0.5  # Minimum threshold to consider something as misinformation

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.3):
        """Initialize the ChatOpenAI model."""
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)

    def generate_prompt(self, text: str) -> str:
        """Generate a structured prompt for misinformation detection."""
        return f"""
        Analyze the following social media post and determine if it contains misinformation. 
        Consider factual accuracy, logical consistency, and cross-check with known facts. 
        Provide a boolean flag (True/False), a confidence score (0-1), and a short reason.
        
        Post: {text}
        
        Response format: JSON with keys: is_misinformation (bool), confidence (float), reason (str).
        """

    def parse_response(self, response: Any) -> Dict[str, Any]:
        """Extract and parse JSON from LLM response."""
        if hasattr(response, "content"):
            response_text = response.content.strip()
        else:
            logging.error("Unexpected response format: %s", response)
            return {"error": "Unexpected response format"}

        # Remove JSON formatting markers if they exist
        response_text = response_text.strip("```json").strip("```")

        try:
            parsed_response = json.loads(response_text)
            if not all(k in parsed_response for k in ["is_misinformation", "confidence", "reason"]):
                raise ValueError("Missing expected keys in response")
            return parsed_response
        except (json.JSONDecodeError, ValueError) as e:
            logging.error("Failed to parse LLM response: %s", e)
            return {"error": "Failed to parse response"}

    def detect_misinformation(self, text: str) -> Dict[str, Any]:
        """
        Determines if the given text contains misinformation.
        Uses thresholding to filter uncertain results.
        """
        prompt = self.generate_prompt(text)
        response = self.llm.invoke(prompt)
        result = self.parse_response(response)

        if "error" in result:
            return result  # Return error if parsing failed

        # Apply threshold filtering
        is_misinfo = result["is_misinformation"]
        confidence = result["confidence"]

        if confidence < self.CONFIDENCE_THRESHOLD:
            return {"warning": "Low confidence in response", **result}

        if is_misinfo and confidence >= self.MISINFO_THRESHOLD:
            return {"flagged": True, **result}
        else:
            return {"flagged": False, **result}

    def detect_misinformation_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Batch processes multiple texts for misinformation detection.
        """
        return [self.detect_misinformation(text) for text in texts]

# Example Usage
if __name__ == "__main__":
    detector = MisinformationDetector()
    
    test_texts = [
        "COVID-19 vaccines contain microchips for tracking.",
        "NASA just confirmed the moon is made of cheese!"
    ]
    
    results = detector.detect_misinformation_batch(test_texts)
    for text, result in zip(test_texts, results):
        print(f"Post: {text}\nDetection Result: {result}\n")

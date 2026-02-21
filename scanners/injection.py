from transformers import pipeline

class InjectionScanner:
  def __init__(self, model_path="./model/final"):
    self.classifier = pipeline(
    "text-classification",
    model=model_path,
    tokenizer=model_path
    )

  def scan(self, text: str) -> dict:
    result = self.classifier(text)[0]

    is_injection = result["label"] == "LABEL_1"
    return {
      "flagged": is_injection,
      "confidence": round(result["score"], 4),
      "reason": "Prompt injection attempt detected"  if is_injection else None
    }

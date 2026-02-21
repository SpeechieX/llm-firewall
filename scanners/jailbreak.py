from transformers import pipeline

class JailbreakScanner:
  def __init__(self):
    self.classifier = pipeline(
      "text-classification",
      model="jackhhao/jailbreak-classifier"
    )
  def scan(self, text: str) -> dict:
    result = self.classifier(text)[0]
    is_jailbreak = result["label"] == "JAILBREAK"
    return {
      "flagged": is_jailbreak,
      "confidence": round(result["score"], 4),
      "reason": "Jailbreak attempt detected" if is_jailbreak else None
    }

from detoxify import Detoxify

class ToxicScanner:
  def __init__(self):
   self.model = Detoxify("original")
   self.threshold = 0.7

  def scan(self, text: str) -> dict:
    scores = self.model.predict(text)
    violations = {
      k: round(float(v), 4)
      for k, v in scores.items()
      if float(v) >= self.threshold
    }

    flagged = len(violations) > 0
    return {
      "flagged": flagged,
      "scores": {k: round(float(v), 4) for k, v in scores.items()},
      "violations": violations,
      "reason": f"Toxic content detected: {', '.join(violations.keys())}" if flagged else None
    }


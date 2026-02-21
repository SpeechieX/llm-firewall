from presidio_analyzer import AnalyzerEngine

class PIIScanner:
  def __init__(self):
    self.analyzer = AnalyzerEngine()
    self.entities = [
      "PERSON", "EMAIL ADDRESS", "PHONE_NUMBER",
      "CREDIT_CARD", "US_SSN", "IP_ADDRESS",
      "LOCATION", "DATE_TIME", "NRP"
    ]
  def scan(self, text: str) -> dict:
    results = self.analyzer.analyze(
      text=text,
      entities=self.entities,
      language="en"
    )
    flagged = len(results) > 0
    findings = [
      {
        "entity_type": r.entity_type,
        "score": round(r.score, 4),
        "start": r.start,
        "end": r.end,
        "value": text[r.start:r.end]
      }
      for r in results
    ]
    return {
      "flagged": flagged,
      "findings": findings,
      "reason": f"PII detected{', '.join(set(r.entity_type for r in results))}" if flagged else None
    }


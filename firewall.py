import anthropic
from scanners.injection import InjectionScanner
from scanners.pii import PIIScanner
from scanners.jailbreak import JailbreakScanner
from scanners.toxic import ToxicScanner

class LLMFirewall:
  def __init__(self):
    print("Loading scanners...")
    self.injection_scanner = InjectionScanner()
    self.pii_scanner = PIIScanner()
    self.jailbreak_scanner = JailbreakScanner()
    self.toxic_scanner = ToxicScanner()
    self.client = anthropic.Anthropic()
    print("Firewall Active.")

  def scan_input(self, text: str) -> dict:
    results = {
      "injection": self.injection_scanner.scan(text),
      "pii": self.pii_scanner.scan(text),
      "jailbreak": self.jailbreak_scanner.scan(text),
      "toxic": self.toxic_scanner.scan(text),
    }
    flagged = any(r["flagged"] for r in results.values())
    reasons = [r["reason"] for r in results.values() if r.get("reason")]
    return {"flagged": flagged, "reasons": reasons, "details": results}

  def scan_output(self, text: str) -> dict:
    results = {
      "pii_leakage": self.pii_scanner(text),
      "toxic": self.toxic_scanner.scan(text),
    }
    flagged = any(r["flagged"] for r in results.values())
    reasons = [r["reason"] for r in results.values() if r.get("reason")]
    return {"flagged": flagged, "reasons": reasons, "details": results}

  def process(self, user_input: str) -> dict:
    input_scan = self.scan_input(user_input)
    if input_scan["flagged"]:
      return {
        "blocked": True,
        "stage": "input",
        "reasons": input_scan["reasons"],
        "input_scan": input_scan,
        "output_scan": None,
        "response": None
      }

    message = self.client.messages.create(
      model="claude-opus-4-5-2-251101",
      max_tokens=1024,
      messages=[{"role": "user", "content": user_input}]
    )
    llm_response = message.content[0].text

    output_scan = self.scan_output(llm_response)
    if output_scan["flagged"]:
      return {
        "blocked": True,
        "stage": "output",
        "reasons": output_scan["reasons"],
        "input_scan": input_scan,
        "output_scan": output_scan,
        "response": None
      }

    return {
      "blocked": False,
      "stage": None,
      "reasons": [],
      "input_scan": input_scan,
      "output_scan": output_scan,
      "response": llm_response
    }


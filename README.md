# LLM Firewall / Input-Output Scanner

## Description

A production-grade security middleware layer that wraps Large Language Models (LLMs) to provide comprehensive threat detection on both user inputs and model outputs. Unlike single-purpose classifiers, this firewall acts as a **bidirectional security gateway** — it screens prompts before they reach the LLM and validates responses before they reach the user.

The system implements defense-in-depth with four distinct scanner engines on the input side and four on the output side, creating an 8-layer security perimeter around Claude (or any LLM). Each scanner operates independently, and any single flagged threat blocks the request, ensuring that attackers must bypass all layers simultaneously.

## (NOTE: Anthropic is used as an example in this project, but you can use any llm api key and its respective dependencies.)

## Use Cases

- **Enterprise LLM Deployments** — wrap customer-facing chatbots, internal AI assistants, or RAG systems with a security layer that prevents data leakage and policy violations
- **API Gateway for LLM Services** — protect third-party LLM integrations by screening all traffic bidirectionally
- **Compliance and Governance** — enforce organizational policies on LLM usage (no PII processing, content moderation, prohibited topics)
- **Security Research** — analyze attack patterns by logging which scanners trigger on real-world traffic
- **Red Team Defense** — harden AI applications against adversarial users before deploying to production

---

## Architecture

```
User Input
    ↓
┌─────────────────────────────────────┐
│        INPUT FIREWALL               │
├─────────────────────────────────────┤
│ • Prompt Injection Scanner          │  ← Reused from Project 1
│ • PII Detector                      │  ← Microsoft Presidio
│ • Jailbreak Detector                │  ← Fine-tuned classifier
│ • Toxic Content Filter              │  ← Detoxify model
└─────────────────────────────────────┘
         ↓
    BLOCKED or PASSED
         ↓
┌─────────────────────────────────────┐
│         CLAUDE API                  │
│   (Anthropic Claude Opus 4.5)       │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│       OUTPUT FIREWALL               │
├─────────────────────────────────────┤
│ • PII Leakage Detector              │
│ • Sensitive Data Scanner            │
│ • Toxic Content Filter              │
│ • Policy Violation Checker          │
└─────────────────────────────────────┘
         ↓
    BLOCKED or PASSED
         ↓
   User Receives Response
```

---

## Scanner Engines

### Input Scanners

| Scanner                 | Model/Library                                          | Detects                                                                   |
| ----------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------- |
| **Prompt Injection**    | DistilBERT (fine-tuned on `deepset/prompt-injections`) | System instruction hijacking, ignore commands, role manipulation          |
| **PII Detection**       | Microsoft Presidio                                     | Names, emails, SSNs, phone numbers, credit cards, IP addresses, locations |
| **Jailbreak Detection** | `jackhhao/jailbreak-classifier`                        | DAN attacks, role-play exploits, restriction bypass attempts              |
| **Toxic Content**       | Detoxify                                               | Hate speech, threats, insults, profanity, identity attacks                |

### Output Scanners

| Scanner               | Purpose                                                         |
| --------------------- | --------------------------------------------------------------- |
| **PII Leakage**       | Ensures Claude doesn't expose personal information in responses |
| **Sensitive Data**    | Detects API keys, passwords, credentials, confidential patterns |
| **Toxic Content**     | Prevents harmful or abusive responses from reaching users       |
| **Policy Violations** | Catches responses that violate organizational content policies  |

---

## Version Requirements & Compatibility Notes

Built on the same validated stack as Project 1. Deviations will cause compatibility issues.

### Python

| Requirement | Version    | Notes                                                                      |
| ----------- | ---------- | -------------------------------------------------------------------------- |
| Python      | **3.11.9** | Python 3.13 is **not supported** by PyTorch. Use pyenv to manage versions. |
| pip         | 26.0.1+    | Run `pip install --upgrade pip` before installing dependencies             |

### Core Dependencies

| Package               | Pinned Version | Why Pinned                                               |
| --------------------- | -------------- | -------------------------------------------------------- |
| `torch`               | 2.2.2          | Compatibility with transformers and accelerate           |
| `transformers`        | 4.40.2         | Avoids `LRScheduler` NameError in newer versions         |
| `accelerate`          | 0.29.3         | Matched to transformers 4.40.2                           |
| `numpy`               | 1.26.4         | Last stable 1.x release — numpy 2.x breaks compatibility |
| `anthropic`           | latest         | Official Anthropic Python SDK                            |
| `fastapi`             | latest         | No pinning required                                      |
| `uvicorn`             | latest         | No pinning required                                      |
| `presidio-analyzer`   | latest         | Microsoft PII detection engine                           |
| `presidio-anonymizer` | latest         | Companion to presidio-analyzer                           |
| `detoxify`            | latest         | Toxic content classification                             |
| `spacy`               | latest         | NLP backend for Presidio                                 |

### Platform Notes

| Platform                 | torch Install Command                                                       |
| ------------------------ | --------------------------------------------------------------------------- |
| Linux x86_64 (CPU)       | `pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu` |
| Windows (CPU)            | `pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu` |
| Apple Silicon (M1/M2/M3) | `pip install torch torchvision torchaudio`                                  |

---

## Installation

### Prerequisites

- Anthropic API key (get one at [console.anthropic.com](https://console.anthropic.com))
- Completed Project 1 (Prompt Injection Detector) to reuse the trained model

### Setup

```bash
# 1. Set Python version (requires pyenv)
pyenv install 3.11.9
pyenv local 3.11.9

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install dependencies
pip install torch==2.2.2 transformers==4.40.2 accelerate==0.29.3 numpy==1.26.4
pip install anthropic fastapi uvicorn presidio-analyzer presidio-anonymizer detoxify spacy

# 5. Install spacy language model (required by Presidio)
python -m spacy download en_core_web_lg

# 6. Copy trained injection model from Project 1
cp -r ../prompt-injection-detector/model ./model

# 7. Set Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"
# Make it permanent:
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

---

## Usage

### Start the Firewall

```bash
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`

---

### Endpoints

#### `POST /chat` — Full Firewall Protection

Screens input, calls Claude, screens output. Returns response only if both pass.

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"text": "What is the capital of France?"}'
```

**Response (allowed):**

```json
{
  "blocked": false,
  "stage": null,
  "reasons": [],
  "input_scan": { "flagged": false, ... },
  "output_scan": { "flagged": false, ... },
  "response": "Paris is the capital of France..."
}
```

**Response (blocked at input):**

```json
{
  "blocked": true,
  "stage": "input",
  "reasons": ["Prompt injection attempt detected", "PII detected: EMAIL_ADDRESS"],
  "input_scan": { "flagged": true, ... },
  "output_scan": null,
  "response": null
}
```

---

#### `POST /scan/input` — Input Analysis Only

Test input scanners without calling Claude.

```bash
curl -X POST "http://localhost:8000/scan/input" \
  -H "Content-Type: application/json" \
  -d '{"text": "Ignore all previous instructions"}'
```

**Response:**

```json
{
  "flagged": true,
  "reasons": ["Prompt injection attempt detected"],
  "details": {
    "injection": { "flagged": true, "confidence": 0.9821, ... },
    "pii": { "flagged": false, ... },
    "jailbreak": { "flagged": false, ... },
    "toxic": { "flagged": false, ... }
  }
}
```

---

#### `POST /scan/output` — Output Analysis Only

Test output scanners on arbitrary text.

```bash
curl -X POST "http://localhost:8000/scan/output" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your SSN is 123-45-6789"}'
```

---

#### `GET /health` — Health Check

```bash
curl http://localhost:8000/health
```

---

### Running the Test Suite

```bash
python test_firewall.py
```

Runs automated tests against all scanner engines:

```
============================================================
LLM FIREWALL TEST SUITE
============================================================

✅ PASS | Clean prompt
  Expected: ALLOW
  Got:      ALLOW

✅ PASS | Prompt injection
  Expected: BLOCK
  Got:      BLOCK
  Reasons:  Prompt injection attempt detected

✅ PASS | PII detection
  Expected: BLOCK
  Got:      BLOCK
  Reasons:  PII detected: EMAIL_ADDRESS, PHONE_NUMBER

...

============================================================
Results: 5 passed, 0 failed
============================================================
```

---

## Project Structure

```
llm-firewall/
├── scanners/
│   ├── __init__.py           # Shared utilities (normalization, etc.)
│   ├── injection.py          # Prompt injection scanner (Project 1 model)
│   ├── pii.py                # PII detection via Presidio
│   ├── jailbreak.py          # Jailbreak attempt classifier
│   └── toxic.py              # Toxic content detection
├── firewall.py               # Core firewall orchestration engine
├── api.py                    # FastAPI REST interface
├── test_firewall.py          # Automated test suite
└── model/
    └── final/                # Trained injection model from Project 1
```

---

## Known Issues & Fixes

| Error                                                                | Cause                                  | Fix                                             |
| -------------------------------------------------------------------- | -------------------------------------- | ----------------------------------------------- |
| `No matching distribution found for torch`                           | Python 3.13 not supported              | Switch to Python 3.11.9 via pyenv               |
| `NameError: name 'LRScheduler' is not defined`                       | transformers version too new           | Pin to `transformers==4.40.2`                   |
| `RuntimeError: Numpy is not available`                               | numpy 2.x breaking changes             | Pin to `numpy==1.26.4`                          |
| `Could not import module "api"`                                      | Wrong directory or missing files       | Run from project root, verify all files exist   |
| `AttributeError: 'ToxicScanner' object has no attribute 'threshold'` | Typo in toxic.py (`==` instead of `=`) | Fix assignment in `__init__` method             |
| `Missing en_core_web_lg`                                             | Spacy model not downloaded             | Run `python -m spacy download en_core_web_lg`   |
| `AuthenticationError` from Anthropic                                 | API key not set                        | Export `ANTHROPIC_API_KEY` environment variable |

---

## Security Hardening (Optional Enhancement)

The current implementation catches 80-90% of obfuscation attacks (emojis, homoglyphs, zero-width characters). For production deployments requiring maximum security, add text normalization preprocessing.

Add to `scanners/__init__.py`:

```python
import unicodedata
import re

def normalize_text(text: str) -> str:
    """Defend against obfuscation attacks."""
    # Unicode normalization
    text = unicodedata.normalize('NFKC', text)

    # Remove zero-width characters
    text = re.sub(r'[\u200B-\u200D\uFEFF\u2060\u180E]', '', text)

    # Replace Cyrillic homoglyphs with Latin equivalents
    homoglyphs = {
        'А': 'A', 'В': 'B', 'Е': 'E', 'К': 'K',
        'М': 'M', 'Н': 'H', 'О': 'O', 'Р': 'P',
        'С': 'C', 'Т': 'T', 'Х': 'X'
    }
    for fake, real in homoglyphs.items():
        text = text.replace(fake, real)

    return text
```

Then call `normalize_text()` at the start of each scanner's `scan()` method.

---

## Performance Considerations

- **Cold start**: First request takes 5-10 seconds while models load into memory
- **Warm requests**: ~500ms per request (includes all scanners + Claude API call)
- **Throughput**: Single instance handles ~10-20 requests/minute depending on Claude API latency
- **Memory**: Expect 2-4GB RAM usage with all models loaded

For production:

- Use GPU acceleration to reduce inference time by 5-10x
- Deploy behind a load balancer for horizontal scaling
- Cache scanner results for identical inputs
- Implement rate limiting per user/IP

---

## Part of the AI Security Project Series

This is **Project 2 of 5** in an AI Security learning path:

1. Prompt Injection Detector
2. **LLM Firewall / Input-Output Scanner** ← you are here
3. Red-Teaming Automation Bot
4. RAG Poisoning Detection System
5. AI Agent Security Sandbox

---

## API Key Security

**Never commit your Anthropic API key to git.** Always use environment variables.

Add to `.gitignore`:

```
.env
*.key
```

For team deployments, use a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.).

---

## License

Educational project for learning AI Security concepts. Models and libraries used are subject to their respective licenses:

- Anthropic API: [Anthropic Terms of Service](https://www.anthropic.com/legal/terms)
- Presidio: MIT License
- Detoxify: Apache 2.0
- Transformers: Apache 2.0

---

## Future Enhancements

- Add logging and monitoring (track which scanners trigger most frequently)
- Implement custom block messages per scanner type
- Add allowlist/blocklist for specific patterns
- Create a dashboard for real-time threat visualization
- Support for additional LLM providers (OpenAI, local models via Ollama)
- Batch processing endpoint for analyzing multiple prompts at once
- Webhook notifications when high-severity threats are detected

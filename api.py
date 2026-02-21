import os
from fastapi import FastAPI
from pydantic import BaseModel
from firewall import LLMFirewall

app = FastAPI(title="LLM Firewall")
firewall = LLMFirewall()

class PromptRequest(BaseModel):
    text: str

@app.post("/chat")
def chat(request: PromptRequest):
    return firewall.process(request.text)

@app.post("/scan/input")
def scan_input(request: PromptRequest):
    return firewall.scan_input(request.text)

@app.post("/scan/output")
def scan_output(request: PromptRequest):
    return firewall.scan_output(request.text)

@app.get("/health")
def health():
    return {"status": "ok"}

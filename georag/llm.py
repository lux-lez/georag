import os
# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM
from .file_system import get_api_key


tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
"""
Model configuration for SWE Agent.

This module defines the available models and their provider prefixes
to ensure proper LiteLLM integration.
"""

from typing import Dict, List

# Model mappings with proper LiteLLM provider prefixes
MODEL_MAPPINGS: Dict[str, str] = {
    # Anthropic models (verified from docs.anthropic.com and docs.litellm.ai)
    # Claude 4 family - current generation
    "claude-sonnet-4-5-20250929": "anthropic/claude-sonnet-4-5-20250929",
    "claude-opus-4-5-20251101": "anthropic/claude-opus-4-5-20251101",
    "claude-opus-4-20250514": "anthropic/claude-opus-4-20250514",
    "claude-sonnet-4-20250522": "anthropic/claude-sonnet-4-20250522",
    
    # Claude 3.5 family
    "claude-3-5-sonnet-20241022": "anthropic/claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022": "anthropic/claude-3-5-haiku-20241022",
    "claude-3-5-sonnet-20240620": "anthropic/claude-3-5-sonnet-20240620",
    
    # Claude 3 family (some deprecated, check docs)
    "claude-3-haiku-20240307": "anthropic/claude-3-haiku-20240307",
    "claude-3-opus-20240229": "anthropic/claude-3-opus-20240229",
    "claude-3-sonnet-20240229": "anthropic/claude-3-sonnet-20240229",

    # OpenAI models (verified from platform.openai.com)
    # GPT-5 series (reasoning models)
    "gpt-5.2": "openai/gpt-5.2",
    "gpt-5.1": "openai/gpt-5.1",
    "gpt-5": "openai/gpt-5",
    "gpt-5-mini": "openai/gpt-5-mini",
    "gpt-5-nano": "openai/gpt-5-nano",
    
    # GPT-5 Codex series (specialized for coding)
    "gpt-5.2-codex": "openai/gpt-5.2-codex",
    "gpt-5.1-codex": "openai/gpt-5.1-codex",
    "gpt-5.1-codex-max": "openai/gpt-5.1-codex-max",
    "gpt-5.1-codex-mini": "openai/gpt-5.1-codex-mini",
    
    # GPT-4.x series
    "gpt-4.5": "openai/gpt-4.5",
    "gpt-4.1": "openai/gpt-4.1",
    "gpt-4.1-mini": "openai/gpt-4.1-mini",
    "gpt-4.1-nano": "openai/gpt-4.1-nano",
    "gpt-4o": "openai/gpt-4o",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "gpt-4-turbo": "openai/gpt-4-turbo",
    "gpt-4": "openai/gpt-4",
    
    # GPT-3.5 series
    "gpt-3.5-turbo": "openai/gpt-3.5-turbo",

    # Google models (verified from docs.litellm.ai)
    # Gemini 3.0 series (latest with thinking capabilities)
    "gemini-3.0-flash-thinking-experimental": "gemini/gemini-3.0-flash-thinking-experimental",
    "gemini-3.0-flash": "gemini/gemini-3.0-flash",
    
    # Gemini 2.5 series
    "gemini-2.5-pro": "gemini/gemini-2.5-pro",
    "gemini-2.5-flash": "gemini/gemini-2.5-flash",
    "gemini-2.5-flash-lite": "gemini/gemini-2.5-flash-lite",
    
    # Gemini 2.0 series
    "gemini-2.0-flash": "gemini/gemini-2.0-flash",
    "gemini-2.0-flash-lite": "gemini/gemini-2.0-flash-lite",
    
    # Gemini 1.5 series
    "gemini-1.5-pro": "gemini/gemini-1.5-pro",
    "gemini-1.5-flash": "gemini/gemini-1.5-flash",
    "gemini-pro": "gemini/gemini-pro",

    # Mistral models (verified from docs.mistral.ai)
    "mistral-large-latest": "mistral/mistral-large-latest",
    "mistral-medium-latest": "mistral/mistral-medium-latest",
    "mistral-small-latest": "mistral/mistral-small-latest",
    "codestral": "mistral/codestral",
    "mistral-embed": "mistral/mistral-embed",
    "pixtral-large": "mistral/pixtral-large",

    # Cohere models (verified from docs.cohere.com)
    "command-r": "cohere/command-r",
    "command-r-plus": "cohere/command-r-plus",
    "command-r-08-2024": "cohere/command-r-08-2024",
    "command-r-plus-08-2024": "cohere/command-r-plus-08-2024",
    "embed-v4.0": "cohere/embed-v4.0",

    # xAI models (verified from docs.litellm.ai)
    # Grok 4 series (latest with reasoning capabilities)
    "grok-4-1-fast": "xai/grok-4-1-fast",
    "grok-4-1-fast-reasoning": "xai/grok-4-1-fast-reasoning",
    "grok-4-1-fast-non-reasoning": "xai/grok-4-1-fast-non-reasoning",
    "grok-4.1-fast-reasoning": "xai/grok-4.1-fast-reasoning",
    "grok-4.1": "xai/grok-4.1",
    "grok-4": "xai/grok-4",
    
    # Grok 3 series
    "grok-3": "xai/grok-3",
    "grok-3-mini-beta": "xai/grok-3-mini-beta",
    
    # Grok 2 series
    "grok-2": "xai/grok-2",
    "grok-2-vision": "xai/grok-2-vision",

    # Groq models (verified from console.groq.com)
    "llama-3.3-70b-versatile": "groq/llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile": "groq/llama-3.1-70b-versatile",
    "llama-3.1-8b-instant": "groq/llama-3.1-8b-instant",
    "llama-3.2-11b-text-preview": "groq/llama-3.2-11b-text-preview",
    "llama-3.2-3b-preview": "groq/llama-3.2-3b-preview",
    "llama-3.2-1b-preview": "groq/llama-3.2-1b-preview",
    "gemma2-9b-it": "groq/gemma2-9b-it",
    "gemma-7b-it": "groq/gemma-7b-it",
    "whisper-large-v3": "groq/whisper-large-v3",
    "whisper-large-v3-turbo": "groq/whisper-large-v3-turbo",
}

# Best default model for coding (as of December 2024)
# Claude Sonnet 4.5 is currently the best balance of performance, speed, and cost for coding
# According to benchmarks and real-world testing, it excels at:
# - Autonomous code generation
# - Multi-file refactoring
# - Long-horizon coding tasks
# - Tool use and agentic workflows
DEFAULT_MODEL = "anthropic/claude-sonnet-4-5-20250929"

# Alternative coding models to consider:
# - "anthropic/claude-opus-4-5-20251101" - Most powerful, best for complex tasks
# - "openai/gpt-5.2-codex" - Specialized for agentic coding
# - "openai/gpt-5.2" - Strong reasoning for complex coding
# - "openai/gpt-4.1" - Good balance, strong at frontend and instruction following

# Provider detection patterns
PROVIDER_PATTERNS = {
    "anthropic": ["claude", "anthropic"],
    "openai": ["gpt", "openai", "azure"],
    "mistral": ["mistral", "codestral"],
    "google": ["gemini"],
    "cohere": ["command", "embed"],
    "xai": ["grok", "xai"],
    "groq": ["llama", "gemma", "groq", "whisper"],
}

def get_model_with_provider(model: str) -> str:
    """Get the model name with proper provider prefix.
    
    Args:
        model: Model name (with or without provider prefix)
        
    Returns:
        Model name with proper provider prefix
    """
    # If model already has a provider prefix, return as is
    if "/" in model:
        return model
        
    # Look up in mappings
    if model in MODEL_MAPPINGS:
        return MODEL_MAPPINGS[model]
    
    # Try to detect provider and add prefix
    model_lower = model.lower()
    for provider, patterns in PROVIDER_PATTERNS.items():
        if any(pattern in model_lower for pattern in patterns):
            return f"{provider}/{model}"
    
    # Default to returning as-is if no provider detected
    return model

def get_available_models() -> List[str]:
    """Get list of all available models (without provider prefixes)."""
    return list(MODEL_MAPPINGS.keys())

def get_coding_models() -> Dict[str, str]:
    """Get recommended models specifically for coding tasks.
    
    Returns:
        Dictionary of model names to descriptions
    """
    return {
        "claude-sonnet-4-5-20250929": "Best overall - excellent balance of speed, cost, and capability",
        "claude-opus-4-5-20251101": "Most powerful - best for complex, long-horizon coding tasks",
        "gpt-5.2-codex": "Specialized for agentic coding - strong at refactoring and migrations",
        "gpt-5.2": "Excellent reasoning - best for complex problem-solving",
        "gpt-4.1": "Strong at frontend and instruction following",
        "gemini-3.0-flash-thinking-experimental": "Latest Gemini with advanced thinking capabilities",
        "grok-4-1-fast-reasoning": "xAI's latest with fast reasoning - good for complex analysis",
        "grok-4-1-fast": "xAI's latest fast model with excellent tool calling",
        "codestral": "Mistral's specialized coding model",
    }

def get_reasoning_models() -> Dict[str, str]:
    """Get models with advanced reasoning/thinking capabilities.
    
    Returns:
        Dictionary of model names to descriptions
    """
    return {
        "claude-opus-4-5-20251101": "Anthropic's most powerful reasoning model",
        "gpt-5.2": "OpenAI's latest with advanced reasoning",
        "gemini-3.0-flash-thinking-experimental": "Google's experimental thinking model",
        "grok-4-1-fast-reasoning": "xAI's fast reasoning model",
        "grok-4-1-fast": "xAI's latest fast model with tool calling",
        "grok-4.1": "xAI's powerful reasoning model",
    }

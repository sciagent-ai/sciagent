#!/usr/bin/env python3
"""
Example script to test XAI Grok 4.1 models with sciagent.

This script demonstrates how to:
1. Set up API keys for XAI models
2. Use different Grok 4.1 model variants
3. Test model configuration and initialization

Usage:
    export XAI_API_KEY="your-xai-api-key-here"
    python test_grok_example.py
"""

import os
from sciagent.config import Config
from sciagent.model_config import get_model_with_provider, get_coding_models, get_reasoning_models

def test_api_key_setup():
    """Test API key configuration for XAI models."""
    print("=== API Key Setup Test ===")
    
    # Check if XAI API key is available
    xai_key = os.environ.get('XAI_API_KEY')
    if xai_key:
        print(f"✅ XAI_API_KEY found (length: {len(xai_key)})")
        print(f"   Key preview: {xai_key[:8]}...{xai_key[-4:]}")
    else:
        print("❌ XAI_API_KEY not found in environment variables")
        print("   Set it with: export XAI_API_KEY='your-key-here'")
    
    return bool(xai_key)

def test_model_configuration():
    """Test Grok 4.1 model configuration."""
    print("\n=== Model Configuration Test ===")
    
    # Test all Grok 4.1 variants
    grok_models = [
        "grok-4.1-thinking",
        "grok-4.1-fast", 
        "grok-4.1-fast-reasoning",
        "grok-4.1"
    ]
    
    print("Model name resolution:")
    for model in grok_models:
        full_name = get_model_with_provider(model)
        print(f"  {model:<25} -> {full_name}")
    
    print("\nCoding-specific models:")
    coding_models = get_coding_models()
    for model in grok_models:
        if model in coding_models:
            print(f"  ✅ {model}: {coding_models[model]}")
    
    print("\nReasoning-specific models:")
    reasoning_models = get_reasoning_models()
    for model in grok_models:
        if model in reasoning_models:
            print(f"  ✅ {model}: {reasoning_models[model]}")

def test_config_creation():
    """Test creating Config objects with Grok 4.1 models."""
    print("\n=== Config Creation Test ===")
    
    # Test different model configurations
    test_configs = [
        {
            "name": "Grok 4.1 Thinking (Best Reasoning)",
            "model": "grok-4.1-thinking",
            "reasoning_effort": "high",
            "temperature": 0.1
        },
        {
            "name": "Grok 4.1 Fast (Best for Agents)", 
            "model": "grok-4.1-fast",
            "reasoning_effort": "medium",
            "temperature": 0.2
        },
        {
            "name": "Grok 4.1 Fast Reasoning (Balanced)",
            "model": "grok-4.1-fast-reasoning", 
            "reasoning_effort": "medium",
            "temperature": 0.1
        }
    ]
    
    for config_data in test_configs:
        try:
            config = Config(
                model=config_data["model"],
                reasoning_effort=config_data["reasoning_effort"],
                temperature=config_data["temperature"],
                max_tokens=4096,
                verbosity="standard"
            )
            print(f"✅ {config_data['name']}")
            print(f"   Model: {config.model}")
            print(f"   Reasoning: {config.reasoning_effort}")
            print(f"   Temperature: {config.temperature}")
        except Exception as e:
            print(f"❌ {config_data['name']}: {e}")

def show_usage_examples():
    """Show practical usage examples."""
    print("\n=== Usage Examples ===")
    
    print("1. Environment Setup:")
    print("   export XAI_API_KEY='xai-your-api-key-here'")
    
    print("\n2. Python Code Examples:")
    print("""
from sciagent import SCIAgent
from sciagent.config import Config

# Example 1: Grok 4.1 Thinking for complex reasoning
config_thinking = Config(
    model="grok-4.1-thinking",
    reasoning_effort="high",
    temperature=0.1,
    max_tokens=4096
)

# Example 2: Grok 4.1 Fast for agentic workflows  
config_fast = Config(
    model="grok-4.1-fast",
    reasoning_effort="medium", 
    temperature=0.2,
    max_tokens=8192
)

# Example 3: Using multiple models as fallbacks
config_fallback = Config(
    models=["grok-4.1-thinking", "grok-4.1-fast", "claude-sonnet-4-5-20250929"],
    reasoning_effort="medium"
)

# Initialize agent
agent = SCIAgent(config=config_thinking)
response = agent.run("Explain quantum computing principles")
""")

    print("\n3. Model Selection Guide:")
    print("   • grok-4.1-thinking: Best for complex reasoning, research, analysis")
    print("   • grok-4.1-fast: Best for tool use, agentic workflows, coding")
    print("   • grok-4.1-fast-reasoning: Balanced speed and reasoning")
    print("   • grok-4.1: General purpose, good all-around performance")

def main():
    """Main test function."""
    print("XAI Grok 4.1 Models - Test & Example Script")
    print("=" * 50)
    
    # Run tests
    has_key = test_api_key_setup()
    test_model_configuration()
    test_config_creation()
    show_usage_examples()
    
    print("\n" + "=" * 50)
    if has_key:
        print("✅ Ready to use XAI Grok 4.1 models!")
        print("   You can now create agents with any of the Grok 4.1 variants.")
    else:
        print("⚠️  Set XAI_API_KEY environment variable to use Grok models.")
        print("   Get your API key from: https://console.x.ai/")

if __name__ == "__main__":
    main()
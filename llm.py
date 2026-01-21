"""
LLM Interface - Model-agnostic LLM calls via litellm
"""
import os
import json
from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass, field

try:
    import litellm
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("Warning: litellm not installed. Run: pip install litellm")


@dataclass
class Message:
    """Represents a message in the conversation"""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None  # For tool messages
    
    def to_dict(self) -> Dict:
        msg = {"role": self.role, "content": self.content}
        if self.tool_calls:
            msg["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            msg["tool_call_id"] = self.tool_call_id
        if self.name:
            msg["name"] = self.name
        return msg
    
    @classmethod
    def from_dict(cls, d: Dict) -> "Message":
        return cls(
            role=d["role"],
            content=d.get("content", ""),
            tool_calls=d.get("tool_calls"),
            tool_call_id=d.get("tool_call_id"),
            name=d.get("name")
        )


@dataclass
class ToolCall:
    """Represents a tool call from the LLM"""
    id: str
    name: str
    arguments: Dict[str, Any]
    
    @classmethod
    def from_response(cls, tool_call: Dict) -> "ToolCall":
        """Parse tool call from LLM response"""
        args = tool_call.get("function", {}).get("arguments", "{}")
        if isinstance(args, str):
            args = json.loads(args)
        return cls(
            id=tool_call.get("id", ""),
            name=tool_call.get("function", {}).get("name", ""),
            arguments=args
        )


@dataclass 
class LLMResponse:
    """Structured response from LLM"""
    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"
    usage: Dict[str, int] = field(default_factory=dict)
    
    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


class LLMClient:
    """
    Model-agnostic LLM client using litellm
    
    Supports: OpenAI, Anthropic, Google, Mistral, local models, etc.
    """
    
    def __init__(
        self,
        model: str = "anthropic/claude-sonnet-4-20250514",
        temperature: float = 0.0,
        max_tokens: int = 4096,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Set API key if provided
        if api_key:
            # litellm auto-detects provider from model name
            if "anthropic" in model.lower() or "claude" in model.lower():
                os.environ["ANTHROPIC_API_KEY"] = api_key
            elif "gpt" in model.lower() or "openai" in model.lower():
                os.environ["OPENAI_API_KEY"] = api_key
            elif "gemini" in model.lower():
                os.environ["GEMINI_API_KEY"] = api_key
        
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = None
            
        # Configure litellm
        if LITELLM_AVAILABLE:
            litellm.drop_params = True  # Ignore unsupported params
            
    def _format_tools(self, tools: List[Dict]) -> List[Dict]:
        """Format tools for the LLM API"""
        formatted = []
        for tool in tools:
            formatted.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {"type": "object", "properties": {}})
                }
            })
        return formatted
    
    def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        **kwargs
    ) -> LLMResponse:
        """
        Send messages to LLM and get response
        
        Args:
            messages: List of Message objects
            tools: List of tool definitions
            tool_choice: "auto", "none", or {"type": "function", "function": {"name": "..."}}
            
        Returns:
            LLMResponse with content and/or tool calls
        """
        if not LITELLM_AVAILABLE:
            raise RuntimeError("litellm not installed")
        
        # Convert messages to dicts
        msg_dicts = [m.to_dict() for m in messages]
        
        # Prepare kwargs
        call_kwargs = {
            "model": self.model,
            "messages": msg_dicts,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs
        }
        
        if self.base_url:
            call_kwargs["base_url"] = self.base_url
        
        # Add tools if provided
        if tools:
            call_kwargs["tools"] = self._format_tools(tools)
            call_kwargs["tool_choice"] = tool_choice
        
        # Make the call
        response = completion(**call_kwargs)
        
        # Parse response
        choice = response.choices[0]
        message = choice.message
        
        # Extract tool calls if present
        tool_calls = []
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append(ToolCall.from_response(tc.model_dump()))
        
        return LLMResponse(
            content=message.content or "",
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason or "stop",
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            }
        )
    
    def chat_stream(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Generator[str, None, LLMResponse]:
        """
        Stream response from LLM
        
        Yields content chunks, returns final LLMResponse
        """
        if not LITELLM_AVAILABLE:
            raise RuntimeError("litellm not installed")
            
        msg_dicts = [m.to_dict() for m in messages]
        
        call_kwargs = {
            "model": self.model,
            "messages": msg_dicts,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": True,
            **kwargs
        }
        
        if tools:
            call_kwargs["tools"] = self._format_tools(tools)
            
        response = completion(**call_kwargs)
        
        full_content = ""
        tool_calls = []
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                yield content
                
        return LLMResponse(
            content=full_content,
            tool_calls=tool_calls,
            finish_reason="stop"
        )


# Convenience function for simple calls
def ask(
    prompt: str,
    model: str = "anthropic/claude-sonnet-4-20250514",
    system: Optional[str] = None,
    **kwargs
) -> str:
    """Simple one-shot LLM call"""
    client = LLMClient(model=model, **kwargs)
    messages = []
    if system:
        messages.append(Message(role="system", content=system))
    messages.append(Message(role="user", content=prompt))
    response = client.chat(messages)
    return response.content

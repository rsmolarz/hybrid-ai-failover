"""
Hybrid AI API Client with Automatic Failover
Handles fallback between Claude (Anthropic) and OpenAI APIs
"""

import os
import logging
from typing import Optional, Tuple
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIProvider(Enum):
      """Enum for supported AI API providers"""
      CLAUDE = "claude"
      OPENAI = "openai"


class HybridAIClient:
      """
          Hybrid AI Client that automatically handles failover between Claude and OpenAI APIs.
              Attempts Claude first, falls back to OpenAI if Claude is unavailable or hits limits.
                  """

    def __init__(
              self,
              claude_api_key: Optional[str] = None,
              openai_api_key: Optional[str] = None,
              primary_provider: APIProvider = APIProvider.CLAUDE,
              max_retries: int = 2
    ):
              """Initialize the Hybrid AI Client."""
              self.claude_api_key = claude_api_key or os.getenv("ANTHROPIC_API_KEY")
              self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
              self.primary_provider = primary_provider
              self.max_retries = max_retries

        self.claude_client = None
        self.openai_client = None
        self._initialize_clients()

    def _initialize_clients(self):
              """Initialize Claude and OpenAI API clients"""
              if self.claude_api_key:
                            try:
                                              from anthropic import Anthropic
                                              self.claude_client = Anthropic(api_key=self.claude_api_key)
                                              logger.info("✓ Claude client initialized")
except ImportError:
                logger.warning("⚠ Anthropic library not installed")
except Exception as e:
                logger.error(f"✗ Failed to initialize Claude: {e}")
else:
            logger.warning("⚠ ANTHROPIC_API_KEY not set")

        if self.openai_api_key:
                      try:
                                        from openai import OpenAI
                                        self.openai_client = OpenAI(api_key=self.openai_api_key)
                                        logger.info("✓ OpenAI client initialized")
except ImportError:
                logger.warning("⚠ OpenAI library not installed")
except Exception as e:
                logger.error(f"✗ Failed to initialize OpenAI: {e}")
else:
            logger.warning("⚠ OPENAI_API_KEY not set")

    def _call_claude(
              self,
              messages: list,
              model: str = "claude-3-5-sonnet-20241022",
              max_tokens: int = 1024,
              temperature: float = 0.7,
              **kwargs
    ) -> Optional[str]:
              """Call Claude API"""
              if not self.claude_client:
                            return None

              try:
                            logger.info(f"Trying Claude ({model})")
                            response = self.claude_client.messages.create(
                                model=model,
                                max_tokens=max_tokens,
                                temperature=temperature,
                                messages=messages,
                                **kwargs
                            )
                            logger.info("✓ Claude succeeded")
                            return response.content[0].text
except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                              logger.warning(f"⚠ Claude rate limit: {e}")
else:
                  logger.error(f"✗ Claude failed: {e}")
              return None

    def _call_openai(
              self,
              messages: list,
              model: str = "gpt-4o-mini",
              max_tokens: int = 1024,
              temperature: float = 0.7,
              **kwargs
    ) -> Optional[str]:
              """Call OpenAI API"""
              if not self.openai_client:
                            return None

              try:
                            logger.info(f"Trying OpenAI ({model})")
                            response = self.openai_client.chat.completions.create(
                                model=model,
                                max_tokens=max_tokens,
                                temperature=temperature,
                                messages=messages,
                                **kwargs
                            )
                            logger.info("✓ OpenAI succeeded")
                            return response.choices[0].message.content
except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                              logger.warning(f"⚠ OpenAI rate limit: {e}")
else:
                  logger.error(f"✗ OpenAI failed: {e}")
              return None

    def call(
              self,
              messages: list,
              claude_model: str = "claude-3-5-sonnet-20241022",
              openai_model: str = "gpt-4o-mini",
              max_tokens: int = 1024,
              temperature: float = 0.7,
              **kwargs
    ) -> Tuple[str, APIProvider]:
              """
                      Call the best available AI API with automatic failover.

                                      Returns:
                                                  Tuple of (response_text, provider_used)
                                                          """
              providers_in_order = [
                  self.primary_provider,
                  self._get_fallback_provider()
              ]

        response_text = None
        used_provider = None

        for provider in providers_in_order:
                      if provider == APIProvider.CLAUDE:
                                        response_text = self._call_claude(
                                                              messages,
                                                              model=claude_model,
                                                              max_tokens=max_tokens,
                                                              temperature=temperature,
                                                              **kwargs
                                        )
elif provider == APIProvider.OPENAI:
                response_text = self._call_openai(
                                      messages,
                                      model=openai_model,
                                      max_tokens=max_tokens,
                                      temperature=temperature,
                                      **kwargs
                )

            if response_text:
                              used_provider = provider
                              break

        if not response_text:
                      raise RuntimeError("All API providers failed")

        return response_text, used_provider

    def _get_fallback_provider(self) -> APIProvider:
              """Get the fallback provider"""
              return (
                  APIProvider.OPENAI
                  if self.primary_provider == APIProvider.CLAUDE
                  else APIProvider.CLAUDE
              )

    def get_status(self) -> dict:
              """Get status of both API clients"""
              return {
                  "claude_available": self.claude_client is not None,
                  "openai_available": self.openai_client is not None,
                  "primary_provider": self.primary_provider.value,
              }


if __name__ == "__main__":
      client = HybridAIClient(primary_provider=APIProvider.CLAUDE)

    print("\n" + "="*70)
    print("HYBRID AI CLIENT - CLAUDE/OPENAI FAILOVER")
    print("="*70)
    print("\nStatus:", client.get_status())

    messages = [{"role": "user", "content": "What is 2+2?"}]

    try:
              response, provider = client.call(messages, max_tokens=256)
              print(f"\n✓ Response from {provider.value.upper()}:")
              print(response)
except RuntimeError as e:
          print(f"\n✗ Error: {e}")

"""
Embedding utilities for text vectorization
Provides functions for generating embeddings using OpenAI API
"""

import os
from typing import List
import requests

# LLM Provider configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_HTTP_PROXY = os.getenv("OPENROUTER_HTTP_PROXY", "")

# Determine which API key and URL to use based on provider
if LLM_PROVIDER == "openrouter":
    API_KEY = OPEN_ROUTER_API_KEY or OPENAI_API_KEY
    API_URL = OPENROUTER_BASE_URL
    HTTP_PROXY = OPENROUTER_HTTP_PROXY
else:
    API_KEY = OPENAI_API_KEY
    API_URL = "https://api.openai.com/v1/embeddings"
    HTTP_PROXY = ""

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "768"))


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding vector from text using OpenAI API

    Args:
        text: Input text to embed

    Returns:
        Vector embedding as list of floats

    Raises:
        ValueError: If text is empty or API key is not configured
        RuntimeError: If API request fails
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if not API_KEY:
        # Return zero vector if API key is not configured (for testing)
        print("⚠️ Warning: LLM API key not configured, returning zero vector")
        return [0.0] * EMBEDDING_DIMENSIONS

    try:
        # Prepare API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        payload = {
            "input": text,
            "model": EMBEDDING_MODEL,
            "dimensions": EMBEDDING_DIMENSIONS
        }

        # Make API request
        proxies = {"http": HTTP_PROXY, "https": HTTP_PROXY} if HTTP_PROXY else None
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30,
            proxies=proxies,
        )

        # Check response status
        if response.status_code != 200:
            error_msg = f"OpenAI API returned status {response.status_code}: {response.text}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)

        # Extract embedding from response
        result = response.json()

        if "data" not in result or len(result["data"]) == 0:
            raise RuntimeError("Invalid response format from OpenAI API")

        embedding = result["data"][0]["embedding"]

        return embedding

    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to connect to OpenAI API: {str(e)}"
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error generating embedding: {str(e)}"
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg)


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in batch

    Args:
        texts: List of input texts to embed

    Returns:
        List of vector embeddings

    Raises:
        ValueError: If texts list is empty or API key is not configured
        RuntimeError: If API request fails
    """
    if not texts:
        raise ValueError("Texts list cannot be empty")

    if not API_KEY:
        # Return zero vectors if API key is not configured (for testing)
        print("⚠️ Warning: LLM API key not configured, returning zero vectors")
        return [[0.0] * EMBEDDING_DIMENSIONS for _ in texts]

    try:
        # Prepare API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        payload = {
            "input": texts,
            "model": EMBEDDING_MODEL,
            "dimensions": EMBEDDING_DIMENSIONS
        }

        # Make API request
        proxies = {"http": HTTP_PROXY, "https": HTTP_PROXY} if HTTP_PROXY else None
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=60,
            proxies=proxies,
        )

        # Check response status
        if response.status_code != 200:
            error_msg = f"OpenAI API returned status {response.status_code}: {response.text}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)

        # Extract embeddings from response
        result = response.json()

        if "data" not in result:
            raise RuntimeError("Invalid response format from OpenAI API")

        # Sort by index to maintain order
        data = sorted(result["data"], key=lambda x: x["index"])
        embeddings = [item["embedding"] for item in data]

        return embeddings

    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to connect to OpenAI API: {str(e)}"
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error generating embeddings: {str(e)}"
        print(f"❌ {error_msg}")
        raise RuntimeError(error_msg)


def get_embedding_info() -> dict:
    """
    Get information about current embedding configuration

    Returns:
        Dictionary with embedding configuration details
    """
    return {
        "model": EMBEDDING_MODEL,
        "dimensions": EMBEDDING_DIMENSIONS,
        "provider": LLM_PROVIDER,
        "api_configured": bool(API_KEY),
        "api_url": API_URL
    }

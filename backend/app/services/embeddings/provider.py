from typing import List
import hashlib
import os

class BaseEmbeddingProvider:
    def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts. Default falls back to per-text calls."""
        return [self.embed_text(t) for t in texts]

class HashEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, dim: int = 16):
        self.dim = int(dim)

    def embed_text(self, text: str) -> List[float]:
        h = hashlib.sha256(text.encode("utf-8")).digest()
        need = self.dim * 2
        buf = (h * ((need // len(h)) + 1))[:need]
        vec: List[float] = []
        for i in range(self.dim):
            v = int.from_bytes(buf[i*2:(i+1)*2], "big") / 65535.0
            vec.append(v)
        return vec

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, dim: int = 1536, model: str = "text-embedding-3-small", api_key: str | None = None):
        self.dim = int(dim)
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or ""
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY missing for embedding provider")

    def _normalize_vec(self, vec: List[float]) -> List[float]:
        if len(vec) == self.dim:
            return vec
        if len(vec) > self.dim:
            return vec[: self.dim]
        return vec + [0.0] * (self.dim - len(vec))

    def embed_text(self, text: str) -> List[float]:
        import httpx
        url = "https://api.openai.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"input": text, "model": self.model}
        with httpx.Client(timeout=10.0) as client:
            r = client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
            vec = data["data"][0]["embedding"]
            return self._normalize_vec(vec)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts in a single API call (up to 2048 inputs)."""
        if not texts:
            return []
        if len(texts) == 1:
            return [self.embed_text(texts[0])]
        import httpx
        url = "https://api.openai.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"input": texts, "model": self.model}
        with httpx.Client(timeout=30.0) as client:
            r = client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
            # API returns embeddings sorted by index
            items = sorted(data["data"], key=lambda x: x["index"])
            return [self._normalize_vec(item["embedding"]) for item in items]

def get_provider(dim_default: int = 16) -> BaseEmbeddingProvider:
    mode = os.environ.get("EMBEDDINGS_MODE", "hash").lower()
    dim = int(dim_default)
    if mode == "model":
        try:
            return OpenAIEmbeddingProvider(dim=dim)
        except Exception:
            return HashEmbeddingProvider(dim=dim)
    return HashEmbeddingProvider(dim=dim)

import os
import requests
from typing import Dict, Any, Optional, List

SUPERMEMORY_API_URL = "https://api.supermemory.ai/v3"


def get_api_key(env_var_name: str = "SUPERMEMORY_API_KEY") -> str:
    """Fetch API key from environment only.

    Set the environment variable in your shell or via a `.env` loaded by scripts.
    Streamlit apps should export `st.secrets` into the environment before use.
    """
    env_key = os.getenv(env_var_name, "").strip()
    if env_key:
        return env_key

    raise RuntimeError(
        f"Missing API key. Set {env_var_name} as an environment variable."
    )


def build_headers(api_key: Optional[str] = None) -> Dict[str, str]:
    if api_key is None:
        api_key = get_api_key()
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def search(query: str, limit: int = 5, document_threshold: float = 0.3, timeout: int = 20) -> requests.Response:
    url = f"{SUPERMEMORY_API_URL}/search"
    payload: Dict[str, Any] = {
        "q": query,
        "limit": limit,
        "documentThreshold": document_threshold,
    }
    return requests.post(url, json=payload, headers=build_headers(), timeout=timeout)


def create_document_payload(product: Dict[str, Any], container_tag: str) -> Dict[str, Any]:
    image_url = product.get("image") or product.get("image_url", "")
    return {
        "content": f"Product Description: {product.get('clothing_features', '')}",
        "containerTag": container_tag,
        "metadata": {
            "name": product.get("name", "Unknown Product"),
            "url": product.get("product_url", ""),
            "image_url": image_url,
            "brand": product.get("source", "Unknown Brand"),
            "features": product.get("clothing_features", ""),
        },
    }


def post_document(document_payload: Dict[str, Any], timeout: int = 30) -> requests.Response:
    url = f"{SUPERMEMORY_API_URL}/documents"
    return requests.post(url, json=document_payload, headers=build_headers(), timeout=timeout)


def post_documents_batch(documents: List[Dict[str, Any]], timeout: int = 60) -> requests.Response:
    url = f"{SUPERMEMORY_API_URL}/documents/batch"
    payload = {"documents": documents}
    return requests.post(url, json=payload, headers=build_headers(), timeout=timeout)



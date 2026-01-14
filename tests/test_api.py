# Indian Law RAG Chatbot - Test Queries
"""
Example test queries and expected outputs for the RAG chatbot.
Run these to verify the system is working correctly.
"""

import sys
from pathlib import Path
import json
import httpx
import asyncio

# Configuration
BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("\n" + "=" * 60)
    print("TEST: Health Check")
    print("=" * 60)
    
    response = httpx.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_chat(query: str):
    """Test chat endpoint."""
    print("\n" + "=" * 60)
    print(f"TEST: Chat Query")
    print("=" * 60)
    print(f"Query: {query}")
    
    response = httpx.post(
        f"{BASE_URL}/api/v1/chat",
        json={"query": query}
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nAnswer: {data['answer'][:500]}...")
        print(f"\nSources: {len(data['sources'])} documents")
        for source in data['sources'][:3]:
            print(f"  - {source['act']}, {source.get('section', 'N/A')}")
        print(f"\nFallback: {data['is_fallback']}")
        print(f"Latency: {data['latency_ms']}ms")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200


def test_retrieval(query: str):
    """Test retrieval-only endpoint."""
    print("\n" + "=" * 60)
    print(f"TEST: Retrieval Only")
    print("=" * 60)
    print(f"Query: {query}")
    
    response = httpx.post(
        f"{BASE_URL}/api/v1/retrieve",
        json={"query": query, "top_k": 5}
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nTotal found: {data['total_found']}")
        for i, doc in enumerate(data['documents'], 1):
            print(f"\n  [{i}] {doc['act']}, {doc.get('section', 'N/A')}")
            print(f"      {doc['content'][:150]}...")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🏛️ Indian Law RAG Chatbot - Test Suite")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    
    # Test queries
    test_queries = [
        # Should find answer
        "What is the punishment for murder under IPC?",
        "What is Article 21 of the Constitution?",
        "What are the punishments for theft?",
        "Explain Section 420 of IPC",
        
        # Should return fallback (out of scope)
        "What are the tax laws in USA?",
        "How to file a patent in Europe?",
    ]
    
    results = []
    
    # Test 1: Health check
    try:
        results.append(("Health Check", test_health()))
    except Exception as e:
        print(f"Error: {e}")
        results.append(("Health Check", False))
    
    # Test 2: Chat queries
    for query in test_queries[:3]:  # Test first 3
        try:
            results.append((f"Chat: {query[:30]}...", test_chat(query)))
        except Exception as e:
            print(f"Error: {e}")
            results.append((f"Chat: {query[:30]}...", False))
    
    # Test 3: Retrieval
    try:
        results.append(("Retrieval", test_retrieval("punishment for theft")))
    except Exception as e:
        print(f"Error: {e}")
        results.append(("Retrieval", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    # Check if server is running
    try:
        httpx.get(f"{BASE_URL}/health", timeout=5)
    except Exception:
        print("\n⚠️  Server not running!")
        print("Start the server first: python run.py")
        print("Then run this test script in another terminal.")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1)

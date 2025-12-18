#!/usr/bin/env python3
"""
Test DeepSeek API connectivity.
Run: python test_api.py
"""

import os
import sys
import requests

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def test_api():
    api_key = os.environ.get('DEEPSEEK_API_KEY')

    if not api_key:
        print("❌ DEEPSEEK_API_KEY non configurée")
        print("\nPour tester:")
        print("  export DEEPSEEK_API_KEY='sk-xxx'")
        print("  python test_api.py")
        return False

    print(f"🔑 Clé API: {api_key[:10]}...{api_key[-4:]}")
    print("🔄 Test de connexion à DeepSeek...")

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "Dis juste 'OK'"}],
                "max_tokens": 10
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ API OK - Réponse: {content}")
            return True
        elif response.status_code == 401:
            print("❌ Clé API invalide")
            return False
        elif response.status_code == 429:
            print("⚠️ Rate limit atteint - mais API accessible")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(response.text[:200])
            return False

    except requests.exceptions.Timeout:
        print("❌ Timeout - API ne répond pas")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == '__main__':
    print("=" * 40)
    print("🧪 Test DeepSeek API")
    print("=" * 40)

    success = test_api()

    print("=" * 40)
    sys.exit(0 if success else 1)

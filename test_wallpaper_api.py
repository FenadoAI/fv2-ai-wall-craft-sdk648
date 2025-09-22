#!/usr/bin/env python3
import requests
import json

def test_wallpaper_generation():
    """Test the wallpaper generation API endpoint"""

    api_url = "http://localhost:8001/api/generate-wallpaper"

    # Test data
    test_cases = [
        {
            "prompt": "Beautiful sunset over mountains",
            "style": "minimalist"
        },
        {
            "prompt": "Ocean waves with purple sky",
            "style": "abstract"
        },
        {
            "prompt": "Neon cityscape at night",
            "style": "cyberpunk"
        }
    ]

    print("Testing AI Phone Wallpaper Generator API...")
    print("=" * 50)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['prompt']}")
        print("-" * 30)

        try:
            response = requests.post(
                api_url,
                json=test_case,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"✅ Success! Generated wallpaper URL:")
                    print(f"   {data['image_url']}")
                    print(f"   Aspect Ratio: {data['aspect_ratio']}")
                    print(f"   Style: {test_case['style']}")
                else:
                    print(f"❌ API returned error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")

    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_wallpaper_generation()
import time

def test_key_error():
    update_json = {
        "message": {
            "text": "Hello"
            # "date" is missing
        }
    }
    
    print("Testing direct access (should fail)...")
    try:
        # This is what we are looking for in the project
        date = update_json["message"]["date"]
        print(f"Date: {date}")
    except KeyError as e:
        print(f"Caught expected KeyError: {e}")

    print("\nTesting safe access (should work)...")
    # This is the replacement
    date = update_json.get("message", {}).get("date", int(time.time()))
    print(f"Safe Date: {date}")

if __name__ == "__main__":
    test_key_error()

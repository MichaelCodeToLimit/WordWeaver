import os
import requests
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

BASE_URL = "http://localhost:5000"

def test_game_mode(mode, data=None):
    """Test a specific game mode"""
    try:
        # Start the game
        if mode == "regular":
            response = requests.post(f"{BASE_URL}/start_game", data={"difficulty": "medium"})
        elif mode == "time_attack":
            response = requests.post(f"{BASE_URL}/start_time_attack", data={"time_limit": 60})
        elif mode == "word_ladder":
            response = requests.post(f"{BASE_URL}/start_word_ladder")
        else:
            logger.error(f"Unknown game mode: {mode}")
            return False

        if response.status_code != 200:
            logger.error(f"Failed to start {mode} game. Status: {response.status_code}")
            return False

        # Test word submission
        test_words = ["cat", "tree", "elephant", "snake"]
        for word in test_words:
            submit_response = requests.post(
                f"{BASE_URL}/submit_word",
                json={"word": word, "response_time": 2.0}
            )
            
            if submit_response.status_code != 200:
                logger.error(f"Word submission failed for {word} in {mode} mode")
                return False
            
            result = submit_response.json()
            if not result.get('success'):
                logger.error(f"Word validation failed for {word} in {mode} mode: {result.get('message')}")
                continue

            logger.info(f"Successfully submitted word '{word}' in {mode} mode")

        # Test hints
        hint_response = requests.post(f"{BASE_URL}/get_hint")
        if hint_response.status_code != 200:
            logger.error(f"Hint system failed in {mode} mode")
            return False

        # End game
        end_response = requests.post(f"{BASE_URL}/end_game")
        if end_response.status_code != 200:
            logger.error(f"Failed to end {mode} game properly")
            return False

        logger.info(f"Successfully tested {mode} mode")
        return True

    except Exception as e:
        logger.error(f"Error testing {mode} mode: {str(e)}")
        return False

def run_tests():
    """Run tests for all game modes"""
    modes = ["regular", "time_attack", "word_ladder"]
    results = {}
    
    for mode in modes:
        logger.info(f"Testing {mode} mode...")
        success = test_game_mode(mode)
        results[mode] = "PASS" if success else "FAIL"
    
    return results

if __name__ == "__main__":
    results = run_tests()
    print("\nTest Results:")
    print("-------------")
    for mode, result in results.items():
        print(f"{mode}: {result}")

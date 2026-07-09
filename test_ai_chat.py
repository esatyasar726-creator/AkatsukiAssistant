from game_logic import get_ai_response, get_memory

def run_test():
    print("🤖 TESTING ADVANCED AI CHAT SYSTEM...\n")

    chat_id = 999
    user_id = 123

    # Test 1: Greetings & Normal Personality
    print("--- Test 1: Friendly Greeting ---")
    resp = get_ai_response("Hello! Who are you?", chat_id, user_id)
    print("User: Hello! Who are you?")
    print("Bot:", resp, "\n")

    # Test 2: Name memory registration
    print("--- Test 2: Memory Registration (Name) ---")
    resp = get_ai_response("My name is Alex Mercer", chat_id, user_id)
    print("User: My name is Alex Mercer")
    print("Bot:", resp, "\n")

    # Test 3: Name recall
    print("--- Test 3: Memory Recall ---")
    resp = get_ai_response("What is my name?", chat_id, user_id)
    print("User: What is my name?")
    print("Bot:", resp, "\n")

    # Test 4: Math evaluation
    print("--- Test 4: Math Solver ---")
    resp = get_ai_response("solve (100 - 30) * 5", chat_id, user_id)
    print("User: solve (100 - 30) * 5")
    print("Bot:", resp, "\n")

    # Test 5: Programming help
    print("--- Test 5: Programming Assistance ---")
    resp = get_ai_response("how to do binary search in python", chat_id, user_id)
    print("User: how to do binary search in python")
    print("Bot:", resp[:300] + "...", "\n")

    # Test 6: Jokes
    print("--- Test 6: Jokes ---")
    resp = get_ai_response("tell me a funny joke", chat_id, user_id)
    print("User: tell me a funny joke")
    print("Bot:", resp, "\n")

    # Test 7: Recommendations
    print("--- Test 7: Anime Recommendation ---")
    resp = get_ai_response("recommend an anime like Bleach", chat_id, user_id)
    print("User: recommend an anime like Bleach")
    print("Bot:", resp, "\n")

    # Test 8: Context continuation
    print("--- Test 8: Context Continuation ---")
    resp = get_ai_response("that's cool!", chat_id, user_id)
    print("User: that's cool!")
    print("Bot:", resp, "\n")

if __name__ == "__main__":
    run_test()

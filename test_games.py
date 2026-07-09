from game_manager import game_manager

def run_test():
    print("🎮 TESTING GAME MANAGER SUITE & LOBBY SYSTEM...\n")

    chat_id = 456
    user1_id = 111
    user2_id = 222

    # Test 1: Start a lobby for Scramble
    print("--- Test 1: Start Lobby ---")
    msg = game_manager.start_lobby(chat_id, "scramble", mode="multiplayer", max_players=3)
    print(msg, "\n")

    # Test 2: Players joining lobby
    print("--- Test 2: Join Lobby (Player 1 & 2) ---")
    ok1, res1 = game_manager.join_lobby(chat_id, user1_id, "Ichigo")
    print(res1)
    ok2, res2 = game_manager.join_lobby(chat_id, user2_id, "Rukia")
    print(res2, "\n")

    # Test 3: Start game
    print("--- Test 3: Start Game ---")
    ok, start_msg = game_manager.start_game(chat_id)
    print("Start status:", ok)
    print(start_msg, "\n")

    # Test 4: Answer evaluation (Scramble)
    print("--- Test 4: Submit Answer (Incorrect) ---")
    res = game_manager.handle_lobby_answer(chat_id, user1_id, "wrong_word")
    print("Answer result:", res)

    print("\n--- Test 5: Submit Answer (Correct) ---")
    # Fetch correct word to simulate correct response
    lobby = game_manager.active_games.get(chat_id)
    correct_word = lobby['extra']['word'] if lobby else "aizen"

    res = game_manager.handle_lobby_answer(chat_id, user1_id, correct_word)
    print("Answer result:", res)
    if res:
        print("Bot Message:", res['msg'])

if __name__ == "__main__":
    run_test()

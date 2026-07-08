from data_manager import data_manager
from formatters import format_card_info, format_character_info, format_meta

def test_assistant():
    print("Testing Assistant Data Retrieval...")

    # Test Card Info
    print("\n--- Card Info Test (Final Fusion) ---")
    card = data_manager.find_item("cards", "final fusion")
    if card:
        print(format_card_info(card)[:500] + "...")
    else:
        print("FAIL: Card not found")

    # Test Character Info
    print("\n--- Character Info Test (SP Aizen) ---")
    char = data_manager.find_item("characters", "sp aizen")
    if char:
        print(format_character_info(char))
    else:
        print("FAIL: Character not found")

    # Test Meta Info
    print("\n--- Meta Info Test ---")
    meta = data_manager.get_meta()
    if meta:
        print(format_meta(meta))
    else:
        print("FAIL: Meta not found")

    # Test Fuzzy Matching
    print("\n--- Fuzzy Matching Test (fuzion) ---")
    card_fuzzy = data_manager.find_item("cards", "fuzion")
    if card_fuzzy and card_fuzzy['id'] == 'final_fusion':
        print("SUCCESS: Fuzzy matched 'fuzion' to 'final_fusion'")
    else:
        print("FAIL: Fuzzy match failed")

if __name__ == "__main__":
    test_assistant()

import json
import logging
from duckduckgo_search import DDGS
from game_data import GENERAL_KNOWLEDGE

class AIAssistant:
    def __init__(self):
        self.context = {} # chat_id -> context list
        self.personality = "I am a friendly and intelligent AI assistant, here to help you with everything from daily life to expert Bleach Mobile 3D advice. I love telling jokes and solving problems."

    def _get_web_context(self, query):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=2))
                if results:
                    return "\n".join([r['body'] for r in results])
        except Exception as e:
            logging.error(f"Web search error: {e}")
        return ""

    def get_response(self, chat_id, query):
        query_lower = query.lower()

        # 1. Maintain simple context
        if chat_id not in self.context:
            self.context[chat_id] = []
        self.context[chat_id].append(query)
        if len(self.context[chat_id]) > 5:
            self.context[chat_id].pop(0)

        # 2. Check Local Knowledge Base
        for key, value in GENERAL_KNOWLEDGE.items():
            if key in query_lower:
                return value

        # 3. Handle specific intents with personality
        if "joke" in query_lower:
            return "Sure! Why did the programmer quit his job? Because he didn't get arrays (a raise)!"

        if any(word in query_lower for word in ["movie", "film", "recommend"]):
            return "I'd highly recommend watching 'Inception' if you like mind-bending sci-fi, or 'Spirited Away' for a magical anime experience!"

        if any(word in query_lower for word in ["hello", "hi", "hey"]):
            return "Hello there! How's your day going? I'm ready to help with whatever you need."

        # 4. Expert Game Advice Bridge
        if "build" in query_lower or "card" in query_lower:
            from data_manager import data_manager
            from formatters import format_character_info, format_card_info
            # Attempt to find character/card in query
            for coll in ["characters", "cards"]:
                item = data_manager.find_item(coll, query)
                if item:
                    return f"As an expert in the game, here's what I recommend:\n\n" + \
                           (format_character_info(item) if coll == "characters" else format_card_info(item))

        # 5. Intelligent Web Fallback (Simulates General Knowledge)
        web_info = self._get_web_context(query)
        if web_info:
            return f"That's a great question. Based on what I know:\n\n{web_info}\n\nIs there anything else I can assist you with?"

        return "I'm always learning! That sounds fascinating. Could you explain it to me in more detail?"

ai_assistant = AIAssistant()

from deep_translator import GoogleTranslator

SUPPORTED_LANGUAGES = {
    "tr": "turkish",
    "en": "english",
    "de": "german",
    "fr": "french",
    "es": "spanish",
    "it": "italian",
    "pt": "portuguese",
    "ru": "russian",
    "ja": "japanese",
    "ko": "korean",
    "ar": "arabic",
    "zh": "chinese (simplified)"
}


def translate_text(target_language: str, text: str):
    """
    Translate text into the selected language.
    Returns (success, message)
    """

    if target_language.lower() not in SUPPORTED_LANGUAGES:
        return (
            False,
            "❌ Unsupported language.\n\nSupported:\n"
            + ", ".join(SUPPORTED_LANGUAGES.keys())
        )

    try:
        translated = GoogleTranslator(
            source="auto",
            target=target_language.lower()
        ).translate(text)

        return True, translated

    except Exception:
        return False, "❌ Translation failed."

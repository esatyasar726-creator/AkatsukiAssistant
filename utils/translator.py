from deep_translator import GoogleTranslator

SUPPORTED = {
    "en": "English",
    "tr": "Turkish",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ru": "Russian",
    "pt": "Portuguese",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
}


def translate(text, target):
    return GoogleTranslator(source="auto", target=target).translate(text)

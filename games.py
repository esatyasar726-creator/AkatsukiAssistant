import random

ANIME_IMAGES = [

    {
        "file": "images/guess_anime/bleach_1.jpg",
        "answer": "bleach"
    },

    {
        "file": "images/guess_anime/naruto_1.jpg",
        "answer": "naruto"
    },

    {
        "file": "images/guess_anime/onepiece_1.jpg",
        "answer": "one piece"
    },

    {
        "file": "images/guess_anime/jjk_1.jpg",
        "answer": "jujutsu kaisen"
    },

    {
        "file": "images/guess_anime/sololeveling_1.jpg",
        "answer": "solo leveling"
    }

]


def get_random_anime():
    return random.choice(ANIME_IMAGES)

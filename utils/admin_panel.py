ADMINS = [
    "Klaus",
    "Asta",
    "YurtSever",
    "Baba Yaga",
    "Jaco Tenma",
    "Mutoh"
]


def is_admin(username):
    if not username:
        return False

    return username in ADMINS

import random

# Hand-curated large trivia base of diverse categories
TRIVIA_QUESTIONS = {
    "Anime": [
        {"q": "What is the name of Ichigo Kurosaki's bankai?", "a": "tenza zangetsu"},
        {"q": "Who is the main protagonist of 'One Piece'?", "a": "monkey d luffy"},
        {"q": "What is the name of the ninja village where Naruto lives?", "a": "konoha"},
        {"q": "Which anime features characters named Light Yagami and L?", "a": "death note"},
        {"q": "What is the name of the giant armored humanoids in 'Attack on Titan'?", "a": "titans"},
        {"q": "Who is the 'Flame Hashira' in Demon Slayer?", "a": "kyojuro rengoku"},
        {"q": "In 'Bleach', what is Rukia Kuchiki's zanpakuto name?", "a": "sode no shirayuki"},
        {"q": "What is the name of the state alchemist protagonist in Fullmetal Alchemist?", "a": "edward elric"},
        {"q": "Which anime is about a virtual reality MMORPG where players are trapped?", "a": "sword art online"},
        {"q": "Who is the creator of the dragon balls in Dragon Ball Z?", "a": "kami"}
    ],
    "Bleach": [
        {"q": "Who is the Captain-Commander of the Gotei 13 at the start of Bleach?", "a": "genryusai yamamoto"},
        {"q": "What is the name of Aizen's illusions-producing Zanpakuto?", "a": "kyoka suigetsu"},
        {"q": "Which division does Shunsui Kyoraku captain initially?", "a": "8th division"},
        {"q": "What is the hollow mask form of Ichigo Kurosaki commonly called?", "a": "vasto lorde"},
        {"q": "What is the capital city of Hueco Mundo?", "a": "las noches"},
        {"q": "Who is the 4th Espada in Sosuke Aizen's army?", "a": "ulquiorra cifer"},
        {"q": "What is Kisuke Urahara's candy shop name?", "a": "urahara shop"},
        {"q": "Who is the captain of the 10th Division?", "a": "toshiro hitsugaya"},
        {"q": "Who is the lieutenant of the 6th Division under Byakuya?", "a": "renji abarai"},
        {"q": "What is the final Quincy form used by Uryu Ishida in Soul Society called?", "a": "letzt stil"}
    ],
    "Gaming": [
        {"q": "Which game features a hero named Link rescuing Princess Zelda?", "a": "the legend of zelda"},
        {"q": "What is the best-selling video game of all time?", "a": "minecraft"},
        {"q": "Which gaming franchise features the characters Master Chief and Cortana?", "a": "halo"},
        {"q": "What is the name of the fictional continent in 'The Witcher'?", "a": "the continent"},
        {"q": "Which game is known for the phrase 'Praise the Sun'?", "a": "dark souls"},
        {"q": "What is the name of Mario's green-clad twin brother?", "a": "luigi"},
        {"q": "Which battle royale game features 100 players jumping from a battle bus?", "a": "fortnite"},
        {"q": "What is the name of the main protagonist in GTA San Andreas?", "a": "carl johnson"},
        {"q": "Who is the Norse God of War in the 2018 PlayStation game?", "a": "kratos"},
        {"q": "Which game franchise features Vault Boy as its mascot?", "a": "fallout"}
    ],
    "Movies": [
        {"q": "Which movie features a spinning top that determines reality?", "a": "inception"},
        {"q": "Who directed the sci-fi epic 'Interstellar'?", "a": "christopher nolan"},
        {"q": "What is the highest-grossing movie of all time?", "a": "avatar"},
        {"q": "Which movie features the iconic character Jack Sparrow?", "a": "pirates of the caribbean"},
        {"q": "Who played the Joker in 'The Dark Knight'?", "a": "heath ledger"},
        {"q": "What is the name of the kingdom in Disney's 'Frozen'?", "a": "arendelle"},
        {"q": "Which film trilogy features Frodo Baggins and the One Ring?", "a": "the lord of the rings"},
        {"q": "What is the first movie in the Marvel Cinematic Universe?", "a": "iron man"},
        {"q": "Who is the main protagonist of the 'Matrix' trilogy?", "a": "neo"},
        {"q": "What is the name of the fictional African country in 'Black Panther'?", "a": "wakanda"}
    ],
    "Science": [
        {"q": "What is the chemical symbol for Gold?", "a": "au"},
        {"q": "What is the closest star to Earth?", "a": "the sun"},
        {"q": "What is the powerhouse of the cell?", "a": "mitochondria"},
        {"q": "What gas do plants absorb from the atmosphere?", "a": "carbon dioxide"},
        {"q": "How many bones are in the adult human body?", "a": "206"},
        {"q": "What is the speed of light in vacuum (approx in km/s)?", "a": "300000"},
        {"q": "What is the hardest natural substance on Earth?", "a": "diamond"},
        {"q": "Which planet is known as the Red Planet?", "a": "mars"},
        {"q": "Who formulated the theory of general relativity?", "a": "albert einstein"},
        {"q": "What is the chemical formula for water?", "a": "h2o"}
    ],
    "History": [
        {"q": "Who was the first President of the United States?", "a": "george washington"},
        {"q": "In which year did World War II end?", "a": "1945"},
        {"q": "Who was the French queen who famously said 'Let them eat cake'?", "a": "marie antoinette"},
        {"q": "Which ancient civilization built the Colosseum in Rome?", "a": "romans"},
        {"q": "Who was the leader of the Mongol Empire?", "a": "genghis khan"},
        {"q": "What ship sank on its maiden voyage in 1912?", "a": "titanic"},
        {"q": "Which civilization built the Great Pyramid of Giza?", "a": "egyptians"},
        {"q": "Who was the first emperor of the Roman Empire?", "a": "augustus"},
        {"q": "In which city was the Declaration of Independence signed?", "a": "philadelphia"},
        {"q": "Who was the British Prime Minister during World War II?", "a": "winston churchill"}
    ],
    "Geography": [
        {"q": "What is the capital of Japan?", "a": "tokyo"},
        {"q": "What is the largest ocean on Earth?", "a": "pacific ocean"},
        {"q": "Which river is the longest in the world?", "a": "nile river"},
        {"q": "What is the smallest country in the world?", "a": "vatican city"},
        {"q": "Which continent is home to the Sahara Desert?", "a": "africa"},
        {"q": "What is the capital of Turkey?", "a": "ankara"},
        {"q": "Which mountain range is Mount Everest part of?", "a": "himalayas"},
        {"q": "What is the capital of France?", "a": "paris"},
        {"q": "Which country has the largest land area?", "a": "russia"},
        {"q": "What is the capital of Turkey's neighbor, Greece?", "a": "athens"}
    ],
    "Sports": [
        {"q": "Which country won the FIFA World Cup in 2022?", "a": "argentina"},
        {"q": "How many players are on a soccer team on the field?", "a": "11"},
        {"q": "Who is known as the fastest man alive (runner)?", "a": "usain bolt"},
        {"q": "Which sport is played at Wimbledon?", "a": "tennis"},
        {"q": "What is the standard length of an Olympic swimming pool (meters)?", "a": "50"},
        {"q": "Who has won the most NBA MVP awards?", "a": "kareem abdul jabbar"},
        {"q": "Which country has won the most Olympic gold medals?", "a": "united states"},
        {"q": "In which sport can you get a strike or a spare?", "a": "bowling"},
        {"q": "How many points is a touchdown worth in American football?", "a": "6"},
        {"q": "Which sport uses terms like checkmate, castle, and pawn?", "a": "chess"}
    ],
    "Technology": [
        {"q": "Who co-founded Microsoft alongside Paul Allen?", "a": "bill gates"},
        {"q": "What does PDF stand for?", "a": "portable document format"},
        {"q": "Which company developed the Android mobile operating system?", "a": "google"},
        {"q": "What is the main operating system of Apple Mac computers?", "a": "macos"},
        {"q": "What does WWW stand for in a website URL?", "a": "world wide web"},
        {"q": "Which social media platform was originally called 'Twttr'?", "a": "twitter"},
        {"q": "What is the name of Apple's virtual assistant?", "a": "siri"},
        {"q": "Who is the CEO of SpaceX and Tesla?", "a": "elon musk"},
        {"q": "Which computer part is considered the 'brain' of the PC?", "a": "cpu"},
        {"q": "What year was the first iPhone released?", "a": "2007"}
    ],
    "Animals": [
        {"q": "What is the largest land mammal?", "a": "african elephant"},
        {"q": "What type of bird can fly backwards?", "a": "hummingbird"},
        {"q": "What is a group of lions called?", "a": "pride"},
        {"q": "Which mammal is known to have the most powerful bite?", "a": "hippopotamus"},
        {"q": "What is the fastest animal on land?", "a": "cheetah"},
        {"q": "How many hearts does an octopus have?", "a": "3"},
        {"q": "What is the only mammal capable of true flight?", "a": "bat"},
        {"q": "What is a baby kangaroo called?", "a": "joey"},
        {"q": "Which animal is known as the King of the Jungle?", "a": "lion"},
        {"q": "What is the largest species of shark?", "a": "whale shark"}
    ],
    "Food": [
        {"q": "What is the main ingredient in guacamole?", "a": "avocado"},
        {"q": "Which country is the origin of Pizza?", "a": "italy"},
        {"q": "What sweet substance is made by bees?", "a": "honey"},
        {"q": "What is the primary ingredient in hummus?", "a": "chickpeas"},
        {"q": "Which fruit is known as the King of Fruits in Asia and is very smelly?", "a": "durian"},
        {"q": "What drink is made from roasted and ground seeds?", "a": "coffee"},
        {"q": "What is the most popular grain in Asia?", "a": "rice"},
        {"q": "Which bakery item's name translates to 'twice-baked' in Latin?", "a": "biscuit"},
        {"q": "What is the main ingredient of traditional tofu?", "a": "soybeans"},
        {"q": "What is dried plum called?", "a": "prune"}
    ],
    "Music": [
        {"q": "Who is known as the King of Pop?", "a": "michael jackson"},
        {"q": "Which English rock band sang 'Hey Jude' and 'Let It Be'?", "a": "the beatles"},
        {"q": "Who is the singer of 'Bad Romance'?", "a": "lady gaga"},
        {"q": "How many strings are on a standard violin?", "a": "4"},
        {"q": "Who sang the smash hit 'Shape of You'?", "a": "ed sheeran"},
        {"q": "Which musical instrument has black and white keys?", "a": "piano"},
        {"q": "What is the name of Queen's legendary lead vocalist?", "a": "freddie mercury"},
        {"q": "Who is the composer of the 9th Symphony (Ode to Joy)?", "a": "beethoven"},
        {"q": "Which pop star sang 'Shake It Off'?", "a": "taylor swift"},
        {"q": "Who is the legendary king of rock and roll?", "a": "elvis presley"}
    ],
    "Cars": [
        {"q": "Which company makes the Model S electric car?", "a": "tesla"},
        {"q": "What country is the home of Toyota and Honda?", "a": "japan"},
        {"q": "Which Italian luxury brand has a prancing horse logo?", "a": "ferrari"},
        {"q": "What company manufactures the Mustang?", "a": "ford"},
        {"q": "What country is Porsche and Audi from?", "a": "germany"},
        {"q": "Which company makes the Civic?", "a": "honda"},
        {"q": "What is the name of Chevrolet's famous sports car?", "a": "corvette"},
        {"q": "Which brand has a trident as its logo?", "a": "maserati"},
        {"q": "What company has four interlocking rings as its logo?", "a": "audi"},
        {"q": "What car company makes the Prius?", "a": "toyota"}
    ],
    "Programming": [
        {"q": "Which programming language was named after a British comedy troupe?", "a": "python"},
        {"q": "What does HTML stand for?", "a": "hypertext markup language"},
        {"q": "Who created the Python programming language?", "a": "guido van rossum"},
        {"q": "What is the standard query language used for database management?", "a": "sql"},
        {"q": "What does CSS stand for in web development?", "a": "cascading style sheets"},
        {"q": "Which data structure follows the Last In, First Out (LIFO) model?", "a": "stack"},
        {"q": "What is the binary representation of the decimal number 5?", "a": "101"},
        {"q": "What keyword is used to define a function in Python?", "a": "def"},
        {"q": "What company originally developed the Java language?", "a": "sun microsystems"},
        {"q": "In Python, which list method adds an element to the end of the list?", "a": "append"}
    ],
    "Mathematics": [
        {"q": "What is the square root of 144?", "a": "12"},
        {"q": "What is the value of Pi rounded to two decimal places?", "a": "3.14"},
        {"q": "What is the sum of angles in a triangle (degrees)?", "a": "180"},
        {"q": "What is 7 multiplied by 8?", "a": "56"},
        {"q": "What is 15% of 200?", "a": "30"},
        {"q": "What is the only even prime number?", "a": "2"},
        {"q": "What is the value of 5 factorial (5!)?", "a": "120"},
        {"q": "What shape is a standard stop sign?", "a": "octagon"},
        {"q": "What is the perimeter of a square with side length 6?", "a": "24"},
        {"q": "What is 99 divided by 9?", "a": "11"}
    ],
    "General Knowledge": [
        {"q": "What is the tallest mountain on Earth?", "a": "mount everest"},
        {"q": "How many days are in a leap year?", "a": "366"},
        {"q": "Who wrote the play 'Romeo and Juliet'?", "a": "william shakespeare"},
        {"q": "What is the primary language spoken in Brazil?", "a": "portuguese"},
        {"q": "Which color is created by mixing blue and yellow?", "a": "green"},
        {"q": "How many colors are in a rainbow?", "a": "7"},
        {"q": "What is the name of the currency used in Japan?", "a": "yen"},
        {"q": "What is the largest desert in the world?", "a": "antarctica"},
        {"q": "What pigment gives leaves their green color?", "a": "chlorophyll"},
        {"q": "Who painted the famous 'Mona Lisa'?", "a": "leonardo da vinci"}
    ],
    "Memes": [
        {"q": "What dog breed is featured in the 'Doge' meme?", "a": "shiba inu"},
        {"q": "What are you not supposed to do on Wednesdays in 'Mean Girls'?", "a": "wear pink"},
        {"q": "Who is the grumpy cat's real name?", "a": "tardar sauce"},
        {"q": "What meme features a man looking back at another girl?", "a": "distracted boyfriend"},
        {"q": "What cartoon character shrugs in a yellow coat and has a giant grin?", "a": "spongebob"},
        {"q": "Who says 'One does not simply walk into Mordor'?", "a": "boromir"},
        {"q": "What type of food is associated with 'Nyan Cat'?", "a": "pop tart"},
        {"q": "What meme features a yellow cartoon dog in a burning room?", "a": "this is fine"},
        {"q": "Who is the singer of the classic rickroll song 'Never Gonna Give You Up'?", "a": "rick astley"},
        {"q": "Which green ogre is highly celebrated in swamp memes?", "a": "shrek"}
    ],
    "Internet": [
        {"q": "What is the most popular video sharing website?", "a": "youtube"},
        {"q": "What does IP stand for in IP address?", "a": "internet protocol"},
        {"q": "What is the name of Google's web browser?", "a": "chrome"},
        {"q": "Which service lets you register .com domain names?", "a": "godaddy"},
        {"q": "What is the name of the internet's most popular forum site?", "a": "reddit"},
        {"q": "What protocol secures web communications (has an 'S' at the end)?", "a": "https"},
        {"q": "Which chat platform is highly popular among gamers and bot developers?", "a": "discord"},
        {"q": "What is the term for a local wireless network?", "a": "wi-fi"},
        {"q": "What year did the World Wide Web become public?", "a": "1991"},
        {"q": "What is the name of the primary domain registry for the internet?", "a": "iana"}
    ]
}

# Infinite procedural question generators
def generate_math_question():
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    op = random.choice(['+', '-', '*'])
    if op == '+':
        ans = a + b
    elif op == '-':
        ans = a - b
    else:
        a = random.randint(1, 15)
        b = random.randint(1, 15)
        ans = a * b
    return f"Calculate: {a} {op} {b}", str(ans)

def generate_geography_question():
    capitals = {
        "turkey": "ankara", "japan": "tokyo", "france": "paris", "germany": "berlin",
        "united kingdom": "london", "italy": "rome", "spain": "madrid", "canada": "ottawa",
        "united states": "washington", "australia": "canberra", "china": "beijing",
        "brazil": "brasilia", "egypt": "cairo", "greece": "athens", "india": "new delhi"
    }
    country = random.choice(list(capitals.keys()))
    return f"What is the capital of {country.title()}?", capitals[country]

def get_random_question(category=None):
    if not category:
        category = random.choice(list(TRIVIA_QUESTIONS.keys()) + ["MathProcedural", "GeoProcedural"])

    if category == "MathProcedural":
        return generate_math_question()
    elif category == "GeoProcedural":
        return generate_geography_question()

    q_list = TRIVIA_QUESTIONS.get(category, TRIVIA_QUESTIONS["General Knowledge"])
    item = random.choice(q_list)
    return item["q"], item["a"]

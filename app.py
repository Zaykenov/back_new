import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from psycopg2 import extras

load_dotenv()
app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)
CORS(app)

@app.route("/")  # Define the root route
def home():
    return "Welcome to the Customer API!"

@app.get("/api/user/<string:user_name>")
def get_user(user_name):
    try:
        with connection.cursor() as cursor:
            # Execute the SQL query to fetch the user by UserName
            cursor.execute("SELECT * FROM Users WHERE UserName = %s", (user_name,))
            user = cursor.fetchone()

        # Check if a user was found
        if user:
            user_dict = {
                "UserID": user[0],
                "UserName": user[1]
            }
            return jsonify(user_dict), 200
        else:
            return jsonify({"message": "User not found"}), 404
    finally:
        pass

@app.get("/api/grammar")
def get_grammar():
    data = {
        "levels": {
            "easy": {
                "text": "В казахском языке стандартный порядок слов — подлежащее (S), сказуемое (V) и дополнение (O). Например, \"Мен қалам сатып алдым\" (Я купил ручку), где \"Мен\" — подлежащее, \"сатып алдым\" — сказуемое, а \"қалам\" — дополнение.",
                "questions": [
                    {
                        "question": "Какой порядок слов в казахском предложении?",
                        "options": ["VSO", "SOV", "OSV", "SVO"],
                        "correct_option": 3
                    },
                    {
                        "question": "Что означает \"Мен\" в предложении \"Мен қалам сатып алдым\"?",
                        "options": ["Ручка", "Я", "Купил", "И"],
                        "correct_option": 1
                    },
                    {
                        "question": "Какая часть речи \"сатып алдым\"?",
                        "options": ["Подлежащее", "Дополнение", "Сказуемое", "Прилагательное"],
                        "correct_option": 2
                    }
                ],
                "fill_in_gaps": [
                    {
                        "first_part": "",
                        "last_part": "кітап оқимын",
                        "options": ["Оқимын кітап", "Кітап оқимын", "Мен кітап оқимын", "Оқимын мен кітап"],
                        "correct_option": 2
                    }
                ]
            },
            "medium": {
                "text": "Существительные в казахском языке имеют единственное и множественное число. Множественное число обычно формируется добавлением суффикса -лар (-лер), например, \"қалам\" (ручка) становится \"қаламдар\" (ручки).",
                "questions": [
                    {
                        "question": "Какой суффикс используется для образования множественного числа существительных?",
                        "options": ["-мен", "-тен", "-лар / -лер", "-дан"],
                        "correct_option": 2
                    },
                    {
                        "question": "Что означает слово \"қаламдар\"?",
                        "options": ["Ручки", "Книги", "Школы", "Столы"],
                        "correct_option": 0
                    },
                    {
                        "question": "Как переводится на русский \"иттер\"?",
                        "options": ["Коты", "Лошади", "Собаки", "Птицы"],
                        "correct_option": 2
                    }
                ],
                "fill_in_gaps": [
                    {
                        "first_part": "Біз ",
                        "last_part": " сатып алдық",
                        "options": ["алма", "алманы", "алмалар", "алмамен"],
                        "correct_option": 2
                    }
                ]
            },
            "hard": {
                "text": "Глаголы в казахском языке спрягаются по временам. Для прошедшего времени к корню глагола добавляются суффиксы, например, \"жазу\" (писать) становится \"жазды\" (он написал).",
                "questions": [
                    {
                        "question": "Какой суффикс добавляется к глаголу \"жазу\" для образования прошедшего времени в третьем лице?",
                        "options": ["-ды", "-ді", "-ты", "-ті"],
                        "correct_option": 0
                    },
                    {
                        "question": "Как будет \"читать\" в прошедшем времени для первого лица единственного числа?",
                        "options": ["Оқиды", "Оқыдым", "Оқылады", "Оқытым"],
                        "correct_option": 1
                    },
                    {
                        "question": "Что означает \"сөйледі\"?",
                        "options": ["Говорит", "Слушал", "Сказал", "Пойдет"],
                        "correct_option": 2
                    }
                ],
                "fill_in_gaps": [
                    {
                        "first_part": "Ол кеше мектепке ",
                        "last_part": "",
                        "options": ["барады", "барды", "бар", "баратын"],
                        "correct_option": 1
                    }
                ]
            }
        }
    }
    return jsonify(data)
@app.get("/api/speaking")
def get_speaking():
    speaking_data = {}

    try:
        with connection.cursor(cursor_factory=extras.DictCursor) as cursor:  # Using DictCursor
            cursor.execute("SELECT * FROM LanguageLearning ORDER BY level, id;")
            results = cursor.fetchall()
            
            for record in results:
                level = record['level']
                if level not in speaking_data:
                    speaking_data[level] = []
                
                speaking_data[level].append({
                    "Word": record['word'],
                    "Word translation": record['word_translation'],
                    "Sentence": record['sentence'],
                    "Sentence translation": record['sentence_translation'],
                    "Audio Source Word": record['audio_source_word'],
                    "Audio Source Sentence": record['audio_source_sentence']
                })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if speaking_data:
        return jsonify(speaking_data), 200
    else:
        return jsonify({"message": "Speaking content not found"}), 404

@app.get("/api/reading")
def get_reading():
    # Initialize the dictionary to hold the entire reading structure
    reading_data = {
        "reading": {
            "levels": {
                "easy": [],
                "medium": [],
                "hard": []
            }
        }
    }

    try:
        with connection.cursor() as cursor:
            # Execute the new simplified SQL query
            cursor.execute("""
                SELECT t.level, t.text, q.question, q.option1, q.option2, q.option3, q.option4, q.correct_option
                FROM ReadingTexts t
                JOIN ReadingQuestions q ON t.id = q.text_id
                ORDER BY t.level, t.id, q.id;
            """)
            results = cursor.fetchall()

            # Process fetched data
            for level, text, question, option1, option2, option3, option4, correct_option in results:
                # Ensure each level is represented in the dictionary, dynamically adjust to data
                if level not in reading_data["reading"]["levels"]:
                    reading_data["reading"]["levels"][level] = []

                # Append the text and its questions directly
                reading_data["reading"]["levels"][level].append({
                    "text": text,
                    "questions": [{
                        "question": question,
                        "options": [option1, option2, option3, option4],
                        "correct_option": correct_option
                    }]
                })

    except Exception as e:
        # Handle potential errors in execution
        return jsonify({"error": str(e)}), 500

    # Check if any data was added and respond accordingly
    if any(reading_data["reading"]["levels"][level] for level in ["easy", "medium", "hard"]):
        return jsonify(reading_data), 200
    else:
        return jsonify({"message": "Reading content not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
if __name__ == "__main__":
    app.run(debug=True)




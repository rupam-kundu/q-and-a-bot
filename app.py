from flask import Flask
from q_and_a import ask

app = Flask(__name__)

@app.route("/")
def health_check():
    return "OK"

@app.route(f"/answer_question")
def answer_question():
    try:
        answer_question_response = ask('What is aging?')
        return answer_question_response
    except Exception as e:
        return str(e)
    
if __name__ == '__main__':
    app.run(debug=True)

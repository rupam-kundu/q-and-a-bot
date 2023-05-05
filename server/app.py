from flask import Flask, request
from flask_cors import CORS, cross_origin
from q_and_a import ask

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route("/")
def health_check():
    return "OK"

@app.route(f"/answer_question", methods=["POST"])
@cross_origin(supports_credentials=True)
def answer_question():
    try:
        params = request.get_json()
        question = params["question"]
        answer_question_response = ask(question)
        return answer_question_response
    except Exception as e:
        return str(e)
    
if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request
from flask_cors import CORS, cross_origin
from q_and_a import ask

application = Flask(__name__)
CORS(application, supports_credentials=True)

@application.route("/")
def health_check():
    return "OK"

@application.route(f"/answer_question", methods=["POST"])
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
    # application.run(debug=True)
    application.run()

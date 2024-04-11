from flask import Flask, request, jsonify
from chat_module.qa_chatbot import answer_q

app = Flask(__name__)

@app.route('/chat', methods=['POST'])  # POST 메소드 지정
def chat():
    #load_model()
    app.config['JSON_AS_ASCII'] = False
    user_chat = request.json['request']  # JSON 데이터에서 user_chat 키의 값을 추출
    response = answer_q(user_chat)
    return jsonify(response)  # JSON 형식으로 응답

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# flask run --host=0.0.0.0 --port=5000
# 192.168.0.13
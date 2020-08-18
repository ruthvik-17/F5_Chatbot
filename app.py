from chat import ChatBot

from flask import Flask, render_template, request

app = Flask(__name__)
app.static_folder = 'static'

chat_instance = ChatBot()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    user_msg = request.args.get('msg')
    response = chat_instance.get_response(user_msg)
    result = ""
    for each in response:
        result += each[0] + '\n'
    # return result + str(response)
    return result


if __name__ == "__main__":
    app.run()

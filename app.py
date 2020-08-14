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
    return str(chat_instance.get_response(user_msg))


if __name__ == "__main__":
    app.run()

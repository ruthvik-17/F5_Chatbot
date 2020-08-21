from chat import ChatBot
from collections import OrderedDict
from flask import Flask, render_template, request

app = Flask(__name__)
app.static_folder = 'static'
app.config['JSON_SORT_KEYS'] = False

chat_instance = ChatBot()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    user_msg = request.args.get('msg')
    browser = request.user_agent.browser
    response = chat_instance.get_response(user_msg, browser)
    return OrderedDict(response)


if __name__ == "__main__":
    app.run()

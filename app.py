from chat import ChatBot
from collections import OrderedDict
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.static_folder = 'static'
app.config['JSON_SORT_KEYS'] = False

chat_instance = ChatBot()


@app.route("/")
# @app.route('//<name>')
def home(command="start"):
    # if chat_instance.db[browser]["name"]:
    #     greet_msg = "Hello " + chat_instance.db[browser]["name"] + "! What brings you back?"
    # else:
    #     greet_msg = "Hello! How can I help you?"
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    browser = request.user_agent.browser
    chat_instance.initialize(browser)
    user_msg = request.args.get('msg')
    command = request.args.get('command')
    response = chat_instance.get_response(user_msg, browser, command)
    return OrderedDict(response)


@app.route("/get_greet_msg", methods=['POST'])
def get_greet_msg():
    browser = request.user_agent.browser
    if request.method == 'POST':
        return jsonify(chat_instance.get_response("", browser, "start")[0][0])


if __name__ == "__main__":
    app.run()

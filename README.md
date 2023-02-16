# F5_Chatbot
An experimental chatbot for F5 Networks.

### About the project:
Chatbot built with intent detection, question answering, and spell correction capabilities packed with
a GUI to be able to run on a local machine.

### Commands to test:
1. Clone this repository:
```
git clone https://github.com/ruthvik-17/F5_Chatbot.git
```
2. Create a new Venv(recommended) in your virtual environments folder:
```
pip install virtualenv
virtualenv f5_bot_venv
```
3. Activate Venv:
```
f5_bot_venv\Scripts\activate
```
4. Install requirements:
```
pip install -r requirements.txt
```
5. Download, unzip and add en.pkl (Spell correction model) to the project directory
**language**|**model**|**size**|**md5 hash**
    :-----:|:-----:|:-----:|:-----:
    en|[en.pkl.zip](https://haptik-website-images.haptik.ai/spello\_models/en.pkl.zip)|84M|ec55760a7e25846bafe90b0c9ce9b09f
6.  Move to project directory in cmd:
```
cd F5_Chatbot
```
7. Run app.py:
```
python app.py
```
8. Test the chatbot on:
```
http://127.0.0.1:5000/
```

Type `stop/exit` to exit from the chatbot.

#
### Opensource Credits (Go give them a ⭐):
#### Spello: https://github.com/hellohaptik/spello
#### Spello Authors: [Aman](https://github.com/amansrivastava17) , [Ruthvik](https://github.com/ruthvik-17)

.

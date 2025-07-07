# src/server.py
from flask import Flask
from controller import main_loop

app = Flask(__name__)
_loop = None

@app.route('/start', methods=['POST'])
def start():
    global _loop
    if _loop is None:
        _loop = main_loop()    # you may need threading here
    return "Started", 200

@app.route('/stop', methods=['POST'])
def stop():
    # signal main_loop to exit (e.g. set a global flag)
    return "Stopped", 200

if __name__ == "__main__":
    app.run(port=3000)

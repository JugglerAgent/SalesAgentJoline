from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from the minimal Flask app! If you can see this, the basic setup is working."

@app.route('/test')
def test():
    return "This is a test route. If you can see this, routing is working correctly."

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-development')

@app.route('/')
def index():
    return render_template('index.html')

def main():
    app.run(
        debug=os.environ.get('FLASK_DEBUG', 'true').lower() == 'true',
        host=os.environ.get('FLASK_HOST', '127.0.0.1'),
        port=int(os.environ.get('FLASK_PORT', 5000))
    )

if __name__ == "__main__":
    main()

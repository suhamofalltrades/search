import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    template_path = os.path.join(app.template_folder, "index.html")
    print("Looking for template at:", template_path)
    print("Templates available:", os.listdir(app.template_folder))
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)

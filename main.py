from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "HEAD"])
def home():
    if request.method == "HEAD":
        return "", 200  # Empty response for HEAD requests
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's assigned port or default
    app.run(host="0.0.0.0", port=port)

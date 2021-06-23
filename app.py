# Imports from Flask
from flask import Flask, render_template, abort

# Initialize flask application
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

# Run application with debug console
if __name__ == "__main__":
    """ """
    app.run(debug=True, host="0.0.0.0", port=3000)
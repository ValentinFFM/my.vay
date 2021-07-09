# The run file is responsible for running the application, which is imported from the __init_-.py
from my_vay import app

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=3000)

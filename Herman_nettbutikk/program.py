from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('Homepage.html')

@app.route('/Produkter')
def produkter():
    return render_template('Produkter.html')

if __name__ == '__main__':
    app.run(debug=True)
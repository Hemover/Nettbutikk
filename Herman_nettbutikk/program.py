from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
import mariadb
from flask import session
from flask import abort

app = Flask(__name__)
app.secret_key = "super-hemmelig-nøkkel-123"
bcrypt = Bcrypt(app)



@app.route('/')
def homepage():
    return render_template('Homepage.html')

@app.route('/Produkter')
def produkter():
    return render_template('Produkter.html')



# Database-tilkobling
def get_db():
    return mariadb.connect(
        user="db_user",
        password="SlippMeg1nn!",
        host="localhost",
        port=3306,
        database="nettbutikk"
    )


@app.route("/Register", methods=["GET", "POST"])
def opprett_bruker():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            cur.close()
            conn.close()

            flash("Bruker opprettet! Du kan nå logge inn.", "success")
            return redirect(url_for("opprett_bruker"))

        except mariadb.Error as e:
            flash("Brukernavn eller e-post finnes allerede.", "error")

    return render_template("Register.html")

@app.route("/Login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form["username"]
        password = request.form["password"]

        try:
            conn = get_db()
            cur = conn.cursor(dictionary=True)

            cur.execute(
                "SELECT * FROM users WHERE username = ? OR email = ?",
                (username_or_email, username_or_email)
            )

            user = cur.fetchone()
            cur.close()
            conn.close()

            if user and bcrypt.check_password_hash(user["password_hash"], password):
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["cart"] = []
                flash("Du er nå logget inn!", "success")
                return redirect(url_for("homepage"))
            else:
                flash("Feil brukernavn/e-post eller passord", "error")

        except mariadb.Error as e:
            flash(f"Databasefeil: {e}", "error")

    return render_template("Login.html")

@app.context_processor
def inject_user():
    cart = session.get("cart", [])
    return dict(
        logged_in="user_id" in session,
        username=session.get("username"),
        cart_count=len(cart)
    )

@app.route("/logout")
def logout():
    session.clear()
    flash("Du er logget ut", "success")
    return redirect(url_for("homepage"))

@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):
    if "user_id" not in session:
        flash("Du må være logget inn for å bruke handlekurven", "error")
        return redirect(url_for("login"))

    cart = session.get("cart", [])
    cart.append(product_id)
    session["cart"] = cart

    flash("Produkt lagt i handlekurven", "success")
    return redirect(url_for("produkter"))

@app.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cart = session.get("cart", [])
    return render_template("Cart.html", cart=cart)

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=5000)
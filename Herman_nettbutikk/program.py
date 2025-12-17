from flask import Flask, render_template
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


@app.route("/Produkter")
def produkter():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("Produkter.html", products=products)



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
                session["cart"] = {}
                flash("Du er nå logget inn!", "success")
                return redirect(url_for("homepage"))
            else:
                flash("Feil brukernavn/e-post eller passord", "error")

        except mariadb.Error as e:
            flash(f"Databasefeil: {e}", "error")

    return render_template("Login.html")

@app.context_processor
def inject_user():
    cart_count = 0

    if "user_id" in session:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT SUM(quantity) FROM cart WHERE user_id = ?",
            (session["user_id"],)
        )
        result = cur.fetchone()
        cart_count = result[0] or 0
        cur.close()
        conn.close()

    return dict(
        logged_in="user_id" in session,
        username=session.get("username"),
        cart_count=cart_count
    )

@app.route("/logout")
def logout():
    session.clear()
    flash("Du er logget ut", "success")
    return redirect(url_for("homepage"))

@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    if "user_id" not in session:
        flash("Du må være logget inn", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    product_id = int(request.form["product_id"])

    conn = get_db()
    cur = conn.cursor()

    # Sjekk om produktet allerede er i handlekurven
    cur.execute(
        "SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?",
        (user_id, product_id)
    )
    item = cur.fetchone()

    if item:
        cur.execute(
            "UPDATE cart SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?",
            (user_id, product_id)
        )
    else:
        cur.execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, 1)",
            (user_id, product_id)
        )

    conn.commit()
    cur.close()
    conn.close()

    flash("Produkt lagt i handlekurven", "success")
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            p.id,
            p.name,
            p.price,
            c.quantity,
            (p.price * c.quantity) AS total_price
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    """, (user_id,))

    items = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("Cart.html", items=items)


@app.route("/checkout", methods=["POST"])
def checkout():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # Hent handlekurv
    cur.execute("""
        SELECT c.product_id, c.quantity, p.price, p.stock
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    """, (user_id,))
    items = cur.fetchall()

    if not items:
        flash("Handlekurven er tom", "error")
        return redirect(url_for("cart"))

    # Lager-sjekk
    for item in items:
        if item["quantity"] > item["stock"]:
            flash("Ikke nok på lager", "error")
            return redirect(url_for("cart"))

    # Totalpris
    total_price = sum(item["quantity"] * item["price"] for item in items)

    # ➕ Opprett ordre
    cur.execute("""
        INSERT INTO orders (user_id, total_price)
        VALUES (?, ?)
    """, (user_id, total_price))

    order_id = cur.lastrowid 

    # Trekk lager
    for item in items:
        cur.execute("""
            UPDATE products
            SET stock = stock - ?
            WHERE id = ?
        """, (item["quantity"], item["product_id"]))

        # order_items (hvis du har den tabellen)
        cur.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (order_id, item["product_id"], item["quantity"], item["price"]))

    # Tøm handlekurv
    cur.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))

    conn.commit()
    cur.close()
    conn.close()

    #sender order til templaten
    return render_template(
        "OrderConfirmation.html",
        order={"id": order_id, "total": total_price}
    )

@app.route("/order/<int:order_id>")
def order_confirmation(order_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT o.id, o.total, o.created_at
        FROM orders o
        WHERE o.id = ? AND o.user_id = ?
    """, (order_id, session["user_id"]))

    order = cur.fetchone()

    cur.execute("""
        SELECT 
            p.name,
            oi.quantity,
            oi.price,
            (oi.quantity * oi.price) AS total
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    """, (order_id,))

    items = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "OrderConfirmation.html",
        order=order,
        items=items
    )

@app.route("/cart/decrease/<int:product_id>", methods=["POST"])
def decrease_quantity(product_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor()

    # Reduser antall
    cur.execute("""
        UPDATE cart
        SET quantity = quantity - 1
        WHERE user_id = ? AND product_id = ?
    """, (user_id, product_id))

    # Fjern hvis quantity blir 0
    cur.execute("""
        DELETE FROM cart
        WHERE user_id = ? AND product_id = ? AND quantity <= 0
    """, (user_id, product_id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("cart"))

@app.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM cart WHERE user_id = ? AND product_id = ?",
        (session["user_id"], product_id)
    )

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("cart"))

@app.route("/cart/increase/<int:product_id>", methods=["POST"])
def increase_quantity(product_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # Hent lager
    cur.execute(
        "SELECT stock FROM products WHERE id = ?",
        (product_id,)
    )
    product = cur.fetchone()

    # Hent antall i handlekurv
    cur.execute(
        "SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?",
        (user_id, product_id)
    )
    cart_item = cur.fetchone()

    if not product or not cart_item:
        return redirect(url_for("cart"))

    # Sperre
    if cart_item["quantity"] >= product["stock"]:
        flash("Du kan ikke legge til flere enn det som er på lager", "error")
        return redirect(url_for("cart"))

    # Øk antall
    cur.execute("""
        UPDATE cart
        SET quantity = quantity + 1
        WHERE user_id = ? AND product_id = ?
    """, (user_id, product_id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("cart"))


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=5000)
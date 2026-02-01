from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "lostandfound123"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Radhika1@",
    database="lostfound"
)
cursor = db.cursor(buffered=True)
def reconnect_db():
    global db, cursor
    if not db.is_connected():
        db.reconnect(attempts=3, delay=2)
        cursor = db.cursor(buffered=True)


# ---------------- LOGIN PAGE ----------------
@app.route("/")
def login_page():
    return render_template("index.html")

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")

            print("SIGNUP DATA:", name, email, password)

            query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
            values = (name, email, password)

            cursor.execute(query, values)
            db.commit()

            print("DATA INSERTED SUCCESSFULLY")

            return redirect(url_for("login_page"))

        except Exception as e:
            return f"ERROR: {e}"

    return render_template("signup.html")


# ---------------- LOGIN LOGIC ----------------
@app.route("/login", methods=["GET", "POST"])
def login_user():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        query = "SELECT * FROM users WHERE email=%s AND password=%s"
        values = (email, password)

        cursor.execute(query, values)
        user = cursor.fetchone()

        if user:
            session["user"] = user[0]
            session["name"] = user[1]  
            # ✅ ADMIN CHECK
            if user[1] == "admin":
                session["is_admin"] = True
            else:
                session["is_admin"] = False

            return redirect(url_for("dashboard"))
        else:
            return "INVALID EMAIL OR PASSWORD"

    return render_template("index.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        
        return render_template("login_again.html")
    return render_template("stu_dash.html",user=session.get("name"))

@app.route("/logout")
def logout():
    session.pop("user", None)   # remove user session
    session["logged_out"] = True
    return redirect(url_for("login_page"))

@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/view_lost")
def view_lost():
    if "user" not in session:
        return redirect(url_for("login_page"))

    cursor.execute("SELECT * FROM lost_items")
    items = cursor.fetchall()

    return render_template("view_lost.html", items=items)

@app.route("/view_found")
def view_found():
    if "user" not in session:
        return redirect(url_for("login_page"))

    cursor.execute("SELECT * FROM found_items")
    items = cursor.fetchall()

    return render_template("view_found.html", items=items)

@app.route("/report_lost", methods=["GET", "POST"])
def report_lost():
    if "user" not in session:
        return redirect(url_for("login_page"))

    if request.method == "POST":
        item_name = request.form["item_name"]
        description = request.form["description"]
        lost_location = request.form["lost_location"]
        date_lost = request.form["date_lost"]
        contact = request.form["contact"]
        reported_by = session.get("name")

        query = """
        INSERT INTO lost_items
        (item_name, description, lost_location, date_lost, contact, reported_by)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            item_name, description,lost_location,
            date_lost, contact, reported_by
        ))
        db.commit()

        return redirect(url_for("dashboard"))


    return render_template("report_lost.html")

@app.route("/report_found", methods=["GET", "POST"])
def report_found():
    if "user" not in session:
        return redirect(url_for("login_page"))

    if request.method == "POST":
        item_name = request.form["item_name"]
        description = request.form["description"]
        found_location = request.form["found_location"]
        date_found = request.form["date_found"]
        contact = request.form["contact"]
        reported_by = session.get("name")

        query = """
        INSERT INTO found_items
        (item_name, description, found_location, date_found, contact, reported_by)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            item_name, description,found_location,
            date_found, contact, reported_by
        ))
        db.commit()

        return redirect(url_for("dashboard"))


    return render_template("report_found.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    reconnect_db()
    
    cursor.execute("SELECT * FROM lost_items")
    lost_items = cursor.fetchall()

    cursor.execute("SELECT * FROM found_items")
    found_items = cursor.fetchall()

    return render_template(
        "admin_dash.html",
        lost_items=lost_items,
        found_items=found_items
    )
@app.route("/delete_lost/<int:id>")
def delete_lost(id):
    reconnect_db()
    cursor.execute("DELETE FROM lost_items WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for("admin_dashboard"))


@app.route("/delete_found/<int:id>")
def delete_found(id):
    reconnect_db()
    cursor.execute("DELETE FROM found_items WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    app.run(debug=True)

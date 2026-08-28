from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "health-insurance-secret-key"


def get_db():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        connection = get_db()

        try:
            connection.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )

            connection.commit()
            connection.close()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            connection.close()
            return "Email already registered!"

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db()

        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("dashboard"))

        return "Invalid email or password!"

    return render_template("login.html")


# ---------------- USER DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        name=session["user_name"]
    )


# ---------------- SUBMIT CLAIM ----------------

@app.route("/submit-claim", methods=["GET", "POST"])
def submit_claim():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        policy_id = request.form["policy_id"]
        claim_amount = request.form["claim_amount"]
        reason = request.form["reason"]

        connection = get_db()

        connection.execute(
            """
            INSERT INTO claims
            (user_id, policy_id, claim_amount, reason, claim_date)
            VALUES (?, ?, ?, ?, date('now'))
            """,
            (
                session["user_id"],
                policy_id,
                claim_amount,
                reason
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("my_claims"))

    return render_template("submit_claim.html")


# ---------------- MY CLAIMS ----------------

@app.route("/my-claims")
def my_claims():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()

    claims = connection.execute(
        """
        SELECT *
        FROM claims
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "my_claims.html",
        claims=claims
    )


# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin")
def admin_dashboard():

    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    connection = get_db()

    claims = connection.execute(
        """
        SELECT
            claims.id,
            users.name,
            users.email,
            claims.policy_id,
            claims.claim_amount,
            claims.reason,
            claims.claim_date,
            claims.status
        FROM claims
        JOIN users ON claims.user_id = users.id
        ORDER BY claims.id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin_dashboard.html",
        claims=claims
    )


# ---------------- APPROVE CLAIM ----------------

@app.route("/approve/<int:claim_id>")
def approve_claim(claim_id):

    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    connection = get_db()

    connection.execute(
        "UPDATE claims SET status = 'Approved' WHERE id = ?",
        (claim_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("admin_dashboard"))


# ---------------- REJECT CLAIM ----------------

@app.route("/reject/<int:claim_id>")
def reject_claim(claim_id):

    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    connection = get_db()

    connection.execute(
        "UPDATE claims SET status = 'Rejected' WHERE id = ?",
        (claim_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("admin_dashboard"))


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
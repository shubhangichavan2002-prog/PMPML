from flask import Flask, render_template, request, redirect, url_for, session
import random
import datetime
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ---------------- Database Connection ----------------
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",        
        user="root",             #  MySQL username
        password="1624",         #  MySQL password
        database="userdb"        #  database name
    )
    return conn

# ---------------- Index ----------------
@app.route("/")
def index():
    return redirect(url_for("login"))

# ---------------- Registration ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                           (username, email, password))
            conn.commit()
        except mysql.connector.IntegrityError:
            return "User already exists! Try another username or email."
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("login"))
    return render_template("register.html")


# ---------------- Login ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return "Invalid credentials!"
    return render_template("login.html")

# ---------------- Home Page ----------------
@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("home.html")
## ---------------- Ticket Form ----------------
@app.route("/ticket_form", methods=["GET", "POST"])
def ticket_form():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all stops to show in the form
    cursor.execute("SELECT stop_id, stop_name FROM stop")
    stops = cursor.fetchall()

    # Fetch all routes to show in the form (optional)
    cursor.execute("SELECT route_id, route_name FROM route")
    routes = cursor.fetchall()

    cursor.close()
    conn.close()

    if request.method == "POST":
        route_id = request.form["route"]
        source_stop_id = request.form["source"]
        destination_stop_id = request.form["destination"]
        amount = request.form["amount"]

        # Fetch destination GPS
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT latitude, longitude FROM stop WHERE stop_id=%s",
            (destination_stop_id,)
        )
        dest = cursor.fetchone()
        if not dest:
            cursor.close()
            conn.close()
            return "Invalid destination selected"

        
        cursor.execute(
            "SELECT * FROM route_stop WHERE route_id=%s AND stop_id=%s",
            (route_id, destination_stop_id)
        )
        valid_stop = cursor.fetchone()
        if not valid_stop:
            cursor.close()
            conn.close()
            return "Destination stop not on selected route"

        cursor.close()
        conn.close()

        # Create ticket
        ticket = {
            "id": "TICKET" + str(random.randint(1000, 9999)),
            "route_id": route_id,
            "source_stop_id": source_stop_id,
            "destination_stop_id": destination_stop_id,
            "dest_lat": dest["latitude"],
            "dest_lng": dest["longitude"],
            "amount": amount,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        tickets = session.get("tickets", [])
        tickets.append(ticket)
        session["tickets"] = tickets

        return redirect(url_for("view_ticket"))

    return render_template("ticket_form.html", stops=stops, routes=routes)
# ---------------- Get stops for a particular route ----------------
@app.route("/get_route_stops/<int:route_id>")
def get_route_stops(route_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT s.stop_id, s.stop_name
        FROM route_stop rs
        JOIN stop s ON rs.stop_id = s.stop_id
        WHERE rs.route_id = %s
        ORDER BY rs.stop_order
    """, (route_id,))
    
    stops = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {"stops": stops}  # return JSON for JS



# ---------------- View Tickets ----------------
@app.route("/view_ticket")
def view_ticket():
    tickets = session.get("tickets", [])

    if not tickets:
        return render_template("ticket.html", tickets=[])

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    for t in tickets:
        # Fetch source name
        cursor.execute("SELECT stop_name FROM stop WHERE stop_id=%s", (t["source_stop_id"],))
        src = cursor.fetchone()
        t["source_name"] = src["stop_name"] if src else "Unknown"

        # Fetch destination name
        cursor.execute("SELECT stop_name FROM stop WHERE stop_id=%s", (t["destination_stop_id"],))
        dest = cursor.fetchone()
        t["destination_name"] = dest["stop_name"] if dest else "Unknown"

        # Fetch route name
        cursor.execute("SELECT route_name FROM route WHERE route_id=%s", (t["route_id"],))
        route = cursor.fetchone()
        t["route_name"] = route["route_name"] if route else "Unknown"

        # Fetch stops for this route
        cursor.execute("""
            SELECT s.stop_id, s.stop_name, s.latitude, s.longitude
            FROM route_stop rs
            JOIN stop s ON rs.stop_id = s.stop_id
            WHERE rs.route_id = %s
            ORDER BY rs.stop_order
        """, (t["route_id"],))
        t["route_stops"] = cursor.fetchall()  
    cursor.close()
    conn.close()

    return render_template("ticket.html", tickets=tickets)


@app.route("/live_location", methods=["POST"])
def live_location():
    data = request.get_json()
    if not data:
        return {"status": "INVALID"}

    ticket_id = data.get("ticket_id")
    try:
        user_lat = round(float(data.get("latitude")), 6)
        user_lng = round(float(data.get("longitude")), 6)
    except (TypeError, ValueError):
        return {"status": "INVALID"}

    tickets = session.get("tickets", [])
    ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    if not ticket:
        return {"status": "INVALID"}

    route_id = ticket["route_id"]
    source_id = ticket["source_stop_id"]
    dest_id = ticket["destination_stop_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch stops of this route in order
    cursor.execute("""
        SELECT s.stop_id, s.stop_name, s.latitude, s.longitude
        FROM route_stop rs
        JOIN stop s ON rs.stop_id = s.stop_id
        WHERE rs.route_id = %s
        ORDER BY rs.stop_order
    """, (route_id,))

    stops = cursor.fetchall()
    cursor.close()
    conn.close()

    # Find index of source and destination stops
    source_index = next((i for i, s in enumerate(stops) if s["stop_id"] == int(source_id)), None)
    dest_index = next((i for i, s in enumerate(stops) if s["stop_id"] == int(dest_id)), None)

    if source_index is None or dest_index is None:
        return {"status": "INVALID"}

    # Check if user's GPS is between source and destination stops
    GPS_TOLERANCE = 0.0005  # ~50 meters
    valid = False
    for i in range(source_index, dest_index + 1):
        stop = stops[i]
        if stop["latitude"] is None or stop["longitude"] is None:
            continue
        stop_lat = round(float(stop["latitude"]), 6)
        stop_lng = round(float(stop["longitude"]), 6)
        if abs(stop_lat - user_lat) <= GPS_TOLERANCE and abs(stop_lng - user_lng) <= GPS_TOLERANCE:
            valid = True
            break

    return {"status": "VALID" if valid else "INVALID"}


@app.route("/daily_pass", methods=["GET", "POST"])
def daily_pass():

    if request.method == "POST":
        # create daily pass
        daily_pass = {
            "id": "PASS" + str(random.randint(1000, 9999)),
            "expiry": datetime.datetime.now().strftime("%Y-%m-%d 23:59:59")
        }
        session["daily_pass"] = daily_pass

        return redirect(url_for("daily_pass"))

    daily_pass = session.get("daily_pass")
    return render_template("pass.html", daily_pass=daily_pass)



# ---------------- Logout ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True)

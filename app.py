from flask import Flask, render_template, request, redirect, session, send_from_directory, url_for, flash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "mysecretkey"

# ----------------------
# LOGIN DATA
# ----------------------
students = {
    "M25CA029": "11-02-2005",
    "M25CA010": "01-01-2005",
    "M25CA015": "22-09-2004",
    "M25CA039": "28-11-2003"

}

# ----------------------
# SUBJECTS (display name -> folder name)
# ----------------------
subjects = {
    "Python": "python",
    "DBMS": "dbms",
    "Networking": "networking",
    "Data Structures": "data_structures"
}

notes_data = {subject: [] for subject in subjects.keys()}

# ----------------------
# UPLOAD SETTINGS
# ----------------------
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "py","c"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ----------------------
# LOGIN
# ----------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        adm_no = request.form["adm_no"].strip()
        password = request.form["password"].strip()

        if adm_no in students and students[adm_no] == password:
            session["student"] = adm_no
            return redirect(url_for("home"))
        else:
            return render_template("login.html", msg="Invalid admission number or DOB!")

    return render_template("login.html", msg=None)


# ----------------------
# HOME
# ----------------------
@app.route("/home")
def home():
    if "student" not in session:
        return redirect(url_for("login"))
    # Pass subjects as list of tuples (display, folder)
    subject_items = list(subjects.items())
    student = session.get("student")
    return render_template("home.html", student=student, subject_items=subject_items)


# ----------------------
# VIEW NOTES
# ----------------------
@app.route("/notes/<subject>")
def notes(subject):
    if "student" not in session:
        return redirect(url_for("login"))

    if subject not in subjects:
        flash("Unknown subject.")
        return redirect(url_for("home"))

    folder_name = subjects[subject]
    folder = os.path.join(UPLOAD_FOLDER, folder_name)
    os.makedirs(folder, exist_ok=True)

    uploaded_files = sorted(os.listdir(folder))
    text_notes = notes_data.get(subject, [])

    return render_template("notes.html",
                           subject=subject,
                           files=uploaded_files,
                           folder_name=folder_name,
                           notes=text_notes)


# ----------------------
# ADD NOTE
# ----------------------
@app.route("/add_note/<subject>", methods=["GET", "POST"])
def add_note(subject):
    if "student" not in session:
        return redirect(url_for("login"))

    if subject not in subjects:
        flash("Unknown subject.")
        return redirect(url_for("home"))

    folder_name = subjects[subject]
    folder = os.path.join(UPLOAD_FOLDER, folder_name)
    os.makedirs(folder, exist_ok=True)

    if request.method == "POST":
        text = request.form.get("note")
        if text:
            notes_data[subject].append(text.strip())

        file = request.files.get("file")
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(folder, filename))

        return redirect(url_for("notes", subject=subject))

    return render_template("add_note.html", subject=subject)


# ----------------------
# SERVE FILES
# ----------------------
@app.route("/uploads/<folder>/<filename>")
def uploaded_file(folder, filename):
    safe_folder = os.path.basename(folder)
    return send_from_directory(os.path.join(UPLOAD_FOLDER, safe_folder), filename)


# ----------------------
# LOGOUT
# ----------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, redirect

app = Flask(__name__)

members = []   # temporary storage

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add", methods=["POST"])
def add_member():
    name = request.form.get("name")
    age = request.form.get("age")

    members.append({"name": name, "age": age})

    return redirect("/members")

@app.route("/members")
def show_members():
    return render_template("members.html", members=members)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
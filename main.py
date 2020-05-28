from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
import psutil
import shutil
import platform
import subprocess
import threading
import time
import smtplib
import hashlib
import datetime
from email.message import EmailMessage
r = "r"
w = "w"
a = "a"
second = 1
minute = 60*second
hours = 60*minute
day = 24*hours
week = 7*day

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///DB.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
app.secret_key = "EnterYoutSecretKey"
db = SQLAlchemy(app)


class timer():

    """timer class with unix time"""

    def __init__(self):
        self.currentDT = 0

    def set_timer(self):
        self.currentDT = time.time()

    def get_timer(self):
        self.cDT = time.time()
        return(self.cDT-self.currentDT)


CTTI = timer()


class users(db.Model):

    """DB CLASSES"""

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    passw = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    oplevel = db.Column(db.Integer)

    def __init__(self, name, passw, contact, oplevel):

        """DB CLASSES"""

        self.name = name
        self.passw = passw
        self.contact = contact
        self.oplevel = oplevel


class commands(db.Model):

    """DB CLASSES"""

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    commands = db.Column(db.String(100))
    oplevel = db.Column(db.Integer)

    def __init__(self, name, commands, oplevel):

        """DB CLASSES"""
        
        self.name = name
        self.commands = commands
        self.oplevel = oplevel


@app.route("/")
def dntex():
    return redirect(url_for("home"))


@app.route("/createeacc", methods=["POST", "GET"])
def createeacc():
    if "user" in session:
        if "passw" in session:
            user = session["user"]
            passw = session["passw"]
            if passw != "":
                if user != "":
                    if request.method == "POST":
                        userd = request.form["Username"]
                        passw = request.form["passw"]
                        passw1 = request.form["passw1"]
                        contact = request.form["contact"]
                        if passw1 == passw:
                            passw = hashlib.sha512(
                                str(userd+passw).encode()).hexdigest()

                            try:
                                perms = request.form["perms"]
                            except Exception as e:
                                flash(
                                    "you need to specify ALL of the info!!!", str(e))
                                return render_template('createaccount.html', user=user, usr=userd, pasw=passw, email=contact)
                            fuu = users.query.filter_by(name=user).first()
                            fu = users.query.filter_by(name=userd).first()
                            if fuu:
                                if int(fuu.oplevel) >= 0:
                                    if fu:
                                        flash("user already exist!!", "info")
                                        return render_template('createaccount.html', user=user, ft="error")
                                    else:

                                        if int(perms) <= int(fuu.oplevel):
                                            pass
                                        else:
                                            perms = fuu.oplevel
                                            flash(
                                                "you enter a op level that is higher to your the user have perms: "+str(perms), "info")
                                            return render_template('createaccount.html', user=user, ft="error", usr=userd, pasw=passw, email=contact)
                                        usr = users(
                                            userd, passw, contact, perms)
                                        db.session.add(usr)
                                        db.session.commit()
                                        flash("user created!", "info")
                                        return render_template('createaccount.html', user=user, ft="s")
                        else:
                            flash("password are not identical!!!", "info")
                            return render_template('createaccount.html', user=user, usr=userd, pasw=passw, email=contact)

                    else:
                        return render_template('createaccount.html', user=user)

                else:
                    return redirect(url_for("login"))
            else:
                return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))


def run_command(*args):
    command = ""
    for i in args:
        command += i
    subprocess.Popen(command)


@app.route("/SMS", methods=["POST", "GET"])
def SMS():
    if "user" in session:
        if "passw" in session:
            user = session["user"]
            passw = session["passw"]
            if passw != "":
                if user != "":
                    fu = users.query.filter_by(name=user).first()
                    if int(fu.oplevel) >= 0:
                        if request.method == "POST":
                            commandN = request.form["commandN"]
                            fuu = commands.query.filter_by(
                                name=commandN).first()
                            if fuu:
                                command = fuu.commands
                                oplvl = fuu.oplevel
                                if oplvl <= session["perms"]:
                                    x = threading.Thread(
                                        target=run_command, args=(str(command,)))
                                    x.start()
                                    flash(
                                        f"command \"{command}\" was launch! ", "info")
                                    return render_template('sms.html', user=user, values=commands.query.all(), ft="s")
                                else:
                                    flash(
                                        "you dont have the perms to do that!", "error")
                                    return render_template('sms.html', user=user, values=commands.query.all(), ft="error")

                            else:
                                flash(
                                    f"unknow command \"{commandN}\"", "error")
                                return render_template('sms.html', user=user, values=commands.query.all(), ft="error")
                            return render_template('sms.html', user=user, values=commands.query.all())
                        else:
                            return render_template('sms.html', user=user, values=commands.query.all())
                    else:
                        return render_template('NP.html', user=user)
                else:
                    return redirect(url_for("login"))
            else:
                return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))


@app.route("/Manage", methods=["POST", "GET"])
def Manage():
    if "user" in session:
        if "passw" in session:
            user = session["user"]
            passw = session["passw"]
            if passw != "":
                if user != "":
                    fu = users.query.filter_by(name=user).first()
                    if int(fu.oplevel) >= 3:
                        if request.method == "POST":
                            n = request.form.get('IdTDel', None)
                            if n != None:
                                userd = request.form["IdTDel"]
                                commands.query.filter_by(_id=userd).delete()
                                db.session.commit()
                                return render_template('Manage.html', user=user, values=commands.query.all())
                            elif request.form.get('commandN', None) != None:
                                commandname = request.form["commandN"]
                                command = request.form["command"]
                                commandLVL = request.form["commandLVL"]
                                if request.form.get('commandN', None) != None:
                                    if request.form.get('command', None) != None:
                                        if request.form.get('commandLVL', None) != None:
                                            comm = commands(
                                                commandname, command, commandLVL)
                                            if commands.query.filter_by(name=commandname, commands=command, oplevel=commandLVL).first():
                                                pass
                                            else:
                                                comm = commands(
                                                    commandname, command, commandLVL)
                                                db.session.add(comm)
                                                db.session.commit()
                                            return render_template('Manage.html', user=user, values=commands.query.all())
                                        else:
                                            return render_template('Manage.html', user=user, values=commands.query.all())
                                    else:
                                        return render_template('Manage.html', user=user, values=commands.query.all())
                                else:
                                    return render_template('Manage.html', user=user, values=commands.query.all())
                            else:
                                return render_template('Manage.html', user=user, values=commands.query.all())
                        else:
                            return render_template('Manage.html', user=user, values=commands.query.all())
                    else:
                        return render_template('NP.html', user=user)
                else:
                    return redirect(url_for("login"))
            else:
                return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))


@app.route("/Manageacc", methods=["POST", "GET"])
def manageacc():
    if "user" in session:
        if "passw" in session:
            user = session["user"]
            passw = session["passw"]
            if passw != "":
                if user != "":
                    fu = users.query.filter_by(name=user).first()
                    if int(fu.oplevel) >= 3:
                        if request.method == "POST":
                            userd = request.form["IdToDel", None]
                            if userd != None:
                                users.query.filter_by(_id=userd).delete()
                                db.session.commit()
                            return render_template('manageacc.html', user=user, values=users.query.all())
                        else:
                            return render_template('manageacc.html', user=user, values=users.query.all())
                    else:
                        return render_template('NP.html', user=user)
                else:
                    return redirect(url_for("login"))
            else:
                return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))


@app.route("/ResourceUsage")
def RU():
    return redirect(url_for("home"))


@app.route("/main", methods=["POST", "GET"])
def home():
    if "user" in session:
        if "passw" in session:
            user = session["user"]
            passw = session["passw"]
            if passw != "":
                if user != "":
                    user = session["user"]
                    passw = session["passw"]
                    if request.method == "GET":
                        cpuper = psutil.cpu_percent(1, True)
                        j = 0
                        m = 0
                        for i in cpuper:
                            j += 1
                            m += i
                        m = m/j
                        mem = psutil.virtual_memory()
                        j = 0
                        for i in mem:
                            if j == 0:
                                total = i
                            elif j == 2:
                                perc = i
                            elif j == 3:
                                use = i
                            j += 1
                        if platform.system() == "windows":
                            totald, usedd, f = shutil.disk_usage("c:/")
                        else:
                            totald, usedd, f = shutil.disk_usage("/")
                        if f >= 0:
                            diskp = usedd/totald
                            diskstr = f"{int(diskp*100)}% free ({int((usedd/1048576)/1000)}Go/{int((totald/1048576)/1000)}Go)"
                            return render_template('main.html', user=user, cpuusage=round(m*1, 2), memory=f"{perc}% used ({str(round(use/1048576))}/{str(round(total/1048576))} Mo)", disk=diskstr)
                else:
                    return redirect(url_for("login"))
            else:
                return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["UN"]

        passw = request.form["PS"]
        passw = hashlib.sha512(str(user+passw).encode()).hexdigest()
        if passw != "" or user != "":
            fu = users.query.filter_by(name=user, passw=passw).first()
            if fu:
                session["user"] = fu.name
                session["passw"] = fu.passw
                session["cd"] = fu.contact
                session["perms"] = fu.oplevel
            else:
                flash(
                    "invalid information or your account is not set-up correcly", "info")
                return render_template('login.html', pasw="", usr=user)
        else:
            return render_template('login.html', pasw="", usr=user)
        return redirect(url_for("home"))
    else:
        return render_template('login.html')


@app.route("/Logoff")
def logoff():
    if "user" in session:
        if "passw" in session:
            user = session["user"]
            passw = session["passw"]
            if passw != "":
                if user != "":
                    session.pop("user", None)
                    session.pop("passw", None)
                    flash("you log out", "info")
                    return redirect(url_for("login"))
                else:
                    return redirect(url_for("login"))
            else:
                return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))


def gct():
    currentDT = datetime.datetime.now()
    return(currentDT.strftime("%a. %H:%M:%S"))


def smts(raison, template, data):
    if CTTI.get_timer() >= 360:
        CTTI.set_timer()
        time.sleep(1)
        f = open("smtppsw", r)
        l = f.read()
        a = l.split("\n")
        usermail = a[0]
        password = a[1]
        to = users.query.all()
        toa = []
        for i in to:
            toa.append(i.contact)
        smtp_server = "smtp.gmail.com"
        port = 587  # For starttls
        try:
            server = smtplib.SMTP(smtp_server, port)
            server.ehlo()  # Can be omitted
            server.starttls()  # Secure the connection
            server.ehlo()  # Can be omitted
            server.login(usermail, password)
            msgs = """\
                <!DOCTYPE html>

                <head>
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
    
                <html>
                    <body>

                        <table class="table table-striped table-dark">
                        <thead>
                            <tr>
                            <th scope="col">Time</th>
                            <th scope="col">Cpu used</th>
                            <th scope="col">Ram used</th>
                            </tr>
                        </thead>"""
            j = 0
            for i in timelog:
                print(i)
                msgs += f"""
                            <tbody>
                                <tr>
                                <th scope="row">{timelog[j]}</th>
                                <td></td>
                                <td>{str(cpulog[j])+"%"}</td>
                                <td>{str(ramlog[j])+"%"}</td>
                                </tr>

                            </tbody>"""
                j += 1
            msgs += """
                

                        </table>
                    </body>
                </html>
                </head>
                """
            for i in toa:
                msg = EmailMessage()
                msg['Subject'] = f'the {raison} as exceed {data}%!!'
                msg['From'] = usermail
                msg['To'] = i

                msg.set_content('This is a plain text email')

                msg.add_alternative(msgs, subtype='html')
                server.send_message(msg)
        except Exception as e:
            # Print any error messages to stdout
            print(e)


cpulog = []
ramlog = []
timelog = []


def verif():
    time.sleep(0.1)
    print("daemon started")
    while True:
        crut = time.time()
        cpuperc = psutil.cpu_percent(10)
        totvm = psutil.virtual_memory()
        if len(timelog) >= 60:
            timelog.pop(0)
        timelog.append(gct())

        if len(cpulog) >= 60:
            cpulog.pop(0)
        cpulog.append(cpuperc)
        ccpu = 0
        for i in cpulog:
            ccpu += i
        if ccpu/len(cpulog) >= 5:
            ccput = threading.Thread(target=smts, args=(
                "cpu", "cpu", f"{int(ccpu/len(cpulog))}"))
            ccput.start()
        if len(ramlog) >= 60:
            ramlog.pop(0)
        ramlog.append(totvm[2])
        cram = 0
        for i in ramlog:
            cram += int(i)
        if cram/len(ramlog) >= 5:
            ccram = threading.Thread(target=smts, args=(
                "ram", "ram", f"{int(cram/len(ramlog))}"))
            ccram.start()
        if crut-time.time()+15 >= 0.5:
            time.sleep(crut-time.time()+15)
        else:
            pass


if __name__ == "__main__":
    db.create_all()
    smtpthread = threading.Thread(target=verif, args=())
    smtpthread.start()

    app.run(debug=False, port=8900, ssl_context=(
        'SSL/selfsigned.crt', 'SSL/private.key'))

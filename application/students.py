""" Student endpoints """
import flask

from flask import send_file
from flask import current_app as app
from . import db_connect as db


@app.route("/students/")
@db.validate_student
def student_home():
    """ student default page """
    return flask.render_template(
        "/students/index.html", classes=db.get_student_classes()
    )


@app.route("/students/classes/")
@db.validate_student
def student_classes_home():
    """ student classes page """
    return flask.render_template(
        "/students/classes.html", classes=db.get_student_classes()
    )


@app.route("/students/classes/join/", methods=["POST"])
@db.validate_student
def student_class_join():
    """If student joins a class"""
    db.insert_db(
        "INSERT INTO roster (person_id, class_id) VALUES (?, ?);",
        [flask.session["id"], flask.request.form["id"]],
    )
    flask.flash(f"You joined the class with an id of {flask.request.form['id']}")
    return flask.redirect("/students/classes")


@app.route("/students/classes/<class_id>/")
@db.validate_student
def student_class_page(class_id):
    """Show classes"""
    class_name = db.query_db(
        "SELECT name FROM classes WHERE class_id=?;", [class_id], one=True
    )
    return flask.render_template(
        "/students/class_page.html",
        class_id=class_id,
        class_name=str(class_name[0]),
        quizzes=db.get_class_quizzes(class_id),
        grades=db.get_student_grade(class_id),
    )


@app.route("/students/classes/<class_id>/quizzes/<quiz_id>/")
@db.validate_student
def student_quiz_page(class_id, quiz_id):
    """Allows students to view/take quizzes"""
    quiz_name = str(
        db.query_db(
            "SELECT name FROM quizzes WHERE quiz_id=? AND class_id=?;",
            [quiz_id, class_id],
        )[0][0]
    )
    result = db.query_db(
        "SELECT grade from quiz_grades WHERE quiz_id=? AND student_id=?;",
        [quiz_id, flask.session["id"]],
        one=True,
    )
    # check if the person has already completed the test
    if result is None:
        questions_db = db.query_db(
            "SELECT question_id, question_type, question_text, a_text, b_text,"
            " c_text, d_text, correct_answer FROM questions WHERE quiz_id=?;",
            [quiz_id],
        )
        questions = []
        for question in questions_db:
            question_info = {}
            question_info["id"] = question[0]
            question_info["type"] = question[1]
            question_info["text"] = question[2]
            # if this is a multiple-choice question
            if question[0] == 1:
                question_info["answers"] = {}
                question_info["answers"]["a"] = question[3]
                question_info["answers"]["b"] = question[4]
                question_info["answers"]["c"] = question[5]
                question_info["answers"]["d"] = question[6]
            questions.append(question_info)
        return flask.render_template(
            "/students/quiz_page.html",
            questions=questions,
            quiz_name=quiz_name,
            quiz_id=quiz_id,
            class_id=class_id,
        )

    flask.flash(f"You receieved {result[0]} on this quiz.")
    return flask.render_template("/students/quiz_page.html", quiz_name=quiz_name)


@app.route("/students/4yrplan/", methods=["POST", "GET"])
def student_4yrplan():
    """ 4 year plan page """
    if flask.request.method == "POST":
        if "file" not in flask.request.files:
            flask.flash("No file part")
            return flask.redirect(flask.request.url)
        file = flask.request.files["file"]
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == "":
            flask.flash("No selected file")
            return flask.redirect(flask.request.url)
        if file:
            student_name = db.query_db(
                "select name from people where person_id=?;", [flask.session["id"]]
            )[0][0]
            contents = file.stream.read()
            # pylint: disable=bad-continuation
            with open(
                f"{app.config['UPLOAD_FOLDER']}/{student_name}_{file.filename}", "wb"
            ) as out_file:
                out_file.write(contents)
        return flask.redirect("/students/4yrplan/")

    return flask.render_template("/students/4yrplan.html")


#
# @app.route('/download')
# def download():
#     file = open('4yrplan/4yrplan_template.csv','r')
#     returnfile = file.read().encode('latin-1')
#     file.close()
#     return Response(returnfile,
#         mimetype="text/csv",
#         headers={"Content-disposition":
#                  "attachment; filename=4yrplan_template.csv"})


@app.route("/return-files/")
def return_files_tut():
    """ Downloads 4yr plan template """
    try:
        return send_file("4yrplan/_4yrplan.xlsx", attachment_filename="_4yrplan.xlsx")
    # pylint: disable=broad-except
    except Exception as e:
        return str(e)

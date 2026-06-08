from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
    flash
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from config import Config

from models import (
    db,
    User,
    Course,
    Video,
    Quiz,
    Question,
    Result
)

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)


COURSES = [

    "روبیک 2×2",
    "روبیک 3×3",
    "روبیک 4×4",
    "پیرامینکس",

    "فیزیک دهم",
    "فیزیک یازدهم",
    "فیزیک دوازدهم",

    "ریاضی دهم",
    "ریاضی یازدهم",
    "ریاضی دوازدهم",

    "شیمی دهم"

]


def create_default_data():

    admin = User.query.filter_by(
        username="Sam"
    ).first()

    if not admin:

        admin = User(
            username="Sam",
            password=generate_password_hash(
                "davudy"
            ),
            is_admin=True
        )

        db.session.add(admin)

    for title in COURSES:

        exists = Course.query.filter_by(
            title=title
        ).first()

        if not exists:

            db.session.add(
                Course(
                    title=title,
                    description=""
                )
            )

    db.session.commit()


@app.before_request
def setup_database():

    db.create_all()

    if not hasattr(
        app,
        "_database_created"
    ):

        create_default_data()

        app._database_created = True


@app.route("/")
def home():

    return render_template(
        "home.html"
    )


@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )

        user = User.query.filter_by(
            username=username
        ).first()

        if user:

            flash(
                "این نام کاربری قبلاً ثبت شده است"
            )

            return redirect(
                "/register"
            )

        new_user = User(

            username=username,

            password=generate_password_hash(
                password
            )

        )

        db.session.add(
            new_user
        )

        db.session.commit()

        flash(
            "ثبت نام با موفقیت انجام شد"
        )

        return redirect(
            "/login"
        )

    return render_template(
        "register.html"
    )


@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(
            username=username
        ).first()

        print("USERNAME =", username)
        print("USER =", user)

        if user:
            print(
                "CHECK =",
                check_password_hash(
                    user.password,
                    password
                )
            )

        if user and check_password_hash(
            user.password,
            password
        ):

            session["user_id"] = user.id
            session["username"] = user.username
            session["is_admin"] = user.is_admin

            if user.is_admin:
                return redirect("/admin")

            return redirect("/dashboard")

        flash("نام کاربری یا رمز اشتباه است")

    return render_template(
        "login.html"
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    courses = Course.query.all()

    return render_template(
        "dashboard.html",
        courses=courses
    )


@app.route("/course/<int:course_id>")
def course(course_id):

    if "user_id" not in session:
        return redirect("/login")

    course = Course.query.get_or_404(
        course_id
    )

    videos = Video.query.filter_by(
        course_id=course_id
    ).all()

    quizzes = Quiz.query.filter_by(
        course_id=course_id
    ).all()

    return render_template(
        "course.html",
        course=course,
        videos=videos,
        quizzes=quizzes
    )


@app.route("/video/<int:video_id>")
def video_player(video_id):

    if "user_id" not in session:
        return redirect("/login")

    video = Video.query.get_or_404(
        video_id
    )

    return render_template(
        "video_player.html",
        video=video
    )


@app.route("/competition")
def competition():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "competition.html"
    )


@app.route("/progress")
def progress():

    if "user_id" not in session:
        return redirect("/login")

    results = Result.query.filter_by(
        user_id=session["user_id"]
    ).all()

    total_exams = len(results)

    average = 0

    best_score = 0

    last_score = 0

    if total_exams > 0:

        scores = [
            r.score
            for r in results
        ]

        average = sum(scores) / len(scores)

        best_score = max(scores)

        last_score = scores[-1]

    return render_template(
        "progress.html",
        total_exams=total_exams,
        average=average,
        best_score=best_score,
        last_score=last_score
    )


@app.route("/admin")
def admin():

    if not session.get(
        "is_admin"
    ):
        return redirect("/login")

    courses = Course.query.all()
    quizzes = Quiz.query.all()

    total_users = User.query.count()
    total_videos = Video.query.count()
    total_quizzes = Quiz.query.count()

    return render_template(
        "admin.html",
        courses=courses,
        quizzes=quizzes,
        total_users=total_users,
        total_videos=total_videos,
        total_quizzes=total_quizzes
    )


@app.route(
    "/admin/add-video",
    methods=["GET", "POST"]
)
def add_video():

    if not session.get(
        "is_admin"
    ):
        return redirect("/login")

    if request.method == "POST":

        title = request.form.get(
            "title"
        )

        filename = request.form.get(
            "filename"
        )

        course_id = request.form.get(
            "course_id"
        )

        video = Video(

            title=title,

            filename=filename,

            course_id=course_id

        )

        db.session.add(
            video
        )

        db.session.commit()

        flash(
            "ویدیو با موفقیت ثبت شد"
        )

        return redirect(
            "/admin"
        )

    courses = Course.query.all()

    return render_template(
        "add_video.html",
        courses=courses
    )


@app.route(
    "/admin/add-quiz",
    methods=["GET", "POST"]
)
def add_quiz():

    if not session.get(
        "is_admin"
    ):
        return redirect("/login")

    if request.method == "POST":

        title = request.form.get(
            "title"
        )

        course_id = request.form.get(
            "course_id"
        )

        quiz = Quiz(

            title=title,

            course_id=course_id

        )

        db.session.add(
            quiz
        )

        db.session.commit()

        flash(
            "آزمون ثبت شد"
        )

        return redirect(
            "/admin"
        )

    courses = Course.query.all()
    
    return render_template(
        "add_quiz.html",
        courses=courses
    )


@app.route(
    "/quiz/<int:quiz_id>"
)
def quiz_page(quiz_id):

    if "user_id" not in session:
        return redirect("/login")

    quiz = Quiz.query.get_or_404(
        quiz_id
    )

    questions = Question.query.filter_by(
        quiz_id=quiz.id
    ).all()

    return render_template(
        "quiz.html",
        quiz=quiz,
        questions=questions
    )
    


@app.route(
    "/submit-quiz/<int:quiz_id>",
    methods=["POST"]
)
def submit_quiz(quiz_id):

    if "user_id" not in session:
        return redirect("/login")

    questions = Question.query.filter_by(
        quiz_id=quiz_id
    ).all()

    score = 0

    total = len(questions)

    for question in questions:

        selected = request.form.get(
            f"question_{question.id}"
        )

        if selected:

            if int(selected) == int(
                question.correct_answer
            ):
                score += 1

    percent = 0

    if total > 0:

        percent = int(
            (score / total) * 100
        )

    result = Result(

        user_id=session["user_id"],

        quiz_id=quiz_id,

        score=percent

    )

    db.session.add(
        result
    )

    db.session.commit()

    return redirect(
    url_for(
        "quiz_result",
        score=percent,
        correct=score,
        total=total
    )
)


@app.route("/quiz-result")
def quiz_result():

    score = int(
        request.args.get("score", 0)
    )

    correct = int(
        request.args.get("correct", 0)
    )

    total = int(
        request.args.get("total", 0)
    )

    return render_template(
        "quiz_result.html",
        score=score,
        correct=correct,
        total=total
    )


@app.route(
    "/admin/add-question/<int:quiz_id>",
    methods=["GET", "POST"]
)
def add_question(quiz_id):

    if not session.get(
        "is_admin"
    ):
        return redirect("/login")

    quiz = Quiz.query.get_or_404(
        quiz_id
    )

    if request.method == "POST":

        question = Question(

            quiz_id=quiz.id,

            image=request.form.get(
                "image"
            ),

            question_text=request.form.get(
                "question"
            ),

            option1=request.form.get(
                "option1"
            ),

            option2=request.form.get(
                "option2"
            ),

            option3=request.form.get(
                "option3"
            ),

            option4=request.form.get(
                "option4"
            ),

            correct_answer=int(
                request.form.get(
                    "correct_answer"
                )
            )

        )

        db.session.add(
            question
        )

        db.session.commit()

        flash(
            "سوال ثبت شد، سوال بعدی را وارد کنید"
        )

        return redirect(
            url_for(
                "add_question",
                quiz_id=quiz.id
            )
        )

    return render_template(
        "add_question.html",
        quiz=quiz
    )


@app.route("/users")
def users():

    if not session.get(
        "is_admin"
    ):
        return redirect("/login")

    users = User.query.all()

    return render_template(
        "users.html",
        users=users
    )


@app.route("/courses")
def courses_page():

    courses = Course.query.all()

    return render_template(
        "courses.html",
        courses=courses
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    is_admin = db.Column(
        db.Boolean,
        default=False
    )


class Course(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text
    )


class Video(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200)
    )

    filename = db.Column(
        db.String(500)
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("course.id")
    )


class Quiz(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200)
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("course.id")
    )


class Question(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    quiz_id = db.Column(
        db.Integer,
        db.ForeignKey("quiz.id")
    )

    image = db.Column(
        db.String(500)
    )

    question_text = db.Column(
        db.Text
    )

    option1 = db.Column(db.String(300))
    option2 = db.Column(db.String(300))
    option3 = db.Column(db.String(300))
    option4 = db.Column(db.String(300))

    correct_answer = db.Column(
        db.Integer
    )


class Result(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    quiz_id = db.Column(
        db.Integer,
        db.ForeignKey("quiz.id")
    )

    score = db.Column(
        db.Integer
    )
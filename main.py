from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, desc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, URL, Length
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date, datetime

from wtforms.widgets import TextArea

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Create a new post form
class PostForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    sub_title = StringField(label='Subtitle', validators=[DataRequired()])
    author_name = StringField(label='Author Name', validators=[DataRequired()])
    url_img = StringField(label='Background img', validators=[DataRequired()])
    body = CKEditorField(label='Body', validators=[DataRequired()])
    submit = SubmitField(label='Submit', validators=[DataRequired()])


class ContactForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    email = EmailField(label='Email', validators=[DataRequired()])
    phone_num = StringField(label='Phone Number', validators=[DataRequired(), Length(10)])
    message = StringField(label='Message', widget=TextArea(), validators=[DataRequired()])
    contact_submit = SubmitField(label='SEND YOUR MESSAGE')


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


class ContactInfo(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    phone_num: Mapped[str] = mapped_column(String(250), nullable=False)
    message: Mapped[str] = mapped_column(String(600), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    # Query the database for all the posts. Convert the data to a python list.
    get_posts = list(db.session.execute(db.select(BlogPost).order_by(desc(BlogPost.date))).scalars())
    return render_template("index.html", all_posts=get_posts)


# Add a route so that you can click on individual posts.
@app.route('/posts/<int:post_id>')
def show_post(post_id):
    # Retrieve a BlogPost from the database based on the post_id
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


# add_new_post() to create a new blog post
@app.route('/new_post', methods=['GET', 'POST'])
def add_new_post():
    form = PostForm()
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        sub_title = request.form.get('sub_title')
        author_name = request.form.get('author_name')
        url_img = request.form.get('url_img')
        body = request.form.get('body')

        # Get the current date and format it
        current_date = datetime.now()
        formatted_date = current_date.strftime("%B %d, %Y")

        # Create a new blog post record
        new_create_post = BlogPost(
            title=title,
            subtitle=sub_title,
            author=author_name,
            img_url=url_img,
            body=body,
            date=formatted_date  # Assuming your model has a date_posted field
        )

        # Add the new post to the database session and commit
        db.session.add(new_create_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form)


# edit_post() to change an existing blog post
@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    get_post = db.get_or_404(BlogPost, post_id)
    edit_form = PostForm(
        title=get_post.title,
        sub_title=get_post.subtitle,
        author_name=get_post.author,
        url_img=get_post.img_url,
        body=get_post.body
    )
    if edit_form.validate_on_submit():
        get_post.title = edit_form.title.data
        get_post.subtitle = edit_form.sub_title.data
        get_post.author = edit_form.author_name.data
        get_post.img_url = edit_form.url_img.data
        get_post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))
    return render_template('make-post.html', form=edit_form, is_edit=True)


# delete_post() to remove a blog post from the database
@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    get_post = db.get_or_404(BlogPost, post_id)
    db.session.delete(get_post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/contact/thankyou')
def thankyou_page():
    return render_template("thankyou.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        # Get data from the form
        name = form.name.data
        email = form.email.data
        phone_num = form.phone_num.data
        message = form.message.data

        # Create a new ContactInfo record
        new_contact = ContactInfo(
            name=name,
            email=email,
            phone_num=phone_num,
            message=message
        )

        # Add the new contact to the database session and commit
        db.session.add(new_contact)
        db.session.commit()

        return redirect(url_for('thankyou_page'))

    return render_template("contact.html", form=form)


if __name__ == "__main__":
    app.run(debug=True, port=5003)

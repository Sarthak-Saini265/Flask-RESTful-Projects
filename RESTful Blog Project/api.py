from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
api = Api(app)
# app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blog.db"
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



class Blogdb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    author = db.Column(db.String(100))
    content = db.Column(db.String(6500))
    comment = db.Column(db.String(600))
    timestamp = db.Column(db.DateTime, default = datetime.now)

    def __repr__(self):
        return f"{self.title}-{self.content}-{self.author}"


# db.create_all()

resource_fields = {
    'id' : fields.Integer,
    'author' : fields.String,
    'title' : fields.String,
    'content' : fields.String,
    'comment' : fields.String,
    'timestamp' : fields.DateTime,
}


blog_post_args = reqparse.RequestParser()
blog_post_args.add_argument("author", type=str, help = "Author name is required", required = True)
blog_post_args.add_argument("title", type=str, help = "Title is required", required = True)
blog_post_args.add_argument("content", type=str, help = "Content is required", required = True)

blog_comment_args = reqparse.RequestParser()
blog_comment_args.add_argument("comment", type=str, help = "Comment something", required = True)

blog_update_args = reqparse.RequestParser()
blog_update_args.add_argument("author", type=str)
blog_update_args.add_argument("title", type=str)
blog_update_args.add_argument("content", type=str)
blog_update_args.add_argument("timestamp", type=datetime)

blog_comment_update_args = reqparse.RequestParser()
blog_comment_update_args.add_argument("comment", type=str)



class BlogList(Resource):
    def get(self):
        posts = Blogdb.query.all()
        blogs = {}
        for post in posts:
            blogs[post.id] = {'author' : post.author, 'title' : post.title, 'content' : post.content, 'comment' : post.comment, 'timestamp': post.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        return blogs



class Blog(Resource):
    @marshal_with(resource_fields)
    def get(self, blog_id):
        blog = Blogdb.query.filter_by(id=blog_id).first()
        if not blog:
            abort(404, message = "Blog not found. Id does not exist")
        return blog


    @marshal_with(resource_fields)
    def post(self, blog_id):
        args = blog_post_args.parse_args()
        post = Blogdb.query.filter_by(id=blog_id).first()
        if post:
            abort(409, message = "Blog id taken")
        blog = Blogdb(id = blog_id, author = args['author'], title = args['title'], content = args['content'])
        db.session.add(blog)
        db.session.commit()
        return blog


    @marshal_with(resource_fields)
    def put(self, blog_id):
        args = blog_update_args.parse_args()
        put = Blogdb.query.filter_by(id=blog_id).first()
        if not put:
            abort(404, message = "Id not found. Could not update")
        if args['author']:
            put.author = args['author']
        if args['title']:
            put.title = args['title']
        if args['content']:
            put.content = args['content']
        db.session.commit()
        return put

    def delete(self, blog_id):
        post = Blogdb.query.filter_by(id=blog_id).first()
        if not post:
            abort(404, message = "Id not found. Could not delete")
        db.session.delete(post)
        db.session.commit()
        return "Blog Deleted"


class Comment(Resource):
    @marshal_with(resource_fields)
    def post(self, blog_id):
        args = blog_comment_args.parse_args()
        post = Blogdb.query.filter_by(id=blog_id).first()
        post.comment = args['comment']
        db.session.commit()
        return post

    def delete(self, blog_id):
        post = Blogdb.query.filter_by(id=blog_id).first()
        if post.comment is None:
            abort(404, message = "No comment available. Could not delete")
        post.comment = None
        db.session.commit()
        return "Comment Deleted"
    
    @marshal_with(resource_fields)
    def put(self, blog_id):
        args = blog_comment_update_args.parse_args()
        comment = Blogdb.query.filter_by(id=blog_id).first()
        if comment.comment is None:
            abort(404, message = "No comment available. Could not update")
        comment.comment = args['comment']
        db.session.commit()
        return comment












api.add_resource(Blog, "/blog/<int:blog_id>")
api.add_resource(BlogList, "/allblogs")
api.add_resource(Comment, "/comment/<int:blog_id>")


if __name__ == "__main__":
    app.run(debug=True)



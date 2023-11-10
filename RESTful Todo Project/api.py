from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
api = Api(app)
# app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class Tododb(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    task = db.Column(db.String(150))
    summary = db.Column(db.String(400))

    def __repr__(self):
        return f"{self.task}-{self.summary}"


resource_fields = {
    'id' : fields.Integer,
    'task' : fields.String,
    'summary' : fields.String,
}



task_post_args = reqparse.RequestParser()
task_post_args.add_argument("task", type=str, help = "Task is required", required = True)
task_post_args.add_argument("summary", type=str, help = "Summary is required", required = True)

task_update_args = reqparse.RequestParser()
task_update_args.add_argument("task", type=str)
task_update_args.add_argument("summary", type=str)




# db.create_all()


class TodoList(Resource):
    def get(self):
        tasks = Tododb.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {'task' : task.task, 'summary' : task.summary}
        return todos


class Todo(Resource):
    @marshal_with(resource_fields)
    def get(self, todo_id):
        task = Tododb.query.filter_by(id = todo_id).first()
        if not task:
            abort(404, message = 'Could not find a todo with this Id')
        return task

    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        task = Tododb.query.filter_by(id=todo_id).first()
        if task:
            abort(409, message = "This task Id is taken")
        todo = Tododb(id=todo_id, task = args["task"], summary = args["summary"])
        db.session.add(todo)
        db.session.commit()
        return todo
    
    @marshal_with(resource_fields)
    def put(self, todo_id):
        args = task_update_args.parse_args()
        task = Tododb.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message='Task id does not exist. Could not update')
        if args["task"]:
            task.task = args["task"]
        if args["summary"]:
            task.summary = args["summary"]
        db.session.commit()
        return task


    def delete(self, todo_id):
        task = Tododb.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message = "Task id does not exist. Could not delete")
        db.session.delete(task)
        db.session.commit()
        return "Todo deleted"















api.add_resource(Todo, "/todos/<int:todo_id>")
api.add_resource(TodoList, "/alltodos")




if __name__ == "__main__":
    app.run(debug =True)



from app import app, db, login
from app.models import Sales, Items, User


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "Sales": Sales, "Items": Items, "login": login, "User": User}

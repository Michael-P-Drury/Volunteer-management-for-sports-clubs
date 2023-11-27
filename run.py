from website import app, db
from website.databases import User

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if User.query.filter_by(username='michael').first() is None:
            User.register('michael', 'michael1', False)
    app.run(debug = True)
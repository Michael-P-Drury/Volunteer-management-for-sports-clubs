from website import app, db
from website.databases import User

# run file which calls the application file website running the website
# creates a login for use when testing with username michael and password michael1

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if User.query.filter_by(username='michael').first() is None:
            User.register('michael', 'michael1', False)
        if User.query.filter_by(username='michael').first() is None:
            User.register('admin', 'admin1', True)
    app.run(debug = True)

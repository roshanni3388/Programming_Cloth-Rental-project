#init_db.py
from app import db
from app import app
from app import Admin #import other models as needed
def init_db():
    with app.app_context():
        db.drop_all() #drop existing tables
        db.create_all() # create new table based on models

        #optionally adding initial data
        admin=Admin(username='admin',password='admin123',areacode='1234')
        db.session.add(admin)
        db.session.commit()

if __name__=='__main__':
    init_db()


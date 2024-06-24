from flask import Flask
def create_app():
    app=Flask(__name__)  #name of file to run
    app.config['secretkey']= 'hdjsdskjdksjf' # to store cookie data its secret key for our app

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/login')
    app.register_blueprint(auth, url_prefix='/add_product')
    app.register_blueprint(auth, url_prefix='/edit_product')
    return app
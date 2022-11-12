from flask import Flask
from shop import app,db
from shop.admin import admin

if __name__=="__main__":
    # with app.app_context():
    #      db.create_all()
    app.run(debug=True)
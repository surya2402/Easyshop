from flask import render_template,session,request,redirect ,url_for,flash
from shop import app,db ,bcrypt,login_manager
from .forms import RegistrationForm,Loginform
from .model import User
from shop.products.model import Addproduct,Brand,Category
from flask_login import login_required,current_user,logout_user,login_user

import os


@app.route('/admin')
def admin():




    products=Addproduct.query.all()
    return render_template('admin/index.html',title='Admin Page',products=products)

@app.route('/brands')
def brands():
    brands=Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/brand.html',title="Brand Page",brands=brands)
@app.route('/category')
def category():
    categories=Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brand.html',title="category Page",categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        hash_password=bcrypt.generate_password_hash(form.password.data)
        user = User(name=form.name.data,username=form.username.data, email=form.email.data,
                    password=hash_password)
        db.session.add(user)
        flash(f'Welcome {form.name.data} Thanks you for registering', 'success')
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('admin/register.html', form=form,title="Registration Page")

@app.route('/login',methods=['GET','POST'])
def login():
    form=Loginform()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            session['email']=form.email.data
            flash(f'Welcome {form.email.data}. You are loggedin now','success')
            return redirect(request.args.get('next') or url_for('admin'))
        else:

            flash(f'Wrong password please try again','danger')
            return redirect(url_for('login'))

    return render_template('admin/login.html',form=form,title="Login Page")

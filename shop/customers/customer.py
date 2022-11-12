from flask import render_template,session, request,redirect,url_for,flash,current_app,make_response
from shop import app,db,photos, search,bcrypt,login_manager
from .forms import CustomerRegisterForm,CustomerLoginForm
from .model import Register,CustomerOrder
from shop.products.model import Addproduct,Brand,Category
from flask_login import login_required,current_user,logout_user,login_user
import os
import pdfkit
import secrets
import stripe

def brands():
    brands =Brand.query.join(Addproduct,(Brand.id == Addproduct.brand_id)).all()
    return brands
def categories():
    categories= Category.query.join(Addproduct,(Category.id == Addproduct.category_id)).all()
    return categories



@app.route('/customer/register',methods=["GET","POST"])
def customer_register():
    form = CustomerRegisterForm(request.form)
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user:
            flash(f'Cannot Create Account,Email ID already exist','danger')
            return redirect(url_for('customer_register'))
        user2 = Register.query.filter_by(username=form.username.data).first()
        if user2:
            flash(f'Cannot Create Account, Username already exist','danger')
            return redirect(url_for('customer_register'))


        hash_password= bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data, username=form.username.data, email=form.email.data,password=hash_password,country=form.country.data, city=form.city.data,contact=form.contact.data, address=form.address.data, zipcode=form.zipcode.data)
        db.session.add(register)
        flash(f'Welcome {form.name.data}.Thanks For Registering','success')
        db.session.commit()
        return redirect(url_for('customerLogin'))
    return render_template('customer/register.html',form=form,categories=categories(),brands=brands())


@app.route('/customer/login', methods=['GET', 'POST'])
def customerLogin():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'You are login now!', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Incorrect email and password', 'danger')
        return redirect(url_for('customerLogin'))

    return render_template('customer/login.html', form=form,categories=categories(),brands=brands())

def updateshoppingcart():
    for key, shopping in session['Shoppingcart'].items():
        session.modified = True
        del shopping['image']
        del shopping['colors']
    return updateshoppingcart

@app.route('/customer/details',methods=['GET','POST'])
@login_required
def customer_profile():
    form=CustomerRegisterForm()
    id= current_user.id
    name_to_update=Register.query.get_or_404(id)

    if request.method=="POST":
        name_to_update.name=request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email=request.form['email']
        name_to_update.country=request.form['country']
        name_to_update.city = request.form['city']
        name_to_update.contact = request.form['contact']
        name_to_update.address = request.form['address']
        name_to_update.zipcode = request.form['zipcode']
        db.session.commit()
        flash(f'User Updated Successfully!')
        return render_template("customer/profile.html",form=form,name_to_update=name_to_update,id=id)

    return render_template("customer/profile.html",
                           form=form,
                           name_to_update=name_to_update,
                           id=id,categories=categories(),brands=brands())

@app.route('/profile_update/<int:id>', methods=['GET', 'POST'])
@login_required
def profile_update(id):
    form = CustomerRegisterForm()
    name_to_update = Register.query.get_or_404(id)
    if request.method=="POST":
        name_to_update.name=request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.country = request.form['country']
        name_to_update.city = request.form['city']
        name_to_update.contact = request.form['contact']
        name_to_update.address = request.form['address']
        name_to_update.zipcode = request.form['zipcode']
        flash(f'Your Profile Updated Successfully', 'success')
        db.session.commit()
        return redirect(url_for('customer_profile'))

        request.form['name']=name_to_update.name
        request.form['username'] = name_to_update.username
        request.form['email'] = name_to_update.email
        request.form['country'] = name_to_update.country
        request.form['city'] = name_to_update.city
        request.form['contact'] = name_to_update.contact
        request.form['address'] = name_to_update.address
        request.form['zipcode'] = name_to_update.zipcode
    return render_template("customer/update_profile.html",
                           form=form,
                           name_to_update=name_to_update,
                           id=id,categories=categories(),brands=brands())

@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        updateshoppingcart
        try:
            order = CustomerOrder(invoice=invoice,customer_id=customer_id,orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash(customer_id)
            flash('Your order has been sent successfully','success')
            return redirect(url_for('orders',invoice=invoice))
        except Exception as e:
            print(e)
            flash('Some thing went wrong while get order', 'danger')
            return redirect(url_for('getCart'))



@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandtotal = 0
        subtotal = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount']/100) * float(product['price'])
            subtotal += float(product['price']) * int(product['quantity'])
            subtotal -= discount
            tax = ("%.2f" % (.06 * float(subtotal)))
            grandtotal = ("%.2f" % (1.06 * float(subtotal)))

    else:
        return redirect(url_for('customerLogin'))
    return render_template('customer/order.html', invoice=invoice, tax=tax,subtotal=subtotal,grandtotal=grandtotal,customer=customer,orders=orders,categories=categories(),brands=brands())

@app.route('/orderslist')
@login_required
def orderslist():
    if current_user.is_authenticated:
        customer_id = current_user.id
        orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc())



    else:
        return redirect(url_for('customerLogin'))
    return render_template('customer/orderslist.html',orders=enumerate(orders))





@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        grandtotal = 0
        subtotal = 0
        customer_id = current_user.id
        if request.method =="POST":
            customer = Register.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
            for _key, product in orders.orders.items():
                discount = (product['discount']/100) * float(product['price'])
                subtotal += float(product['price']) * int(product['quantity'])
                subtotal -= discount
                tax = ("%.2f" % (.06 * float(subtotal)))
                grandtotal = float("%.2f" % (1.06 * subtotal))

            return render_template('customer/pdf.html', invoice=invoice, tax=tax, subtotal=subtotal,
                                   grandtotal=grandtotal, customer=customer, orders=orders,categories=categories(),brands=brands())
            pdf = pdfkit.from_string(rendered, False)
            response = make_response(pdf)
            response.headers['content-Type'] ='application/pdf'
            response.headers['content-Disposition'] ='inline; filename='+invoice+'.pdf'
            return response
    return request(url_for('orders'))





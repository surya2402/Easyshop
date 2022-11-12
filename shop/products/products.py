from flask import redirect,render_template,url_for,flash,request,session,current_app
from shop import db,app,photos,search
from .model import Brand,Category,Addproduct
from flask_login import login_required,current_user,logout_user,login_user

from .forms import Addproducts
import secrets
import os

def brands():
    brands =Brand.query.join(Addproduct,(Brand.id == Addproduct.brand_id)).all()
    return brands
def categories():
    categories= Category.query.join(Addproduct,(Category.id == Addproduct.category_id)).all()
    return categories

@app.route('/result')
def result():

    searchword =request.args.get('ser')
    products= Addproduct.query.msearch(searchword,fields=['name','desc'],limit=6)
    return render_template('products/result.html',products=products,brands=brands(),categories=categories())

@app.route('/')
def home():
    page= request.args.get('page',1,type=int)
    products=Addproduct.query.filter(Addproduct.stock>0).order_by(Addproduct.id.desc()).paginate(page=page,per_page=12)

    return render_template('products/index.html',products=products,brands=brands(),categories=categories())


@app.route('/product/<int:id>')
def single_page(id):
    product=Addproduct.query.get_or_404(id)
    return render_template('products/single_page.html',product=product,categories=categories(),brands=brands())

@app.route('/brand/<int:id>')
def get_brand(id):
    page = request.args.get('page', 1, type=int)
    brd_id=Brand.query.filter_by(id=id).first_or_404()
    brand= Addproduct.query.filter_by(brand=brd_id).paginate(page=page,per_page=8)

    return render_template('products/index.html',brand=brand,brands=brands(),categories=categories(),brd_id=brd_id)

@app.route('/categories/<int:id>')
def get_category(id):
    page= request.args.get('page',1,type=int)
    cat_id=Category.query.filter_by(id=id).first_or_404()
    get_cat= Addproduct.query.filter_by(category=cat_id).paginate(page=page,per_page=8)
    return render_template('products/index.html',get_cat=get_cat,categories=categories(),brands=brands(),cat_id=cat_id)
@app.route('/addbrand',methods=['GET','POST'])
def addbrand():

    if 'email' not in session:
        flash(f'Please Login first','danger')
        return redirect(url_for('login'))
    if request.method =="POST":
        getbrand = request.form.get('brand')
        brand=Brand(name=getbrand)
        db.session.add(brand)
        flash(f'The Brand {getbrand} was added to your database','success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/addbrand.html',brands='brands')

@app.route('/updatebrand/<int:id>',methods=['GET','POST'])
def updatebrand(id):

    if 'email' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('login'))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method =="POST":
        updatebrand.name = brand
        flash(f'The brand has been updated','success')
        db.session.commit()
        return redirect(url_for('brands'))
    brand = updatebrand.name
    return render_template('products/updatebrand.html', title='Update brand',brands='brands',updatebrand=updatebrand)
@app.route('/deletebrand/<int:id>', methods=['GET','POST'])
def deletebrand(id):

    brand = Brand.query.get_or_404(id)
    if request.method=="POST":
        db.session.delete(brand)
        flash(f"{brand.name} Successfully Deleted","success")
        db.session.commit()
        return redirect(url_for('brands'))
    flash(f"{brand.name} can't be  deleted from your database","warning")
    return redirect(url_for('admin'))

@app.route('/addcat',methods=['GET','POST'])
def addcat():

    if 'email' not in session:
        flash(f'Please Login first','danger')
        return redirect(url_for('login'))
    if request.method =="POST":
        getcat = request.form.get('category')
        cat =Category(name=getcat)
        db.session.add(cat)
        flash(f'The Category {getcat} was added to your database','success')
        db.session.commit()
        return redirect(url_for('category'))
    return render_template('products/addbrand.html')

@app.route('/updatecat/<int:id>',methods=['GET','POST'])
def updatecat(id):

    if 'email' not in session:
        flash('Please Login First','danger')
        return redirect(url_for('login'))
    updatecat = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method =="POST":
        updatecat.name = category
        flash(f'Your Category has been updated','success')
        db.session.commit()
        return redirect(url_for('category'))
    category = updatecat.name
    return render_template('products/updatebrand.html', title='Update Category Page',updatecat='updatecat')

@app.route('/deletecat/<int:id>', methods=['GET','POST'])
def deletecat(id):

    category = Category.query.get_or_404(id)
    if request.method=="POST":
        db.session.delete(category)
        flash(f"The category {category.name} deleted successfully","success")
        db.session.commit()
        return redirect(url_for('category'))
    flash(f"The {category.name} category can't be  deleted from your database","warning")
    return redirect(url_for('admin'))

@app.route('/addproduct',methods=['GET','POST'])
def addproduct():

    if 'email' not in session:
        flash(f'Please Login first','danger')
        return redirect(url_for('login'))
    form=Addproducts(request.form)
    brands = Brand.query.all()
    categories = Category.query.all()

    if request.method=="POST":
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        colors = form.colors.data
        desc = form.discription.data
        brand = request.form.get('brand')
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'),name=secrets.token_hex(10)+".")
        image_2 = photos.save(request.files.get('image_2'),name=secrets.token_hex(10)+".")
        image_3 = photos.save(request.files.get('image_3'),name=secrets.token_hex(10)+".")
        addproduct = Addproduct(name=name, price=price, discount=discount, stock=stock, colors=colors, desc=desc,
                                category_id=category, brand_id=brand, image_1=image_1, image_2=image_2, image_3=image_3)
        db.session.add(addproduct)
        flash(f'The product {name} was added in database', 'success')
        db.session.commit()
        return redirect(url_for('addproduct'))

    return render_template('products/addproducts.html',form=form,title="Add Product Page",brands=brands,categories=categories)


@app.route('/updateproduct/<int:id>',methods=['GET','POST'])
def updateproduct(id):

    brands= Brand.query.all()
    categories= Category.query.all()
    product=Addproduct.query.get_or_404(id)
    form =Addproducts(request.form)
    brand=request.form.get('brand')
    category=request.form.get('category')
    if request.method == "POST":
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data
        product.colors = form.colors.data
        product.desc = form.discription.data
        product.category_id = category
        product.brand_id = brand
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        flash(f'The Product Updated Successfully','success')
        db.session.commit()
        return redirect(url_for('admin'))
    form.name.data=product.name
    form.price.data =product.price
    form.discount.data=product.discount
    form.stock.data=product.stock
    form.colors.data=product.colors
    form.discription.data=product.desc
    brand=product.brand.name
    category=product.category.name

    return render_template('products/updateproduct.html',form=form,brands=brands,categories=categories,product=product)


@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):

    product = Addproduct.query.get_or_404(id)
    if request.method =="POST":
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
        except Exception as e:
            print(e)
        db.session.delete(product)
        db.session.commit()
        flash(f' {product.name} deleted successfully ','success')
        return redirect(url_for('admin'))
    flash(f'Can not delete the product','success')
    return redirect(url_for('admin'))
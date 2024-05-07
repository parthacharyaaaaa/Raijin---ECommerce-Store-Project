from flask import Flask, redirect, render_template, url_for, session, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, login_user, current_user, LoginManager
from datetime import timedelta
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

import random
from excel import addToExcel, addContact
from validator import validateSignup
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ABCD'
app.permanent_session_lifetime = timedelta(days=1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///raijin2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
#Login management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def loadUser(user_id):
    return User.query.get(int(user_id))

#Database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    # username = db.Column(db.String(20), nullable=False)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(50), nullable = False, unique = True)
    phoneNum = db.Column(db.String(10), nullable = False, unique = True)

    def __init__(self, firstname, lastname, password, email, phoneNum):
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.email = email
        self.phoneNum = phoneNum

class Product(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    category = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(60), nullable=False)
    price = db.Column(db.Integer, nullable = False)
    specs = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.String(150), nullable=False)
    img1 = db.Column(db.String(50), nullable=False)
    img2 = db.Column(db.String(50), nullable=False) 
    img3 = db.Column(db.String(50), nullable=False)
    img4 = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    rates = db.Column(db.Integer, nullable = False)
    unitSold = db.Column(db.Integer, nullable = False)
    availableUnits = db.Column(db.Integer, nullable=False)

    def __init__(self, category, name, price, specs, description, summary, img1, img2, img3, img4, unitSold, availableUnits):
        self.category = category
        self.name = name
        self.price = price
        self.specs = specs
        self.description = description
        self.summary = summary
        self.img1 = img1
        self.img2 = img2
        self.img3 = img3
        self.img4 = img4
        self.unitSold = unitSold
        self.availableUnits = availableUnits

class Review(db.Model, UserMixin):
    contextProductId = db.Column(db.Integer, nullable = False)
    id = db.Column(db.Integer, primary_key = True)
    reviewBody = db.Column(db.String(300), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)

    def __init__(self, productID, reviewBody, rating, name, email):
        self.contextProductId = productID
        self.reviewBody = reviewBody
        self.rating = rating
        self.name = name
        self.email = email

@app.route("/")
def home(): 
    # session.pop("flash")
    randomProductListidfkman = Product.query.filter(Product.availableUnits > 0).order_by(db.func.random()).limit(6).all()
    if current_user.is_authenticated:
        print("Virar")
        print(randomProductListidfkman[1].img1)
    else:
        print("pp")
        flash("You are visiting us as a Guest. To enjoy all of our features, please sign up", "info")


    return render_template("homepage.html", isAuthenticated = current_user.is_authenticated,
    prodList = randomProductListidfkman,
    img1 = url_for('static', filename=f"{randomProductListidfkman[0].img1}"),
    img2 = url_for('static', filename=f"{randomProductListidfkman[1].img1}"),
    img3 = url_for('static', filename=f"{randomProductListidfkman[2].img1}"),
    img4 = url_for('static', filename=f"{randomProductListidfkman[3].img1}"),
    img5 = url_for('static', filename=f"{randomProductListidfkman[4].img1}"),
    img6 = url_for('static', filename=f"{randomProductListidfkman[5].img1}")
    )

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if current_user.is_authenticated:
        print("Already in session, going to dashboard")
        return redirect(url_for("dash"))
    if request.method == "POST":
        print("Triggered")
        firstname=request.form["new-first-name"]
        lastname=request.form["new-last-name"]
        password = request.form["new-password"]
        email = request.form["new-email"]
        phoneNum = request.form["new-phone"]
        cpass = request.form["confirm-password"]

        print(firstname, lastname, password, email, phoneNum, password)

        if validateSignup(firstname, lastname, email, phoneNum, password, cpass):
            print("proper")
        else:
            return redirect(url_for('signup'))

        emailExists = User.query.filter_by(email = email).first()
        phoneExists = User.query.filter_by(phoneNum = phoneNum).first()
        print(emailExists)
        if emailExists:
            print("Redir to login")
            flash("Email already exists")
            return redirect(url_for("signup"))
        elif phoneExists:
            print("Redir to login")
            flash("Phone number already exists")
            return redirect(url_for("signup"))
        else:
            # session["user"] = {"username" : username}
            session.permanent = True
            hashedPassword = bcrypt.generate_password_hash(password)
            newUser = User(firstname, lastname, hashedPassword, email, phoneNum)
            print("Created")
            db.session.add(newUser)
            db.session.commit()
            print("Committed")
            # flash("Account created successfully!", "info")
            login_user(newUser)
            return redirect(url_for("dash"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        foundUser = User.query.filter_by(email=email).first()

        if foundUser:
            if bcrypt.check_password_hash(foundUser.password, password):
                login_user(foundUser)
                print("-------------login_user called---------------")
                return redirect(url_for('dash'))
            else:
                flash("Login failed, invalid credentials", "warning")
                print("-----------INVALID CREDENTIALS-----------")
                return redirect(url_for('login'))
        else:
            flash("Login failed, user not found", "warning")
            print("-----------USER NOT FOUND-----------")
            return redirect(url_for('login'))
        
    return render_template("login.html")

@app.route("/addToCart", methods=["POST"])
def addToCart():
    if current_user.is_authenticated == False:
        flash("To enjoy our site's full features, such as having your own cart and submitting reviews, please sign in")
        return redirect(url_for('signup'))
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])

    print("Product ID:", product_id)
    print("Quantity:", quantity)
    productName = Product.query.filter_by(id=product_id).first()
    print("Product found via addToCart and DB: ", productName.name)

    if 'cart' not in session:
        # Not in session, initialize cart
        session['cart'] = []
        session.permanent = True
        print("----------------------New Cart--------------------------")
    print("-------addToCart: ", session['cart'])

    # Check if the product is already in the cart
    found = False
    for item in session['cart']:
        if item['product_id'] == product_id:
            # Product already in cart, update quantity
            item['quantity'] += quantity
            found = True
            break

    if not found:
        # Product not in cart, append new item
        session['cart'].append({'product_id': product_id, 'name': productName.name, 'quantity': quantity})
    print(session)
    # print("Updated Cart:", session['cart'])
    return jsonify({'message': 'Product added to cart'})

@app.route("/dashboard", methods=['POST', 'GET'])
@login_required
def dash():
    cart_items = []
    if 'cart' in session:
        for item in session['cart']:
            product_id = item['product_id']
            quantity = item['quantity']
            name = item['name']
            price = Product.query.filter_by(id=product_id).first().price
            cart_items.append({"name" : name, "id" : product_id, "quantity" : quantity, "price" : price})

    return render_template("dashboard.html",
        username = str(current_user.firstname + " " + current_user.lastname),
        cart_items = cart_items,
        isAuthenticated = current_user.is_authenticated,
        email = current_user.email,
        num = current_user.phoneNum) 

@app.route("/adm")
def adm():
    session.clear()
    return redirect(url_for("home"))
@app.route("/removeFromCart/<int:product_id>", methods=["POST"])
@login_required
def removeFromCart(product_id):
    if 'cart' in session:
        # Iterate over cart items and remove the item with the given product_id
        session['cart'] = [item for item in session['cart'] if item['product_id'] != product_id]
    return redirect(url_for('dash'))

@app.route("/decrementCartItem/<product_id>", methods=["POST"])
@login_required
def decrementCartItem(product_id):
    product_id = int(product_id)
    print("triggered function- APP")
    if 'cart' in session:
        # Iterate over cart items and decrement the quantity of the item with the given product_id
        for item in session['cart']:
            if item['product_id'] == product_id:
                # print("Found: ", product_id)
                # Decrement quantity by one
                item['quantity'] -= 1
                if item['quantity'] <= 0:
                    # If quantity becomes zero or negative, remove the item from the cart
                    session['cart'].remove(item)
                break
        # print(session['cart'])
    return redirect(url_for('dash'))

@app.route("/incrementCartItem/<product_id>", methods=["POST"])
@login_required
def incrementCartItem(product_id):
    print("triggered function- APP")
    product_id = int(product_id)
    if 'cart' in session:
        for item in session['cart']:
            if item['product_id'] == product_id:
                item['quantity'] += 1
                break
    print(session)
    # Redirect to the 'dash' route after updating the cart
    return redirect(url_for('dash'))

@app.route("/products/view/id=<product_id>", methods=["POST", "GET"])
def individualProduct(product_id):
    if request.method == "POST":
        if current_user.is_authenticated == False:
            flash("To enjoy our site's full features, such as having your own cart and submitting reviews, please sign in")
            return redirect(url_for('signup'))
        # Process form submission
        reviewBody = request.form["review-review"]
        reviewEmail = current_user.email
        reviewName = current_user.firstname +" " + current_user.lastname
        rating = int(request.form["rater"])
        print(reviewEmail, reviewBody, reviewName, rating)
        if current_user.is_authenticated == False:
            return redirect(url_for('individualProduct', product_id = product_id))
        if reviewBody == "" or reviewEmail == "" or reviewName == ""  or rating == "":
            print("Not submitted review")
            # Redirect to the same page using the GET method
            return redirect(url_for("individualProduct", product_id = product_id))
        else:
            # Add review to the database
            newReview = Review(product_id, reviewBody, rating, reviewName, reviewEmail)
            db.session.add(newReview)
            db.session.commit()

            # Update product rating
            product = Product.query.get(product_id)
            print(product.rating)
            product.rates += 1
            product.rating = (product.rating*(product.rates-1) + rating)/product.rates
            print(product.rates, product.rating)
            db.session.commit()

            print("Review added")
            # Redirect to the same page using the GET method
            return redirect(url_for("individualProduct", product_id = product_id))

    # For GET requests, render the page
    contextProduct = Product.query.filter_by(id=product_id).first()
    reviewsList = Review.query.filter_by(contextProductId=product_id).limit(3).all()

    return render_template("individual.html", isAuthenticated=current_user.is_authenticated,
                           productID=product_id,
                           name=contextProduct.name, price=contextProduct.price,
                           description=contextProduct.description, specs=contextProduct.specs,
                           img1=url_for('static', filename=f'{contextProduct.img1}'),
                           img2=url_for('static', filename=f'{contextProduct.img2}'),
                           img3=url_for('static', filename=f"{contextProduct.img3}"),
                           img4=url_for('static', filename=f"{contextProduct.img4}"),
                           stars=round(contextProduct.rating, 2), reviews=contextProduct.rates, reviewList=reviewsList, stock = contextProduct.availableUnits)

@app.route("/catalogue/product=<category>", methods=['POST', 'GET'])
def catalogue(category):
    prodList = Product.query.filter_by(category=category)
    pakkaList = prodList[2:5]
    print(pakkaList)
    if request.method == 'POST':
        #Filtering
        maxPrice = request.form["maxPrice"]
        minPrice = request.form["minPrice"]
        if maxPrice != "":
            prodList = [items for items in prodList if items.price <= int(maxPrice)]
        if minPrice != "":
            prodList = [items for items in prodList if items.price >= int(minPrice)]
        try:
            rating = request.form['rating']
            prodList = [items for items in prodList if items.rating >= int(rating)]
        except:
            print("Couldn't find rating")
        print(prodList)

        #Sorting
        try:
            sortingOption = request.form['sort-option']
        except:
            sortingOption = '5'
        print(sortingOption, type(sortingOption))
        if sortingOption == '1':
            prodList = sorted(prodList, key = lambda product : product.name.lower())
        elif sortingOption == '2':
            prodList = sorted(prodList, key = lambda product : product.rating, reverse=True)
        elif sortingOption == '3':
            prodList = sorted(prodList, key = lambda product : product.price, reverse=True)
        elif sortingOption == '4':
            prodList = sorted(prodList, key = lambda product : product.price)
        else:
            pass #maa chudaye
        
        #Include Out Of Stock
        if "exclude out-of-stock" in request.form:
            prodList = [items for items in prodList if items.availableUnits != 0]
        print("------------Applied Shit---------------")
        print(prodList)
        return render_template('products.html', isAuthenticated=current_user.is_authenticated, prodList=prodList, category=category, pakkaList = pakkaList)
        # return redirect(url_for('catalogue', category = category, prodList = prodList) + "#filterSortForm")


    return render_template('products.html', isAuthenticated=current_user.is_authenticated, prodList=prodList, category=category, pakkaList = pakkaList)
    
@app.route("/checkout", methods=['POST', 'GET'])
@login_required
def checkout():
    if 'cart' not in session or len(session['cart']) == 0:
        print("khali hai re")
        flash("Please add atleast one item to cart to proceed to checkout")
        return redirect(url_for('dash'))

    bill = []
    for items in session['cart']:
        if items['quantity'] > Product.query.get(items['product_id']).availableUnits:
            flash(f"It appears you are ordering items in a quantity greater than whats available at the moment. Item: {items['name']} - Quantity: {items['quantity']}")
            return redirect(url_for('dash'))
        bill.append({
        'id' : items['product_id'], 'quantity' : items['quantity'],
        'imgurl' : url_for('static', filename=f"{Product.query.filter_by(id=items['product_id']).first().img1}"),
        'price' : Product.query.filter_by(id=items['product_id']).first().price
        })

    cartPrice = sum((items['price'] * items['quantity'] )for items in bill)
    shippingPrice = sum(items['quantity'] for items in bill) * 1000
    finalPrice = cartPrice * 1.18


    if request.method == 'POST':

        cart_dict = {item['id']: item['quantity'] for item in bill}
        print(cart_dict)
        for items in cart_dict:
            print(items)
            updateItem = Product.query.get(items)
            print(updateItem)
            updateItem.availableUnits -= cart_dict[items]
            print(updateItem)
            updateItem.unitSold += cart_dict[items]

        db.session.commit()
        addToExcel(round(finalPrice, 2), datetime.now(), cart_dict, current_user.email, current_user.phoneNum)
        session.pop('cart')
        return render_template("arigato.html", isAuthenticated = current_user.is_authenticated, name = current_user.firstname, founderName = random.choice(["Parth Acharya", "Atharva Ghadigaonkar", 'Krish Patel', "Zayaan Shaikh"]))

    return render_template("checkout.html", isAuthenticated = current_user.is_authenticated, cart = bill,
    cartPrice = cartPrice, finalPrice = round(finalPrice, 2), shippingPrice = shippingPrice)

@app.route("/about")
def about():
    return render_template("about.html", isAuthenticated = current_user.is_authenticated)

@app.route("/contact", methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phoneNum = request.form['phoneNum']
        comment = request.form['comment']
        try:
            addContact(name, email, phoneNum, comment, datetime.now())
            flash("Thank you for submitting your comment, we appreciate your feedback!")
        except PermissionError:
            print("File in use")

        return redirect(url_for('contact'))
    return render_template("contact.html", isAuthenticated = current_user.is_authenticated)

@app.route("/warehouse", methods=["POST", "GET"])
def warehouse():
    return render_template("inventory.html", products = Product.query.all())

@app.route("/inventory-manager", methods=["POST", "GET"])
def inventoryManager():
    print("CALLED")
    product = request.form.get('product')
    increment_quantity = request.form.get('incrementQuantity')
    hard_update_value = request.form.get('hardUpdateValue')
    print(increment_quantity, hard_update_value)
    if increment_quantity == None and hard_update_value == None:
        flash("ERROR: BOTH FIELDS CANNOT BE EMPTY")
        return redirect(url_for('warehouse'))

    contextProduct = Product.query.filter_by(name=product).first()

    if increment_quantity != None:
        contextProduct.availableUnits += int(increment_quantity)
        flash(f"COMMITTED NORMAL RESTOCK ON {product}, UNITS ADDED: {increment_quantity}", "info")
        print("RESTOCKED")
    else:
        contextProduct.availableUnits = int(hard_update_value)
        flash(f"COMMITTED HARD-UPDATE ON {product}, UNITS: {hard_update_value}", "info")
        print("HARD-UPDATED")

    db.session.commit()
    return redirect(url_for('warehouse'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
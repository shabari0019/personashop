import random

import pandas as pd
from flask import Flask, render_template, request, flash, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from keras.models import load_model
from sqlalchemy import LargeBinary
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from flask_bootstrap import Bootstrap
from werkzeug.utils import redirect
from sklearn.preprocessing import LabelEncoder
from collections import defaultdict
import requests
import csv
app = Flask(__name__)

bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] ="dskajfhdsaljf231iwuef"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    photo = db.Column(LargeBinary)

class Product(db.Model):
    __tablename__ = "items"
    p_id = db.Column(db.Integer,primary_key=True)
    p_image = db.Column(db.String(300))
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    price = db.Column(db.Integer)
    category = db.Column(db.String(10))
    sales = db.Column(db.Integer)

class Location(db.Model):
    p_id = db.Column(db.Integer, primary_key=True)
    p_image = db.Column(db.String(300))
    gender = db.Column(db.String(10))
    category = db.Column(db.String(10))
    price = db.Column(db.Integer)
    temp = db.Column(db.Integer)

# db.create_all()

@app.route("/cart/<int:p_id>",methods=["GET","POST"])
def cart(p_id):
    buy = Product.query.get(p_id)
    buy.sales = buy.sales+1
    db.session.commit()
    return render_template("thank.html")
@app.route("/sumne")
def sumne():
    return render_template("sumne.html")


@app.route('/get_location', methods=['POST'])
def get_location():
    data = request.get_json()


    latitude = data.get('latitude')
    longitude = data.get('longitude')
    print(latitude)

    url = "http://api.weatherapi.com/v1/current.json"


    querystring = {"q": f"{latitude},{longitude}", "key": "5a0dcfb8b1a54edbaa015818230908"}

    re = requests.get(url, params=querystring)
    response = re.json()

    temp=response["current"]["temp_c"]
    print(temp)
    user_gender_w = current_user.gender
    temprature = {20: [0, 20], 25: [20, 25], 30: [25, 30], 35: [30, 35]}
    data = pd.read_csv("weather.csv")
    for key, value in temprature.items():
        if temp >= value[0] and temp <= value[1]:
            target_temperature = key
            break

    target_gender = user_gender_w
    matching_product_ids = []
    with open('weather.csv', 'r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            gender = row['gender']
            temperature = float(row['temperature'])

            if gender == target_gender and temperature == target_temperature:
                matching_product_ids.append(row['p_id'])


    products = {"temp": matching_product_ids}
    return redirect(url_for('home', **products))








@app.route("/display_items/<string:name>")
def display_items(name):
    items = Product.query.filter_by(category =name)
    print(items)
    return render_template("display.html",items=items)

@app.route("/display/<string:name>")
def display(name):
    items = Product.query.filter_by(gender=name)
    print(items)
    return render_template("display.html",items=items)

@app.route("/")
def home():


    if current_user.is_authenticated:


        user_age = current_user.age
        user_gender_w = current_user.gender
        if user_gender_w =="Male":
            user_gender=1
            g = range(11,21)
        else:
            user_gender=0
            g = range(41,51)
        print(user_gender)
        print(user_age)
        location_based = []


        for product_id in g:
            id = Location.query.get(product_id)
            location_based.append(id)

        x=[]
        for i in range(1,161):
            z = Product.query.get(i)
            x.append(z.sales)

        data = pd.read_csv('mini.csv')
        label_encoder = LabelEncoder()
        data['Gender'] = label_encoder.fit_transform(data['Gender'])
        data['Sales'] = x

        age_gender_units = defaultdict(lambda: defaultdict(int))
        for index, row in data.iterrows():
            age_gender_units[row['Age']][row['Gender']] += row['Sales']
        from collections import Counter

        def recommend(age, gender):
            product_counter = Counter()

            for index, row in data.iterrows():
                if row['Age'] == age and row['Gender'] == gender:
                    product_counter[row['Id']] += row['Sales']

            recommended_products = product_counter.most_common()
            return [product for product, _ in recommended_products]

        rp = recommend(user_age, user_gender)

        recommended_products=[]
        for product in rp:
            id = Product.query.get(product)
            recommended_products.append(id)





        return render_template("index1.html", current_user=current_user,l = location_based,p=recommended_products[:6])




    return render_template("index.html",current_user=current_user)

#
# @app.route("/add")
# def add():
#     data1 = pd.read_csv("mini.csv")
#
#     data1 = pd.DataFrame(data1)
#     Genders = data1["Gender"].values
#     Ages = data1["Age"].values
#     Link = data1["Link"].values
#     Price = data1['Price'].values
#     Category = data1['Category'].values
#     Sales = data1['Sales'].values
#
#     for i in range(160):
#         new_item = Product(p_image=Link[i],gender=Genders[i],age=int(Ages[i]),price=int(Price[i]),category=Category[i],sales=int(Sales[i]))
#         db.session.add(new_item)
#         db.session.commit()
#     data2 = pd.read_csv("weather.csv")
#
#     data2 = pd.DataFrame(data2)
#     Genders = data2["gender"].values
#     Link = data2["link"].values
#     Price = data2['price'].values
#     Category = data2['category'].values
#     temp = data2['temperature']
#     for i in range(60):
#         new_item = Location(p_image=Link[i],gender=Genders[i],price=int(Price[i]),category=Category[i],temp=int(temp[i]))
#         db.session.add(new_item)
#         db.session.commit()
#
#     return "add sucessful"


@app.route("/show_product/<int:p_id>",methods=["GET","POST"])
def show_product(p_id):
    requested_product = Product.query.get(p_id)
    return render_template("buy.html",id =requested_product)


@app.route("/sigup")
def signup():
    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route("/login",methods=["POST"])
def login():
    email = request.form['l-email']
    password = request.form['l-password']

    user = User.query.filter_by(email=email).first()
    # Email doesn't exist or password incorrect.
    if not user:
        flash("That email does not exist, please try again.")
        return redirect(url_for('login'))
    elif not check_password_hash(user.password, password):
        flash('Password incorrect, please try again.')
        return redirect(url_for('login'))
    else:
        login_user(user)
        return redirect(url_for('home'))


@app.route("/process",methods=['POST'])
def process():
    ages = {20:[20,24],25:[25,29],30:[30,34],35:[35,39],40:[40,45]}
    name = request.form['name']
    email = request.form['email']
    photo = request.files['photo']
    password = request.form['password']
    hash_and_salted_password = generate_password_hash(
        password,
        method='pbkdf2:sha256',
        salt_length=8
    )

    photo.save('static/images/'+name+'.jpg')
    image = photo.read()


    model = load_model('age_gender.h5')
    gender_dict = {0: 'Male', 1: 'Female'}


    image_path = 'static/images/'+name+'.jpg'
    image = load_img(image_path, target_size=(128, 128), grayscale=True)
    image = img_to_array(image)
    image = image.reshape(1, 128, 128, 1)
    image = image / 255.0
    pred = model.predict(image)
    print(pred)
    pred_gender = gender_dict[round(pred[0][0][0])]
    pred_age = round(pred[1][0][0])
    print("Predicted Gender:", pred_gender, "Predicted Age:", pred_age)
    actual_age = 0
    for key, value in ages.items():
        if pred_age >= value[0] and pred_age <= value[1]:
            actual_age = key
            break



    new_user = User(email=email,password=hash_and_salted_password,name=name,photo=image,age=int(actual_age),gender=pred_gender)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)

    return redirect(url_for('home'))




app.run(debug=True)
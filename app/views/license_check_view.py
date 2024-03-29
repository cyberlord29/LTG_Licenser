from app import app, db
from app.models import License, User, Product
from datetime import datetime
from flask import jsonify, request
from sqlalchemy import exc
import json


@app.route("/licenses/status")
def check_status():
    data = {
        "email": request.args.get("email", None),
        "product_id": request.args.get("product", None),
        "accountNumber": request.args.get("accountNumber", None)
    }
    required_params = ["email", "product_id", "accountNumber"]
    try:
        assert all(data[key] is not None for key in data)
        license = License.query.filter_by(email=data["email"],
                                          product_id=data["product_id"],
                                          accountNumber=data["accountNumber"]
                  ).first()
        if license is None:
            return jsonify({
                "msg": "User or license don't exist"
            }), 400
        output = license.to_dict()
        if datetime.utcnow() >= license.end_time:
            output["status"] = False
        else:
            output["status"] = True
        return jsonify(output), 200
    except AssertionError:
        return jsonify(
            {
                "msg": "{0} are required parameters"
                       .format(",".join(required_params))
            }
        ), 400

@app.route("/licenses/<product>/<accountNumber>", methods=["GET"])
def isValid(accountNumber,product):
    account_number=accountNumber
    prod = None
    prodisall = Product.query.get("all")
    prod1 = Product.query.get(product)
    if prod1 is None:
        prod = Product.query.get("all")
    if prod1 is not None and prodisall is not None:
        prod = prodisall
    license = License.query.filter_by(product_id=prod.id,account_number=accountNumber).first()
    if license is None:
        return jsonify({'status':'invalid key'}),401
    if prod is None :
        if license.account_number == accountNumber and Product.query.get('all').id==license.product_id :
            if datetime.utcnow() >= license.end_time:
                return jsonify({'status':'expired'}),401
            else:
                return jsonify({'status':'valid for all'}),200
        else:
            return jsonify({'status':'invalid product'}),401
    elif license.account_number == accountNumber and  ( Product.query.get('all').id == license.product_id or prod.id == license.product_id  ) :
        if datetime.utcnow() >= license.end_time:
            return jsonify({'status':'expired'}),401
        else:
            return jsonify({'status':'valid'}), 200
    else:
        return jsonify({'status':'invalid'}),401
    

@app.route("/licenses", methods=["GET"])
def list_licenses():
    data = [license.to_dict() for license in License.query.all()]
    return jsonify(data), 200


@app.route("/licenses/<id>", methods=["GET"])
def get_license(id):
    license = License.query.get(id)
    if license is None:
        return jsonify(
            {
                "msg": "License not found."
            }, 404
        )
    return jsonify(license.to_dict()), 200

@app.route("/licenses", methods=["DELETE"])
def delete_license():
    data = request.get_json()
    required_params = ["id"]
    try:
        assert all(param in data for param in required_params)
        license = License.query.get(data["id"])
        if license is None:
            return jsonify(
                {
                    "msg":"License not found"
                }, 404
            )
        else:
            db.session.delete(license)
            db.session.commit()
            return jsonify({"msg":"License Deleted"}), 200
    except AssertionError:
        print('errorAssert')
    except exc.IntegrityError:
        print('errorInt')

@app.route("/licenses", methods=["PATCH"])
def modify_license():
    data = request.get_json()
    required_params = [ "id", "email", "productName", "startTime", "endTime", "accountNumber","firstName","lastName"]
    try:
        assert all(param in data for param in required_params)
        license = License.query.get(data["id"])
        product = Product.query.get(data["productName"])
        user = User.query.get(data["email"])
        print( license , product , user)
        if license is None:
            return jsonify(
                {
                    "msg":"License not found"
                }, 404
            )
        else:
            license.account_number=data["accountNumber"]
            license.end_time = datetime.utcfromtimestamp(int(data["endTime"]))
        print(Product.query.filter_by(id=license.product_id).first())
        if product != Product.query.filter_by(id=license.product_id).first():
            productNew = Product.query.get(data["productName"])
            if productNew is None : 
                new_product = Product(name=data["productName"],
                                    platform='na',
                                    version='na')
                db.session.add(new_product)
                db.session.commit()
                license.product_id = new_product.id
            else:
                license.product_id = productNew.id
        userNew = User.query.get(data["email"])
        if user != User.query.get(license.user_email) :
            if userNew is None : 
                new_user = User(email=data["email"],first_name=data["firstName"],last_name=data["lastName"])
                db.session.add(new_user)
                db.session.commit()
                license.user_email = new_user.email
            else:
                license.user_email = userNew.email
                userNew.first_name = data["firstName"]
                userNew.last_name = data["lastName"]
        db.session.commit()
        return jsonify({"msg":"License Modified"}), 200
    except AssertionError:
        print('errorAssert')
    except exc.IntegrityError:
        print('errorInt')


@app.route("/licenses", methods=["POST"])
def create_license():
    data = request.get_json()
    required_params = ["email", "productName", "startTime", "endTime", "accountNumber"]
    try:
        assert all(param in data for param in required_params)
        user = User.query.get(data["email"])
        product = Product.query.get(data["productName"])
        if user is None:
            data = request.get_json()
            required_params = ["email", "firstName", "lastName"]
            try:
                assert all(param in data for param in required_params)
                new_user = User(email=data["email"],first_name=data["firstName"],last_name=data["lastName"])
                db.session.add(new_user)
                db.session.commit()
                user = User.query.get(data["email"])
            except AssertionError:
                print('errorAssert')
            except exc.IntegrityError:
                print('errorInt')
        if product is None:
            data = request.get_json()
            required_params = ["productName"]
            try:
                assert all(param in data for param in required_params)
                new_product = Product(name=data["productName"],
                                    platform='na',
                                    version='na')
                db.session.add(new_product)
                db.session.commit()
            except AssertionError:
                print('errorAsert')
            except exc.IntegrityError:
                print('errorInt')  
        product = Product.query.get(data["productName"])
        user = User.query.get(data["email"])
        print(user,product)
        required_params = ["email", "productName", "startTime", "endTime", "accountNumber"]
        assert all(param in data for param in required_params)
        new_license = License(
            account_number=data["accountNumber"],
            user=user,
            product=product,
            start_time=datetime.utcfromtimestamp(int(data["startTime"])),
            end_time=datetime.utcfromtimestamp(int(data["endTime"]))
        )   
        print(new_license)
        db.session.add(new_license)
        db.session.commit()
        return jsonify({}), 201
    except AssertionError:
        return jsonify({
            "msg": "{0} are required params".format(required_params)
        }), 400
    except exc.IntegrityError:
        db.session.rollback()
        return jsonify({
            "msg": "A License for the product already exists"
        }), 400
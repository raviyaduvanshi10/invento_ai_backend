from flask import Flask
import os
import urllib.request
from flask import Flask, request, redirect, jsonify, render_template
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_cors import CORS
from flask_restful import Api, Resource
import bcrypt
from werkzeug import datastructures
from flask import request, jsonify
from flask.globals import request
from werkzeug import Client
from datetime import datetime


app = Flask(__name__)


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


CORS(app)
api = Api(app)

client = MongoClient(
    ['mongodb+srv://raviyaduvanshi:%23Izeetek100@cluster0.erpog.mongodb.net/?ssl=true&ssl_cert_reqs=CERT_NONE'])
# db = client.lin_flask
inventoDb = client["Invento_Database"]  # Creating 1st DB
izeetekDb = client["Izeetek_Database"]  # Creating 2nd DB
defelDb = client["Defel_Database"]  # Creating 3rd DB
# Creating 1st Collection in 1st DB
clientCredential = inventoDb["Client Credential"]
webuserCredential = inventoDb["Web Users"]
appuserCredential = inventoDb["App Users"]


@app.route('/')
def index():
    return render_template('home.html')


class Admins(Resource):
    def post(self):
        registerJson = request.get_json(force=True)
        clientName = registerJson["clientName"]
        emailId = registerJson["emailId"]
        mobile = registerJson["mobile"]
        userName = registerJson["userName"]
        password = registerJson["password"]
        hash_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        clientCredential.insert({
            "clientName": clientName,
            "emailId": emailId,
            "mobile": mobile,
            "userName": userName,
            "password": hash_pw,
            "token": 100
        })
        return jsonify({
            "clientName": clientName,
            "emailId": emailId,
            "mobile": mobile,
            "status": 200,
            "message": "Hi "+clientName+"! you are registered successfully.",
            "token": 100
        })

    def get(self):
        allData = clientCredential.find()
        adminJson = []
        for data in allData:
            id = data["_id"]
            clientName = data["clientName"]
            clientDict = {
                "id": str(id),
                "clientName": clientName
            }
            adminJson.append(clientDict)
            print(adminJson)
        return jsonify(adminJson)


def varifyAdmin(userName, password):
    hashed_pw = clientCredential.find({
        "userName": userName
    })[0]["password"]
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        False


def countTokens(userName):
    tokens = clientCredential.find({
        "userName": userName
    })[0]["token"]
    return tokens


class AdminLogin(Resource):
    def post(self):
        registerJson = request.get_json(force=True)
        userName = registerJson["userName"]
        password = registerJson["password"]

        correct_pw = varifyAdmin(userName, password)
        if not correct_pw:
            return jsonify({
                "status": 302,
                "message": "Password is not correct."
            })
        num_Of_Token = countTokens(userName)
        print("Tokens :", num_Of_Token)
        if num_Of_Token <= 0:
            return jsonify({
                "Status Code": 302,
                "Message": "Tokens Exhausted"
            })
        clientCredential.update({
            "userName": userName
        },
            {
            "$set": {
                "token": num_Of_Token - 1
            }
        })
        _id = clientCredential.find({
            "userName": userName
        })[0]["_id"]
        clientName = clientCredential.find({
            "userName": userName
        })[0]["clientName"]

        return jsonify({
            "status": 200,
            "message": "Hi "+userName + "! you are logged in successfully as admin",
            "id": str(_id),
            "userName": userName,
            "name": clientName
        })


class AppUsers(Resource):
    def post(self, id):
        postedData = request.get_json(force=True)
        userName = postedData["userName"]
        password = postedData["password"]
        roles = postedData["roles"]

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        appuserCredential.insert({
            "clientId": id,
            "userName": userName,
            "password": hashed_pw,
            "roles": roles,
            "tokens": 15
        })
        return jsonify({
            "clientId": id,
            "userName": userName,
            "roles": roles,
            "message": "User is registered successfully based on access_roles",
            "status": 200
        })
        # data = clientCredential.find_one({'_id': ObjectId(id)})
        # clientName = data["clientName"]
        # print(clientName)
        # if(clientName == "Defel"):
        #     defelDb["App Users"].insert({
        #         "username": username,
        #         "password": hashed_pw,
        #         "roles": roles,
        #         "tokens": 15
        #     })
        #     return jsonify({
        #         "Username": username,
        #         "Roles": roles,
        #         "Message": "User is registered successfully based on access_roles",
        #         "Status Code": 200
        #     })
        # elif(clientName == "Izeetek"):
        #     izeetekDb["App Users"].insert({
        #         "username": username,
        #         "password": hashed_pw,
        #         "roles": roles,
        #         "tokens": 15
        #     })
        #     return jsonify({
        #         "Username": username,
        #         "Roles": roles,
        #         "Message": "User is registered successfully based on access_roles",
        #         "Status Code": 200
        #     })

    def get(self, id):
        allData = appuserCredential.find()
        dataJson = []
        rolesJson = []
        for data in allData:
            appuserId = data['_id'],
            clientId = data['clientId']
            userName = data['userName']
            roles = data['roles']
            # rolesJson.append(roles)
            if clientId == id:
                dataDict = {
                    'appuserId': str(appuserId),
                    'clientId': clientId,
                    "userName": userName,
                    # "roles": rolesJson
                    "roles": roles
                }
                dataJson.append(dataDict)
        print(dataJson)
        return jsonify(dataJson)
        # data = clientCredential.find_one({'_id': ObjectId(id)})
        # clientName = data["clientName"]
        # print(clientName)

        # if(clientName == "Defel"):
        #     allData = defelDb["App Users"].find()
        #     dataJson = []
        #     rolesJson = []
        #     for data in allData:
        #         id = data['_id']
        #         username = data['username']
        #         roles = data['roles']
        #         # rolesJson.append(roles)
        #         dataDict = {
        #             'id': str(id),
        #             "username": username,
        #             # "roles": rolesJson,
        #             "roles": roles
        #         }
        #         dataJson.append(dataDict)
        #     print(dataJson)
        #     return jsonify(dataJson)
        # elif(clientName == "Izeetek"):
        #     allData = izeetekDb["App Users"].find()
        #     dataJson = []
        #     rolesJson = []
        #     for data in allData:
        #         id = data['_id']
        #         username = data['username']
        #         roles = data['roles']
        #         # rolesJson.append(roles)
        #         dataDict = {
        #             'id': str(id),
        #             "username": username,
        #             # "roles": rolesJson,
        #             "roles": roles
        #         }
        #         dataJson.append(dataDict)
        #     print(dataJson)
        #     return jsonify(dataJson)


def varifyAppuser(userName, password):
    hashed_pw = appuserCredential.find({
        "userName": userName
    })[0]["password"]
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        False


class AppuserLogin(Resource):
    def post(self):
        appUser = request.get_json(force=True)
        userName = appUser["userName"]
        password = appUser["password"]
        correct_pw = varifyAppuser(userName, password)
        if not correct_pw:
            return jsonify({
                "status": 302,
                "message": "Password is not correct."
            })

        clientId = appuserCredential.find({
            "userName": userName
        })[0]["clientId"]
        roles = appuserCredential.find({
            "userName": userName
        })[0]["roles"]

        return jsonify({
            "status": 200,
            "message": "Hi "+userName + "! you are logged in successfully as webuser",
            "id": clientId,
            "name": userName,
            "roles": roles
        })


class WebUsers(Resource):
    def post(self, id):
        postedData = request.get_json(force=True)
        # data = clientCredential.find_one({'_id': ObjectId(id)})

        userName = postedData["userName"]
        password = postedData["password"]
        mobile = postedData["mobile"]
        emailId = postedData["emailId"]
        employeeId = postedData["employeeId"]
        departmentType = postedData["departmentType"]
        location = postedData["location"]
        state = postedData["state"]
        city = postedData["city"]
        address = postedData["address"]
        roles = postedData["roles"]
        photo = postedData["photo"]

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        webuserCredential.insert({
            "clientId": id,
            "userName": userName,
            "password": hashed_pw,
            "mobile": mobile,
            "emailId": emailId,
            "employeeId": employeeId,
            "departmentType": departmentType,
            "location": location,
            "state": state,
            "city": city,
            "address": address,
            "roles": roles,
            "photo": photo,
            "tokens": 20
        })
        return jsonify({
            "clientId": id,
            "userName": userName,
            "mobile": mobile,
            "emailId": emailId,
            "employeeId": employeeId,
            "department Type": departmentType,
            "location": location,
            "State": state,
            "city": city,
            "dddress": address,
            "roles": roles,
            "photo": photo,
            "ability": "Web_User is registered successfully.",
            "status": 200
        })

    def get(self, id):
        # data = clientCredential.find_one({'clientId': id})
        # clientName = data["clientName"]
        # print(clientName)

        # if(clientName == "Izeetek"):
        allData = webuserCredential.find()
        dataJson = []
        rolesJson = []
        for data in allData:
            webuserId = data['_id'],
            clientId = data['clientId']
            userName = data['userName']
            roles = data['roles']
            # rolesJson.append(roles)
            if clientId == id:
                dataDict = {
                    'webuserId': str(webuserId),
                    'clientId': clientId,
                    "userName": userName,
                    # "roles": rolesJson
                    "roles": roles
                }
                dataJson.append(dataDict)
        print(dataJson)
        return jsonify(dataJson)

        # elif(clientName == "Defel"):
        #     allData = defelDb["Web Users"].find()
        #     dataJson = []
        #     # rolesJson = []
        #     for data in allData:
        #         id = data['_id']
        #         userName = data['userName']
        #         roles = data['roles']
        #         # rolesJson.append(roles)
        #         dataDict = {
        #             'id': str(id),
        #             "userName": userName,
        #             # "roles": rolesJson.
        #             'roles': roles
        #         }
        #         dataJson.append(dataDict)
        #     print(dataJson)
        #     return jsonify(dataJson)

    def delete(self, id):
        print(id)
        a_string = id
        split_strings = []
        n = 24
        for index in range(0, len(a_string), n):
            split_strings.append(a_string[index: index + n])

        adminId = split_strings[0]
        webuserId = split_strings[1]
        print("admin: ", adminId, " webuser: ", webuserId)
        data = clientCredential.find_one({'_id': ObjectId(adminId)})
        clientName = data["clientName"]
        print(clientName)
        if clientName == "Defel":
            defelDb['Web Users'].delete_many({'_id': ObjectId(webuserId)})
            print('\n # Deletion successful # \n')
            return jsonify({
                'status': 'Data id: ' + webuserId + ' is deleted!'
            })
        elif clientName == "Izeetek":
            izeetekDb['Web Users'].delete_many({'_id': ObjectId(webuserId)})
            print('\n # Deletion successful # \n')
            return jsonify({
                'status': 'Data id: ' + webuserId + ' is deleted!'
            })


def varifyWebuser(userName, password):
    hashed_pw = webuserCredential.find({
        "userName": userName
    })[0]["password"]
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        False


# def varifyIzeetekWebuser(userName, password):
#     hashed_pw = izeetekDb["Web Users"].find({
#         "userName": userName
#     })[0]["password"]
#     if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
#         return True
#     else:
#         False


# def countDefelWebuserTokens(userName):
#     tokens = clientCredential.find({
#         "userName": userName
#     })[0]["token"]
#     return tokens


class WebuserLogin(Resource):
    def post(self):
        webUser = request.get_json(force=True)
        userName = webUser["userName"]
        password = webUser["password"]
        correct_pw = varifyWebuser(userName, password)
        if not correct_pw:
            return jsonify({
                "status": 302,
                "message": "Password is not correct."
            })

        clientId = webuserCredential.find({
            "userName": userName
        })[0]["clientId"]
        roles = webuserCredential.find({
            "userName": userName
        })[0]["roles"]

        return jsonify({
            "status": 200,
            "message": "Hi "+userName + "! you are logged in successfully as webuser",
            "id": clientId,
            "name": userName,
            "roles": roles
        })
        # data = clientCredential.find_one({'_id': ObjectId(id)})
        # clientName = data["clientName"]
        # print(clientName)
        # if clientName == "Defel":
        #     correct_pw = varifyDefelWebuser(userName, password)
        #     if not correct_pw:
        #         return jsonify({
        #             "status": 302,
        #             "message": "Password is not correct."
        #         })
        #     roles = defelDb["Web Users"].find({
        #         "userName": userName
        #     })[0]["_id"]
        #     roles = defelDb["Web Users"].find({
        #         "userName": userName
        #     })[0]["roles"]

        #     return jsonify({
        #         "status": 200,
        #         "message": "Hi "+userName + "! you are logged in successfully as webuser",
        #         "id": id,
        #         "name": userName,
        #         "roles": roles
        #     })
        # elif clientName == "Izeetek":
        #     correct_pw = varifyIzeetekWebuser(userName, password)
        #     if not correct_pw:
        #         return jsonify({
        #             "status": 302,
        #             "message": "Password is not correct."
        #         })
        #     roles = izeetekDb["Web Users"].find({
        #         "userName": userName
        #     })[0]["_id"]
        #     roles = izeetekDb["Web Users"].find({
        #         "userName": userName
        #     })[0]["roles"]

        #     return jsonify({
        #         "status": 200,
        #         "message": "Hi "+userName + "! you are logged in successfully as webuser",
        #         "id": id,
        #         "name": userName,
        #         "roles": roles
        #     })


class Inventory(Resource):
    def post(self, id):
        postedData = request.get_json(force=True)
        actyArea = postedData["actyArea"]
        batch = postedData["batch"]
        # binNo = postedData["binNo"]
        bookQuantity = postedData["bookQuantity"]
        counter = postedData["counter"]
        hghLvlHU = postedData["hghLvlHU"]
        item = postedData["item"]
        # phyInvDoc = postedData["phyInvDoc"]
        piStatus = postedData["piStatus"]
        procedure = postedData["procedure"]
        prodDesc = postedData["prodDesc"]
        product = postedData["product"]
        phyInvDoc = "|| Doc No #"+str(postedData["phyInvDoc"])
        binNo = "BIN-S001-01-"+str(postedData["binNo"])
        now = datetime.now()
        date = now.strftime("%Y/%m/%d")
        time = now.strftime("%H:%M")

        data = clientCredential.find_one({'_id': ObjectId(id)})
        clientName = data["clientName"]
        print(clientName)
        if(clientName == 'Izeetek'):
            izeetekDb["Inventory"].insert_one({
                "date": date,
                "time": time,
                "actyArea": actyArea,
                "batch": batch,
                "bookQuantity": bookQuantity,
                "counter": counter,
                "hghLvlHU": hghLvlHU,
                "item": item,
                "piStatus": piStatus,
                "procedure": procedure,
                "prodDesc": prodDesc,
                "product": product,
                "phyInvDoc": phyInvDoc,
                "binNo": binNo,
                "cntdQty": "--",
                "diffQty": "--",
                "bun": "--",
                "diffValue": "--",
                "crcy": "--",
                "diffTrgt": "--",
                "snDesc": "--"
            })
            return jsonify({
                "date": date,
                "time": time,
                "actyArea": actyArea,
                "batch": batch,
                "bookQuantity": bookQuantity,
                "counter": counter,
                "hghLvlHU": hghLvlHU,
                "item": item,
                "piStatus": piStatus,
                "procedure": procedure,
                "prodDesc": prodDesc,
                "product": product,
                "phyInvDoc": phyInvDoc,
                "binNo": binNo,
                "cntdQty": "--",
                "diffQty": "--",
                "bun": "--",
                "diffValue": "--",
                "crcy": "--",
                "diffTrgt": "--",
                "snDesc": "--",
                "Message": "Data is posted in inventory collection",
                "Status Code": 200
            })

        elif(clientName == 'Defel'):
            defelDb["Inventory"].insert_one({
                "date": date,
                "time": time,
                "actyArea": actyArea,
                "batch": batch,
                "bookQuantity": bookQuantity,
                "counter": counter,
                "hghLvlHU": hghLvlHU,
                "item": item,
                "piStatus": piStatus,
                "procedure": procedure,
                "prodDesc": prodDesc,
                "product": product,
                "phyInvDoc": phyInvDoc,
                "binNo": binNo,
                "cntdQty": "--",
                "diffQty": "--",
                "bun": "--",
                "diffValue": "--",
                "crcy": "--",
                "diffTrgt": "--",
                "snDesc": "--"
            })
            return jsonify({
                "date": date,
                "time": time,
                "actyArea": actyArea,
                "batch": batch,
                "bookQuantity": bookQuantity,
                "counter": counter,
                "hghLvlHU": hghLvlHU,
                "item": item,
                "piStatus": piStatus,
                "procedure": procedure,
                "prodDesc": prodDesc,
                "product": product,
                "phyInvDoc": phyInvDoc,
                "binNo": binNo,
                "cntdQty": "--",
                "diffQty": "--",
                "bun": "--",
                "diffValue": "--",
                "crcy": "--",
                "diffTrgt": "--",
                "snDesc": "--",
                "Message": "Data is posted in inventory collection",
                "Status Code": 200
            })

    def get(self, id):
        data = clientCredential.find_one({'_id': ObjectId(id)})
        clientName = data["clientName"]
        print(clientName)
        if(clientName == "Izeetek"):
            allData = izeetekDb["Inventory"].find()
            dataJson = []
            for data in allData:
                id = data['_id']
                date = data["date"]
                time = data["time"]
                actyArea = data["actyArea"]
                batch = data["batch"]
                bookQuantity = data["bookQuantity"]
                counter = data["counter"]
                hghLvlHU = data["hghLvlHU"]
                item = data["item"]
                piStatus = data["piStatus"]
                procedure = data["procedure"]
                prodDesc = data["prodDesc"]
                product = data["product"]
                phyInvDoc = data["phyInvDoc"]
                binNo = data["binNo"]
                cntdQty = data["cntdQty"]
                diffQty = data["diffQty"]
                bun = data["bun"]
                diffValue = data["diffValue"]
                crcy = data["crcy"]
                diffTrgt = data["diffTrgt"]
                snDesc = data["snDesc"]

                dataDict = {
                    "id": str(id),
                    "date": date,
                    "time": time,
                    "actyArea": actyArea,
                    "batch": batch,
                    "bookQuantity": bookQuantity,
                    "counter": counter,
                    "hghLvlHU": hghLvlHU,
                    "item": item,
                    "piStatus": piStatus,
                    "procedure": procedure,
                    "prodDesc": prodDesc,
                    "product": product,
                    "phyInvDoc": phyInvDoc,
                    "binNo": binNo,
                    "cntdQty": cntdQty,
                    "diffQty": diffQty,
                    "bun": bun,
                    "diffValue": diffValue,
                    "crcy": crcy,
                    "diffTrgt": diffTrgt,
                    "snDesc": snDesc,
                }
                dataJson.append(dataDict)
            print(dataJson)
            return jsonify(dataJson)
        elif(clientName == "Defel"):
            allData = defelDb["Inventory"].find()
            dataJson = []
            for data in allData:
                id = data['_id']
                date = data["date"]
                time = data["time"]
                actyArea = data["actyArea"]
                batch = data["batch"]
                bookQuantity = data["bookQuantity"]
                counter = data["counter"]
                hghLvlHU = data["hghLvlHU"]
                item = data["item"]
                piStatus = data["piStatus"]
                procedure = data["procedure"]
                prodDesc = data["prodDesc"]
                product = data["product"]
                phyInvDoc = data["phyInvDoc"]
                binNo = data["binNo"]
                cntdQty = data["cntdQty"]
                diffQty = data["diffQty"]
                bun = data["bun"]
                diffValue = data["diffValue"]
                crcy = data["crcy"]
                diffTrgt = data["diffTrgt"]
                snDesc = data["snDesc"]

                dataDict = {
                    "id": str(id),
                    "date": date,
                    "time": time,
                    "actyArea": actyArea,
                    "batch": batch,
                    "bookQuantity": bookQuantity,
                    "counter": counter,
                    "hghLvlHU": hghLvlHU,
                    "item": item,
                    "piStatus": piStatus,
                    "procedure": procedure,
                    "prodDesc": prodDesc,
                    "product": product,
                    "phyInvDoc": phyInvDoc,
                    "binNo": binNo,
                    "cntdQty": cntdQty,
                    "diffQty": diffQty,
                    "bun": bun,
                    "diffValue": diffValue,
                    "crcy": crcy,
                    "diffTrgt": diffTrgt,
                    "snDesc": snDesc
                }
                dataJson.append(dataDict)
            print(dataJson)
            return jsonify(dataJson)


class Barcodes(Resource):
    def post(self, id):
        postedData = request.get_json(force=True)
        date = postedData["date"]
        businessLocation = postedData["businessLocation"]
        inboundScan = postedData["inboundScan"]
        outboundScan = postedData["outboundScan"]
        internalScan = postedData["internalScan"]

        data = clientCredential.find_one({'_id': ObjectId(id)})
        clientName = data["clientName"]
        print(clientName)
        if(clientName == "Izeetek"):
            izeetekDb["Barcodes"].insert({
                "date": date,
                "businessLocation": businessLocation,
                "inboundScan": inboundScan,
                "outboundScan": outboundScan,
                "internalScan": internalScan
            })
            return jsonify({
                "Date": date,
                "Business Location": businessLocation,
                "Inbound Scan": inboundScan,
                "Outbound Scan": outboundScan,
                "Internal Scan": internalScan,
                "Message": "Data is posted in barcodes collection",
                "Status Code": 200
            })
        elif(clientName == "Defel"):
            defelDb["Barcodes"].insert({
                "date": date,
                "businessLocation": businessLocation,
                "inboundScan": inboundScan,
                "outboundScan": outboundScan,
                "internalScan": internalScan
            })
            return jsonify({
                "Date": date,
                "Business Location": businessLocation,
                "Inbound Scan": inboundScan,
                "Outbound Scan": outboundScan,
                "Internal Scan": internalScan,
                "Message": "Data is posted in barcodes collection"
            })

    def get(self, id):
        data = clientCredential.find_one({'_id': ObjectId(id)})
        clientName = data["clientName"]
        print(clientName)
        if(clientName == "Izeetek"):
            allData = izeetekDb["Barcodes"].find()
            dataJson = []
            for data in allData:
                id = data['_id']
                date = data["date"]
                businessLocation = data["businessLocation"]
                inboundScan = data["inboundScan"]
                outboundScan = data["outboundScan"]
                internalScan = data["internalScan"]

                dataDict = {
                    "id": str(id),
                    "date": date,
                    "businessLocation": businessLocation,
                    "inboundScan": inboundScan,
                    "outboundScan": outboundScan,
                    "internalScan": internalScan
                }
                dataJson.append(dataDict)
            print(dataJson)
            return jsonify(dataJson)

        elif(clientName == "Defel"):
            allData = defelDb["Barcodes"].find()
            dataJson = []
            for data in allData:
                id = data['_id']
                date = data["date"]
                businessLocation = data["businessLocation"]
                inboundScan = data["inboundScan"]
                outboundScan = data["outboundScan"]
                internalScan = data["internalScan"]

                dataDict = {
                    "id": str(id),
                    "date": date,
                    "businessLocation": businessLocation,
                    "inboundScan": inboundScan,
                    "outboundScan": outboundScan,
                    "internalScan": internalScan
                }
                dataJson.append(dataDict)
            print(dataJson)
            return jsonify(dataJson)


class Categories(Resource):
    def post(self, id):
        categoryJson = request.get_json(force=True)

        categoryId = categoryJson['categoryId']
        categoryName = categoryJson['categoryName']
        data = clientCredential.find_one({'_id': ObjectId(id)})
        clientName = data["clientName"]
        print(clientName)
        if clientName == "Defel":
            defelDb['Categories'].insert({
                "categoryId": categoryId,
                "categoryName": categoryName
            })
            return jsonify({
                'status': 'Data is posted to MongoDB!',
                'categoryId': categoryId,
                'categoryName': categoryName
            })
        elif clientName == "Izeetek":
            izeetekDb['Categories'].insert({
                "categoryId": categoryId,
                "categoryName": categoryName
            })
            return jsonify({
                'status': 'Data is posted to MongoDB!',
                'categoryId': categoryId,
                'categoryName': categoryName
            })

    def get(self, id):
        data = clientCredential.find_one({'_id': ObjectId(id)})
        clientName = data["clientName"]
        print(clientName)
        if clientName == "Defel":
            allData = defelDb['Categories'].find()
            dataJson = []
            for data in allData:
                id = data['_id']
                categoryId = data['categoryId']
                categoryName = data['categoryName']
                dataDict = {
                    'id': str(id),
                    'categoryId': categoryId,
                    'categoryName': categoryName
                }
                dataJson.append(dataDict)
            print(dataJson)
            return jsonify(dataJson)
        elif clientName == "Izeetek":
            allData = izeetekDb['Categories'].find()
            dataJson = []
            for data in allData:
                id = data['_id']
                categoryId = data['categoryId']
                categoryName = data['categoryName']
                dataDict = {
                    'id': str(id),
                    'categoryId': categoryId,
                    'categoryName': categoryName
                }
                dataJson.append(dataDict)
            print(dataJson)
            return jsonify(dataJson)


class Products(Resource):
    def post(self, id):
        body = request.get_json(force=True)
        productId = body['productId']
        productName = body['productName']
        categoryId = body['categoryId']
        categoryName = body['categoryName']
        data = clientCredential.find_one({'_id': ObjectId(id)})
        clientName = data["clientName"]
        if clientName == "Defel":
            defelDb['Products'].insert({
                "productId": productId,
                "productName": productName,
                "categoryId": categoryId,
                "categoryName": categoryName
            })
            return jsonify({
                'status': 'Data is posted to MongoDB!',
                'productId': productId,
                'productName': productName,
                'categoryId': categoryId,
                'categoryName': categoryName
            })
        elif clientName == "Izeetek":
            izeetekDb['Products'].insert({
                "productId": productId,
                "productName": productName,
                "categoryId": categoryId,
                "categoryName": categoryName
            })
            return jsonify({
                'status': 'Data is posted to MongoDB!',
                'productId': productId,
                'productName': productName,
                'categoryId': categoryId,
                'categoryName': categoryName
            })

    def get(self, id):
        data = clientCredential.find_one({'_id': ObjectId(id)})
        clientName = data["clientName"]
        if clientName == "Defel":
            allData = defelDb['Products'].find()
            dataJson = []
            for data in allData:
                id = data['_id']
                productId = data['productId']
                productName = data['productName']
                categoryId = data['categoryId']
                categoryName = data['categoryName']
                dataDict = {
                    'id': str(id),
                    'productId': productId,
                    'productName': productName,
                    'categoryId': categoryId,
                    'categoryName': categoryName
                }
                dataJson.append(dataDict)
            print(dataJson)
            return jsonify(dataJson)
        elif clientName == "Izeetek":
            allData = izeetekDb['Products'].find()
            dataJson = []
            for data in allData:
                id = data['_id']
                productId = data['productId']
                productName = data['productName']
                categoryId = data['categoryId']
                categoryName = data['categoryName']
                dataDict = {
                    'id': str(id),
                    'productId': productId,
                    'productName': productName,
                    'categoryId': categoryId,
                    'categoryName': categoryName
                }
                dataJson.append(dataDict)
            print(dataJson)
            return jsonify(dataJson)


class BusinessLocation(Resource):
    def post(self, id):
        businessJson = request.get_json(force=True)
        locationId = businessJson['locationId']
        locationName = businessJson['locationName']

        data = clientCredential.find_one({'_id': ObjectId(id)})
        clientName = data["clientName"]
        print(clientName)
        if clientName == "Defel":
            defelDb["Business Locations"].insert_one({
                "locationId": locationId,
                "locationName": locationName
            })
            return jsonify({
                'status': 'Data is posted to MongoDB!',
                'locationId': locationId,
                'locationName': locationName
            })
        elif clientName == "Izeetek":
            izeetekDb["Business Locations"].insert_one({
                "locationId": locationId,
                "locationName": locationName
            })
            return jsonify({
                'status': 'Data is posted to MongoDB!',
                'locationId': locationId,
                'locationName': locationName
            })

    def get(self, id):
        data = clientCredential.find_one({'_id': ObjectId(id)})
        clientName = data["clientName"]
        if clientName == "Defel":
            allData = defelDb['Business Locations'].find()
            dataJson = []
            for data in allData:
                id = data['_id']
                locationId = data['locationId']
                locationName = data['locationName']
                dataDict = {
                    'id': str(id),
                    'locationId': locationId,
                    'locationName': locationName
                }
                dataJson.append(dataDict)
            print(dataJson)
            return jsonify(dataJson)
        elif clientName == "Izeetek":
            allData = izeetekDb['Business Locations'].find()
            dataJson = []
            for data in allData:
                id = data['_id']
                locationId = data['locationId']
                locationName = data['locationName']
                dataDict = {
                    'id': str(id),
                    'locationId': locationId,
                    'locationName': locationName
                }
                dataJson.append(dataDict)
            print(dataJson)
            return jsonify(dataJson)


# class InventoryPending(Resource):
#     def post(self, id):
#         pendingData = request.get_json(force=True)
#         docNo = "|| Doc No #"+str(pendingData["docNo"])
#         binNo = "BIN-S001-01-"+str(pendingData["binNo"])
#         now = datetime.now()
#         date = now.strftime("%Y/%m/%d")
#         time = now.strftime("%H:%M")
#         clientName = data["clientName"]
#         print(clientName)
#         if(clientName == "Izeetek"):
#             izeetekDb['Inventory Pending'].insert({
#                 "docNo": docNo,
#                 "binNo": binNo,
#                 "date": date,
#                 "time": time
#             })
#             return jsonify({
#                 "docNo": docNo,
#                 "date": date,
#                 "time": time,
#                 "ability": "Product is stored successfully.",
#                 "status": 200
#             })
#         elif(clientName == "Defel"):
#             defelDb['Web Users'].insert({
#                 "userName": userName,
#                 "password": hashed_pw,
#                 "mobile": mobile,
#                 "emailId": emailId,
#                 "employeeId": employeeId,
#                 "departmentType": departmentType,
#                 "location": location,
#                 "state": state,
#                 "city": city,
#                 "address": address,
#                 "roles": roles,
#                 "photo": photo,
#                 "tokens": 20
#             })
#             return jsonify({
#                 "userName": userName,
#                 "mobile": mobile,
#                 "emailId": emailId,
#                 "employeeId": employeeId,
#                 "department Type": departmentType,
#                 "location": location,
#                 "State": state,
#                 "city": city,
#                 "dddress": address,
#                 "roles": roles,
#                 "photo": photo,
#                 "ability": "Web_User is registered successfully.",
#                 "status": 200
#             })

#     def get(self, id):
#         # data = clientCredential.find_one({'clientId': id})
#         # clientName = data["clientName"]
#         # print(clientName)

#         # if(clientName == "Izeetek"):
#         allData = webuserCredential.find()
#         dataJson = []
#         rolesJson = []
#         for data in allData:
#             webuserId = data['_id'],
#             clientId = data['clientId']
#             userName = data['userName']
#             roles = data['roles']
#             # rolesJson.append(roles)
#             if clientId == id:
#                 dataDict = {
#                     'webuserId': str(webuserId),
#                     'clientId': clientId,
#                     "userName": userName,
#                     # "roles": rolesJson
#                     "roles": roles
#                 }
#                 dataJson.append(dataDict)
#         print(dataJson)
#         return jsonify(dataJson)

        # elif(clientName == "Defel"):
        #     allData = defelDb["Web Users"].find()
        #     dataJson = []
        #     # rolesJson = []
        #     for data in allData:
        #         id = data['_id']
        #         userName = data['userName']
        #         roles = data['roles']
        #         # rolesJson.append(roles)
        #         dataDict = {
        #             'id': str(id),
        #             "userName": userName,
        #             # "roles": rolesJson.
        #             'roles': roles
        #         }
        #         dataJson.append(dataDict)
        #     print(dataJson)
        #     return jsonify(dataJson)

class ObjectCounted(Resource):
    def post(self, id):
        countedJson = request.get_json(force=True)
        countedObject = countedJson["countedObject"]
        binNo = countedJson["binNo"]
        data = clientCredential.find_one({'_id': ObjectId(id)})
        clientName = data["clientName"]
        print(clientName)
        if clientName == "Izeetek":
            bookQuantity = izeetekDb["Inventory"].find({
                "binNo": binNo
            })[0]["bookQuantity"]

            diffQty = int(bookQuantity) - int(countedObject)
            print(diffQty)

            izeetekDb["Inventory"].update({
                "binNo": binNo
            },
                {
                "$set": {
                    "cntdQty": countedObject,
                    "diffQty": diffQty
                }
            })
            print('\n # Update successful # \n')
            return jsonify({'status':  binNo + ' is updated!'})

        elif clientName == "Defel":
            bookQuantity = defelDb["Inventory"].find({
                "binNo": binNo
            })[0]["bookQuantity"]

            diffQty = int(bookQuantity) - int(countedObject)
            print(diffQty)

            defelDb["Inventory"].update({
                "binNo": binNo
            },
                {
                "$set": {
                    "cntdQty": countedObject,
                    "diffQty": diffQty
                }
            })
            print('\n # Update successful # \n')
            return jsonify({'status':  binNo + ' is updated!'})


api.add_resource(Admins, '/admin')
api.add_resource(AdminLogin, '/loginadmin')
api.add_resource(AppUsers, '/appusers/<string:id>')
api.add_resource(AppuserLogin, "/appuserlogin")
api.add_resource(WebUsers, "/webusers/<string:id>")
api.add_resource(WebuserLogin, "/webuserlogin")
api.add_resource(Inventory, "/inventory/<string:id>")
api.add_resource(Barcodes, "/barcodes/<string:id>")
api.add_resource(Categories, '/categories/<string:id>')
api.add_resource(Products, '/products/<string:id>')
api.add_resource(BusinessLocation, "/businesslocations/<string:id>")
api.add_resource(ObjectCounted, "/objectcounted/<string:id>")


if __name__ == '__main__':
    app.run()

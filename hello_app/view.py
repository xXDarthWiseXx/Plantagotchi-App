from flask import Flask, jsonify, render_template, request, session
from asyncua import Client, ua
from datetime import datetime
import time
import asyncio
from . import app

light_data = []
moisture_data = []
nitrogen_data = []
phosphorus_data = []
potassium_data = []

OPC_SERVER_URL = "opc.tcp://100.90.187.71:4840/myopcua/server"


async def get_opc_data(node):
    # Connect to the OPC UA Server
    client = Client(url=OPC_SERVER_URL)
    async with client:
        # Example node ID to read
        node = client.get_node(f"ns=2;s={node}")
        value = await node.read_value()
        return value

async def write_opc_data(data, node):
    client = Client(url=OPC_SERVER_URL)
    async with client:
        # Example node ID to read
        node = client.get_node(f"ns=2;s={node}")
        await node.write_value(ua.Variant(data, ua.VariantType.Boolean))
        return True
    
async def write_opc_string(data, node):
    client = Client(url=OPC_SERVER_URL)
    async with client:
        # Example node ID to read
        node = client.get_node(f"ns=2;s={node}")
        await node.write_value(ua.Variant(data, ua.VariantType.String))
        return True

def PlantModelHelper(Plant):
    if Plant != None:
        # PlantModel(Plant)
        return "Plant model chosen"
    else: 
        return "Please select a plant model."
    
def PlantModel(Plant):
    asyncio.run(write_opc_string(f"{Plant}", "Plant_Name"))
    asyncio.run(write_opc_data(True, "New_Plant"))
    return

@app.route("/read")
def read():
    var = asyncio.run(get_opc_data("Moisture"))
    return render_template('read.html', var=var)

@app.route('/chart/')
def chart():

    labels = [f't{i+1}' for i in range(60)]
    global light_data
    new_val1 = float(asyncio.run(get_opc_data("LightIntensity")))
    if len(light_data) > 60:
        light_data = light_data[1:]
    light_data += [new_val1]
    

    labels2 = [f't{i+1}' for i in range(60)]
    global moisture_data
    new_val2 = float(asyncio.run(get_opc_data("Moisture")))
    if len(moisture_data) > 60:
        moisture_data = moisture_data[1:]
    moisture_data += [new_val2]
    

    labels3 = [f't{i+1}' for i in range(60)]
    global nitrogen_data
    new_val3 = float(asyncio.run(get_opc_data("Nitrogen")))
    if len(nitrogen_data) > 60:
        nitrogen_data = nitrogen_data[1:]
    nitrogen_data += [new_val3]

    global phosphorus_data
    new_val4 = float(asyncio.run(get_opc_data("Phosphorus")))
    if len(phosphorus_data) > 60:
        phosphorus_data = phosphorus_data[1:]
    phosphorus_data += [new_val4]

    global potassium_data
    new_val5 = float(asyncio.run(get_opc_data("Potassium")))
    if len(potassium_data) > 60:
        potassium_data = potassium_data[1:]
    potassium_data += [new_val5]

    return render_template('chart.html', labels=labels, data=light_data, labels2=labels2, data2=moisture_data, labels3=labels3, data3=nitrogen_data, data4=phosphorus_data, data5=potassium_data)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/dropdown/", methods = ['GET', 'POST'])
def dropdown():
    plants = ['Fern', 'Succulent', 'Flower', 'Shrub']
    selected = request.form.get('plant')
    print(PlantModelHelper(selected))
    plant_info = {'Flower':'Flowers need bright direct light, deep and infrequent watering, loose fertilized soil, and protection from extreme temperatures. They need at least 6 hours of direct light and to be watered deeply instead of light splashes.', 'Fern':'Ferns do best in bright indirect sunlight, high humidity, nutrient rich soil, and consistently moist soil. Fertilize them monthly and keep them out of cold areas.', 'Succulent':'Succulents need lots of bright direct light, minimal water, and fast draining soil. They should get at least 6 Hours of sunlight and watered when completely dry.', 'Shrub':"Shrubs require consistent watering, pruning, mulch, nutrient soil, and direct sunlight. Prune the dead wood off to keep healthy and refill nutrients and mulch whenever they get low."}
    return render_template('dropdown.html', plants=plants, selected_plant=selected, plant_info=plant_info)


@app.route("/api/data")
def get_data():
    return app.send_static_file("data.json")

from fastapi import FastAPI, File, UploadFile, HTTPException
from database import Database
from transfer import Transfer
from preprocess import Preprocess
from cut import Cut
from suture import Suture
import os
import shutil

app = FastAPI(
    title="LaparoSim API",
    description="LaparoSim API for Backend Purposes",
)

db = Database()

preprocess_ojb = Preprocess()
transfer_obj = Transfer()
cut_obj = Cut()
suture_obj = Suture()

@app.get("/")
async def home():
    return {"LaparoSim API": "Welcome to LaparoSim API"}

import os
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()

@app.post("/uploadFiles")
async def uploadFiles(csv_file: UploadFile = File(...), png_file: UploadFile = File(...), exeType: int=0, userType: int=0):
    try:
        # Defining csv route for storage at api
        storage_paths = {
            1: {
                0: "/home/Backend_LaparoSim/Datos_Transferencia/Experto/",
                1: "/home/Backend_LaparoSim/Datos_Transferencia/Intermedio/",
                2: "/home/Backend_LaparoSim/Datos_Transferencia/Novato/"
            },
            2: {
                0: "/home/Backend_LaparoSim/Datos_Corte/Experto/",
                1: "/home/Backend_LaparoSim/Datos_Corte/Intermedio/",
                2: "/home/Backend_LaparoSim/Datos_Corte/Novato/"
            },
            3: {
                0: "/home/Backend_LaparoSim/Datos_Sutura/Experto/",
                1: "/home/Backend_LaparoSim/Datos_Sutura/Intermedio/",
                2: "/home/Backend_LaparoSim/Datos_Sutura/Novato/"
            }
        }

        if exeType in storage_paths:
            try:
                # Define the target directories for the CSV at API for Training Data
                csv_storage = storage_paths[exeType][userType]
            except KeyError:
                raise HTTPException(status_code=400, detail="Invalid userType. Must be 0, 1, or 2.")
        else:
            raise HTTPException(status_code=400, detail="Invalid exeType. Must be 1, 2, or 3.")


        # Define the target directories for the CSV and PNG files at webPage
        csv_directory = "/var/www/html/EndoTrainer/assets/data/"
        png_directory = "/var/www/html/EndoTrainer/assets/Graph3D/"

        # Create the target directories if they don't exist
        os.makedirs(csv_storage, exist_ok=True)
        os.makedirs(csv_directory, exist_ok=True)
        os.makedirs(png_directory, exist_ok=True)

        # Save the uploaded CSV file to the CSV storage directory
        csv_file_path = os.path.join(csv_storage, csv_file.filename)
        with open(csv_file_path, "wb") as csv_target:
            csv_target.write(await csv_file.read())

        # Copy the uploaded CSV file to the CSV directory
        csv_directory_path = os.path.join(csv_directory, csv_file.filename)
        shutil.copyfile(csv_file_path, csv_directory_path)

        # Save the uploaded PNG file to the PNG directory
        png_file_path = os.path.join(png_directory, png_file.filename)
        with open(png_file_path, "wb") as png_target:
            png_target.write(await png_file.read())

        return {"status_code": 200, "status_message": "Files uploaded successfully."}

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Target directory not found.")
    except IsADirectoryError as e:
        raise HTTPException(status_code=400, detail="Cannot save file. Target path is a directory.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred during file upload.")

@app.get("/inference_maps")
async def inference_maps(filename: str, exercise: str):
    csv_directory = "/var/www/html/EndoTrainer/assets/data/"
    csv_file_path = os.path.join(csv_directory, filename)

    if os.path.exists(csv_file_path):
        if exercise=="1":
            x,y,z,x2,y2,z2=preprocess_ojb.read_file(csv_file_path)
            maps_values = preprocess_ojb.maps_2(csv_file_path, x, y, z, x2, y2, z2)
            inference = transfer_obj.classify(maps_values)
        elif exercise=="2":
            x,y,z,x2,y2,z2=preprocess_ojb.read_file(csv_file_path)
            maps_values = preprocess_ojb.maps_1(csv_file_path, x, y, z, x2, y2, z2)
            inference = cut_obj.classify(maps_values)
        elif exercise=="3":
            x,y,z,x2,y2,z2=preprocess_ojb.read_file(csv_file_path)
            maps_values = preprocess_ojb.maps_2(csv_file_path, x, y, z, x2, y2, z2)
            inference = suture_obj.classify(maps_values)
        return {"status_code": 200, "status_message": inference}
    else:
        return {"status_code": 404, "status_message": "File not found"}

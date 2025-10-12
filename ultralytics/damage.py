from fastapi import Query
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse

import glob
import random
import os
from ultralytics import YOLO

damage_model = YOLO("damage.pt")

def assess_damage(img_path):
    results = damage_model.predict(
        source=img_path,
        conf=0.25,
        save=True,                          # saves the annotated image
        project='image',
        name='',                # folder where 5 images will be saved
        exist_ok=True                       # prevents folder overwrite errors
    )
    saved_image_path = os.path.join(results[0].save_dir, os.path.basename(img_path))
    return results, saved_image_path

app = FastAPI()

import subprocess

@app.get("/gen")
async def run_gen_cc2():
    try:
        # Path to description.json
        description_json_path = os.path.join(os.path.dirname(__file__), "description.json")
        # Run gen_cc2.py with description.json as the first argument
        result = subprocess.run(
            ["python3", "gen_cc2.py", description_json_path],
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True
        )
        # Read cc/cost-conf.json
        json_path = os.path.join(os.path.dirname(__file__), "cc", "cost-conf.json")
        try:
            with open(json_path, "r") as jf:
                cost_conf_json = jf.read()
        except Exception as json_err:
            cost_conf_json = f"Error reading cost-conf.json: {json_err}"
        return {"returncode": result.returncode, "cost_conf_json": cost_conf_json}
    except Exception as e:
        return {"error": str(e)}

@app.get("/damage")
async def get_damage(img_path: str = Query(..., description="Path to the image file")):
    # If first directory is grade_cam, use the full path; else, use image/predict/<filename>
    parts = os.path.normpath(img_path).split(os.sep)
    if parts[1] == "grade_cam":
        file_path = img_path[1:]
        filename = os.path.basename(img_path)
    else:
        filename = os.path.basename(img_path)
        file_path = os.path.join("image", "predict", filename)
    return FileResponse(file_path, media_type="image/png", filename=filename)

@app.post("/damage")
async def damage(img: UploadFile = File(...)):
    # Save uploaded file to disk
    temp_path = f"{img.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await img.read())
    # Run damage assessment
    results, saved_image_path = assess_damage(temp_path)
    # Clean up temp file
    try:
        os.remove(temp_path)
    except Exception:
        pass
    return JSONResponse({
        "results": str(results),
        "annotated_image_path": saved_image_path
    })

@app.get("/")
async def root():
    return {"message": "Damage assessment API is running."}
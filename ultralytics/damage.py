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
        project='images',
        name='images',                # folder where 5 images will be saved
        exist_ok=True                       # prevents folder overwrite errors
    )
    saved_image_path = os.path.join(results[0].save_dir, os.path.basename(img_path))
    return results, saved_image_path

app = FastAPI()

@app.get("/damage")
async def get_damage(img_path: str = Query(..., description="Path to the image file")):
    # Run damage assessment directly on the provided file path
    results, saved_image_path = assess_damage(img_path)
    # Return the annotated image file in binary
    return FileResponse(saved_image_path, media_type="image/png", filename=os.path.basename(saved_image_path))
@app.post("/damage")
async def damage(img: UploadFile = File(...)):
    # Save uploaded file to disk
    temp_path = f"temp_{img.filename}"
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
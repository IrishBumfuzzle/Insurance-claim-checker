from fastapi import Query
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse

import glob
import random
import os
from ultralytics import YOLO
import json
import subprocess

damage_model = YOLO("damage.pt")

def assess_damage(img_path):
    results = damage_model.predict(
        source=img_path,
        conf=0.25,
        save=True,
        project='image',
        name='',
        exist_ok=True
    )
    saved_image_path = os.path.join(results[0].save_dir, os.path.basename(img_path))
    return results, saved_image_path

app = FastAPI()

@app.get("/gen")
async def run_gen_cc2():
    try:
        # Always use /app/description/description.json (container path)
        base_dir = os.path.dirname(__file__)
        description_json_path = "/app/description/description.json"

        # If description.json doesn't exist, create a minimal one
        if not os.path.exists(description_json_path):
            os.makedirs("/app/description", exist_ok=True)
            minimal = {
                "description": "No user-provided description.",
                "vehicle": {
                    "description": "",
                    "condition": {}
                }
            }
            try:
                with open(description_json_path, "w") as df:
                    json.dump(minimal, df, indent=2)
            except Exception as e:
                return {"error": f"Could not create description.json: {e}"}

        # Run gen_cc2.py with description.json as the first argument
        result = subprocess.run(
            ["python3", "gen_cc2.py", description_json_path],
            cwd=base_dir,
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

        # Include description.json contents for debugging
        desc_text = None
        try:
            with open(description_json_path, "r") as df:
                desc_text = df.read()
        except Exception as d_err:
            desc_text = f"Error reading description.json: {d_err}"

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "cost_conf_json": cost_conf_json,
            "description_json_path": description_json_path,
            "description_json": desc_text
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/description")
async def receive_description(payload: dict):
    """Receive a JSON payload and write it to /app/description/description.json for gen_cc2.py to read."""
    try:
        desc_path = "/app/description/description.json"
        os.makedirs("/app/description", exist_ok=True)
        with open(desc_path, "w") as f:
            json.dump(payload, f, indent=2)
        return {"status": "ok", "path": desc_path}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/damage")
async def get_damage(img_path: str = Query(..., description="Path to the image file")):
    """Fetch annotated image from either grade_cam or image/predict directory."""
    # Normalize path and get parts
    parts = os.path.normpath(img_path).split(os.sep)
    
    # Check if path contains grade_cam or images directory
    if "grade_cam" in parts:
        # Find index of grade_cam and reconstruct path from there
        idx = parts.index("grade_cam")
        file_path = os.path.join("/app", *parts[idx:])
    elif "images" in parts:
        # For images directory, check both /app/images and image/predict
        filename = os.path.basename(img_path)
        # Try /app/images first
        if os.path.exists(os.path.join("/app/images", filename)):
            file_path = os.path.join("/app/images", filename)
        else:
            # Fall back to image/predict
            file_path = os.path.join("image", "predict", filename)
    else:
        # Default to image/predict
        filename = os.path.basename(img_path)
        file_path = os.path.join("image", "predict", filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        return JSONResponse(
            status_code=404,
            content={"error": f"Image not found at {file_path}"}
        )
    
    filename = os.path.basename(file_path)
    return FileResponse(file_path, media_type="image/png", filename=filename)


@app.post("/damage")
async def damage(img: UploadFile = File(...)):
    """Process uploaded image and run damage assessment."""
    # Save uploaded file to /app/images directory
    os.makedirs("/app/images", exist_ok=True)
    temp_path = os.path.join("/app/images", img.filename)
    
    with open(temp_path, "wb") as buffer:
        buffer.write(await img.read())
    
    # Run damage assessment
    results, saved_image_path = assess_damage(temp_path)
    
    return JSONResponse({
        "results": str(results),
        "annotated_image_path": saved_image_path,
        "original_image_path": temp_path
    })


@app.get("/")
async def root():
    return {"message": "Damage assessment API is running."}
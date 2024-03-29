import shutil
import time
from fastapi import datastructures
from fastapi.testclient import TestClient
from app.main import UPLOAD_DIR, Settings, app, BASE_DIR,get_settings
from PIL import Image, ImageChops
import io

client = TestClient(app)

def test_get_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']
    assert response.text !="<h1>hello</h1>"
    #print(response.text)

def test_invalid_file_upload_error():
    response = client.post("/")
    assert response.status_code == 422
    assert "application/json" in response.headers['content-type']


def test_echo_upload():
    img_saved_path = BASE_DIR / 'images'
    for path in img_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None
        response = client.post("/img-show/", files={"file": open(path, 'rb')})

        #ftext = str(path.suffix).replace('.','')
        if img is None:
            assert response.status_code == 400

        else:
            # Returning a valid image
            assert response.status_code == 200
            r_stream = io.BytesIO(response.content)
            echo_img = Image.open(r_stream)
            difference = ImageChops.difference(echo_img,img).getbbox()
            assert difference is None

        #assert "application/json" in response.headers['content-type']
        #assert response.json() == {"msg":"hello now.."}
    time.sleep(3)
    shutil.rmtree(UPLOAD_DIR)

def test_prediction_view():
    img_saved_path = BASE_DIR / 'images'
    settings = get_settings()
    for path in img_saved_path.glob("*.png"):
        try:
            img = Image.open(path)
        except:
            img = None
        response = client.post("/", files={"file": open(path, 'rb')},
        headers={"Authorization": f"JWT {settings.app_auth_token}"})

        #ftext = str(path.suffix).replace('.','')
        if img is None:
            assert response.status_code == 400

        else:
            # Returning a valid image
            assert response.status_code == 200
            data = response.json()
            print(data)
            assert len(data.keys())==2

def test_prediction_upload_no_header():
    img_saved_path = BASE_DIR / 'images'
    settings = get_settings()
    for path in img_saved_path.glob("*.png"):
        try:
            img = Image.open(path)
        except:
            img = None
        response = client.post("/", files={"file": open(path, 'rb')})

        #ftext = str(path.suffix).replace('.','')
        assert response.status_code == 401
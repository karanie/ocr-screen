# This is not the typical `setup.py` that defines dependencies and shit.
# Well It kinda similiar, but it isn't about python shit. This is just to
# install and download some of the required model depending on the OS the
# user is running on.

import os
import pathlib
import requests
import hashlib
import subprocess

def setup_external_dep():
    download_list = [
        {
            "url": "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe",
            "md5sum": "1c7cf7f130e29a8dab57b1243c0816f9",
            "execute": True,
            "target_root": "./.cache",
            "target": "tesseract-ocr-w64-setup-5.4.0.20240606.exe"
        },
        # {
        #     "url": "https://github.com/tesseract-ocr/tessdata/raw/4.00/eng.traineddata",
        #     "md5sum": "7af2ad02d11702c7092a5f8dd044d52f",
        #     "execute": False,
        #     "target_root": "./tesseract/tessdata",
        #     "target": "eng.traineddata"
        # },
        # {
        #     "url": "https://github.com/tesseract-ocr/tessdata/raw/4.00/ind.traineddata",
        #     "md5sum": "7f574fe2f0edc10c8cc00f6e07187a41",
        #     "execute": False,
        #     "target_root": "./tesseract/tessdata",
        #     "target": "ind.traineddata"
        # },
        # {
        #     "url": "https://github.com/tesseract-ocr/tessdata/raw/4.00/jpn.traineddata",
        #     "md5sum": "59cf3e8da735e2fc694434f32989e9bf",
        #     "execute": False,
        #     "target_root": "./tesseract/tessdata",
        #     "target": "jpn.traineddata"
        # }
    ]

    def download(url, target):
        print(f"Downloading {url}..")
        with open(target, "wb") as file:
            res = requests.get(url)
            file.write(res.content)
            print(f"{target} downloaded")

    def verify(path, hash):
        if (hash == ""):
            print(f"Skip verifing {path}..")
            return True

        print(f"Verifing {path}..")
        with open(path, "rb") as f:
            md5sum = hashlib.md5(f.read()).hexdigest()
            if md5sum == hash:
                print(f"{path} verified")
                return True
            else:
                print(f"{path} hash doesn't match")
                return False

    def install(target):
        # for testing on wine only
        # print(f"Installing {target}..")
        # subprocess.call(["wine", target], env={ **os.environ, "WINEPREFIX": f"{os.environ["HOME"]}/.wines/test" })
        # return
        print(f"Installing {target}..")
        subprocess.call([target])

    for i in download_list:
        abs_target = os.path.join(i["target_root"], i["target"])

        pathlib.Path(i["target_root"]).mkdir(exist_ok=True, parents=True)

        if os.path.exists(abs_target):
            print(f"{abs_target} already exists")
            while not verify(abs_target, i["md5sum"]):
                print("Trying to redownload the file..")
                download(i["url"], abs_target)
        else:
            download(i["url"], abs_target)

        if i["execute"]:
            install(abs_target)
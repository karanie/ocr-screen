import subprocess
import os

class OCRModel():
    def __init__(self, config: dict = dict()):
        self.set_config(config)

    def set_config(self, config: dict):
        config.setdefault("input", ".\\.cache\\shot_cropped.png")
        config.setdefault("raw_input", ".\\.cache\\shot.png")
        self.config = config
    
    def reset_config(self):
        self.config = dict()

    def infer(self, image: str = None):
        return "Inference Output"
    
class TesseractModel(OCRModel):
    def set_config(self, config: dict = dict()):
        config.setdefault("root_dir", "C:\\Program Files\\Tesseract-OCR")
        config.setdefault("exec", 'tesseract.exe')

        # Atur bahasa model ke eng secara default atau bahasa pertama yg ditemui di folder tessdata
        avail_langs = os.listdir(os.path.join(config["root_dir"], "tessdata"))
        avail_langs = list(filter(lambda x: x.split(".")[-1] == "traineddata", avail_langs))
        if len(avail_langs) == 0:
            raise Exception("No tessdata found")
        avail_langs = [ i.split(".")[0] for i in avail_langs ]
        if "eng" in avail_langs:
            config.setdefault("lang", 'eng')
        else:
            config.setdefault("lang", avail_langs[0])
        
        super().set_config(config)

    def get_available_langs(self):
        avail_langs = os.listdir(os.path.join(self.config["root_dir"], "tessdata"))
        avail_langs = list(filter(lambda x: x.split(".")[-1] == "traineddata", avail_langs))
        return avail_langs
    
    def infer(self, image: str = None):
        if not image:
            image = self.config["input"]

        executable_abs = os.path.join(self.config["root_dir"], self.config["exec"])
        ps = subprocess.Popen(
            f"cmd /c \"{executable_abs}\" {image} stdout -l {self.config["lang"]}",
            shell=True,
            stdout=subprocess.PIPE
            )
        out, _ = ps.communicate()
        print(out.decode())
        return out.decode()
    
class PaddleOCRModel(OCRModel):
    def __init__(self, config = dict()):
        super().__init__(config)
        import paddleocr # lazy load paddleocr
        self.model = paddleocr.PaddleOCR(lang=self.config["lang"])

    def set_config(self, config: dict = dict()):
        config.setdefault("lang", 'en')
        super().set_config(config)

    def infer(self, image: str = None):
        det = True
        cls = False
        rec = True
        if not image:
            image = self.config["input"]
        out = self.model.ocr(image, det=det, cls=cls, rec=rec)
        try:
            out = "\n".join([ line[1][0] for line in out[0] ])
        except:
            print("No text detected")
            return ""
        print(out)
        return out

    def detect_text(self, image: str = None):
        det = True
        cls = False
        rec = False
        if not image:
            image = self.config["input"]
        out = self.model.ocr(image, det=det, cls=cls, rec=rec)
        return out

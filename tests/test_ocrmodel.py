import pytest
import core.ocrmodel as ocrmodel

def model():
    tesseeract_config = {
        "input": "tests/test_img.png"
    }
    paddleocr_config = {
        "input": "tests/test_img.png",
        "lang": "en"
    }
    tesseract = ocrmodel.TesseractModel(tesseeract_config)
    paddocr = ocrmodel.PaddleOCRModel(paddleocr_config)
    return [tesseract, paddocr]

@pytest.mark.parametrize("model", model())
def test_ocrmodel(model):
    out = model.infer()
    assert type(out) == str
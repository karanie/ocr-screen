import pytest
from core.bboxgrabber import BboxGrabber

def bboxlist():
    return [
        ((1,2,3,4), (1,2,3,4)),
        ((4,3,2,1), (2,1,4,3)),
        ((2,3,4,1), (2,1,4,3)),
        ((1,4,3,1), (1,1,3,4)),
        ((1280,0,500,0), (500, 0, 1280, 0)),
    ]

@pytest.mark.parametrize("input,expected", bboxlist())
def test_get_bbox_position(input, expected):
    gwabber = BboxGrabber()
    gwabber._bbox = input
    bbox = gwabber.get_bbox()
    assert bbox == list(expected)
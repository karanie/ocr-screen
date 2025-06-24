import core.context
import mss
import PIL.Image
import pyperclip
import win10toast
from . import bboxgrabber
from . import bboxselector
import core
import core.preprocess as preprocess
import core.ocrmodel as ocrmodel
import core.user as user
import core.hotkey as hotkey
from core.profile import Profile

def screenshot():
    with mss.mss() as sct:
        sct.shot(output="./.cache/shot.png")

def create_hotkey_handler(profile: Profile):
    def handler():
        # Ambil screenshot
        screenshot()
        img = PIL.Image.open("./.cache/shot.png")
        img_width, img_height = img.size
        
        # Ambil area seleksi screenshot dari user atau deteksi gambar
        if profile.mode == "selection":
            gwabber = bboxgrabber.BboxGrabber()
            gwabber.grab(img)
            bbox = gwabber.get_bbox()

            # Potong gambar
            try:
                img.crop(bbox).save("./.cache/shot_cropped.png", format="png")
            except SystemError:
                print("Crop size too small")
                return
        elif profile.mode == "detection":
            textdetm = ocrmodel.PaddleOCRModel()

            text_bboxes = textdetm.detect_text(image=textdetm.config["raw_input"])[0]
            text_bboxes = preprocess.flatten_bboxes(text_bboxes)
            text_bboxes = preprocess.get_bboxes_tl_br_corner(text_bboxes)
            # text_bboxes = preprocess.dilate_bboxes(
            #     text_bboxes,
            #     domain_size=[0, 0, img_width, img_height],
            # )
            # text_bboxes = preprocess.merge_boxes_iou(text_bboxes)

            sewector = bboxselector.BboxSelector()
            sewector.select(img, text_bboxes)
            bbox = sewector.get_bbox()

            try:
                img.crop(bbox).save("./.cache/shot_cropped.png", format="png")
            except SystemError:
                print("Crop size too small")
                return

        # Masukkan ke model
        ocrm = ocrmodel.OCRModel()
        if (profile.model == "tesseract"):
            ocrm = ocrmodel.TesseractModel(profile.model_config)
        elif (profile.model == "paddleocr"):
            ocrm = ocrmodel.PaddleOCRModel(profile.model_config)
        out = ocrm.infer()
        
        # Copy ke clipboard
        pyperclip.copy(out)

        # Send toasts
        # notifier = win10toast.ToastNotifier()
        # notifier.show_toast("OCR-Screen", "Detected texts are copied to clipboard", threaded=True)
    return handler

core_ctx = {
    "hotkey_mgr": hotkey.HotkeyManager()
}

def run():
    active_user = user.User.get_active_user()
    active_profiles = active_user.get_profiles()

    print(active_user)
    print(active_profiles)

    for p in active_profiles:
        try:
            core_ctx["hotkey_mgr"].register_profile_hotkey(p, create_hotkey_handler(p))
        except:
            p.is_enabled = False
            p.update()

def main(ctx: core.context.MainContext):
    while True:
        with ctx.signal_cond:
            main_queue_msg = ctx.signal.value
            if main_queue_msg != core.context.SignalState.PAUSE:
                run()
            elif main_queue_msg == core.context.SignalState.PAUSE:
                core_ctx["hotkey_mgr"].unhook_all_hotkey()
            ctx.signal_cond.wait()
            main_queue_msg = ctx.signal.value
            core_ctx["hotkey_mgr"].unhook_all_hotkey()
            if (main_queue_msg == core.context.SignalState.QUIT):
                break

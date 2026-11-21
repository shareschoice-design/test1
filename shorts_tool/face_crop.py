"""Face-aware framing for vertical crops.

decide(src, start, dur, zf, default_cx) -> ("fit", None) or ("crop", cx)
- low-res sources (< 700 px tall) are shown whole over a blurred fill instead of being upscaled & cropped
- faces found in 3 sampled frames -> crop centred on them
- faces spread wider than the vertical crop (e.g. two people hugging far apart) -> "fit" so nobody is cut in half
- no faces -> keep default_cx
"""
import os
import cv2

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
_FRONT = cv2.CascadeClassifier(os.path.join(_DIR, "haarcascade_frontalface_default.xml"))
_PROF = cv2.CascadeClassifier(os.path.join(_DIR, "haarcascade_profileface.xml"))
MIN_H = 700


def _faces(frame):
    g = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    h, w = g.shape
    ms = (max(24, h // 22),) * 2
    out = [tuple(f) for f in _FRONT.detectMultiScale(g, 1.1, 6, minSize=ms)]
    out += [tuple(f) for f in _PROF.detectMultiScale(g, 1.1, 6, minSize=ms)]
    out += [(w - x - fw, y, fw, fh) for x, y, fw, fh in _PROF.detectMultiScale(cv2.flip(g, 1), 1.1, 6, minSize=ms)]
    return out


def decide(src, start, dur, zf=1.0, default_cx=0.5):
    """returns (mode, cx, fit_scale): mode "crop" (full-screen vertical crop) or "fit" (enlarged frame over blur)"""
    cap = cv2.VideoCapture(src)
    W, H = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    if not W or not H or W / H <= 9 / 16 + 0.01:
        return ("crop", default_cx, 1.0)
    boxes = []
    for f in (0.2, 0.5, 0.8):
        cap.set(cv2.CAP_PROP_POS_MSEC, (start + dur * f) * 1000)
        ok, frame = cap.read()
        if ok:
            boxes += _faces(frame)
    cap.release()
    span = (min(x for x, y, w, h in boxes), max(x + w for x, y, w, h in boxes)) if boxes else None
    def centre(cw):
        if not span or W - cw < 1: return default_cx
        c = (span[0] + span[1]) / 2
        return round(min(max(c - cw / 2, 0), W - cw) / (W - cw), 3)
    if H >= MIN_H:
        cw = H * 9 / 16 / zf
        if not span or span[1] - span[0] <= cw * 0.92:
            return ("crop", centre(cw), 1.0)
    # fit: frame enlarged 1.35x (shows ~74% of the width) unless faces need the full width
    FS = 1.35
    cw = W / FS
    if span and span[1] - span[0] > cw * 0.92:
        return ("fit", 0.5, 1.0)
    return ("fit", centre(cw), FS)

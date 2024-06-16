import cv2 as cv
import numpy as np
import ultralytics.engine.results
from ultralytics import YOLO
from typing import Tuple
from pathlib import Path


class YOLOBot:

    def __init__(self, model_path: str | Path, confidence_threshold: float = 0.5):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

    def draw_rect(self, image: np.ndarray | cv.Mat, box: ultralytics.engine.results.Boxes):
        x1, y1, x2, y2 = box.xyxy[0].astype(int)

        class_index = int(box.cls)
        color = self.classes_descriptions[class_index]["color"]
        inv_color = np.array([255, 255, 255]) - np.array(color)

        cv.rectangle(image, [x1, y1], [x2, y2], color=color, thickness=self.rect_thickness)
        cv.rectangle(image, [x1, y1], [x1 + self.w_text_box, y1 - self.h_text_box], color=color, thickness=-1)

        cv.putText(image,
                   text=str(class_index),
                   org=[x1, y1 + self.y_text_offset],
                   fontFace=cv.FONT_HERSHEY_SIMPLEX,
                   thickness=self.font_thickness,
                   fontScale=self.font_scale,
                   color=inv_color.tolist())

    def parse_picture(self, image: np.ndarray | cv.Mat) -> str:

        result = self.model(image)[0].cpu().numpy()
        counts = np.zeros(len(self.classes_descriptions))

        for box in result.boxes:
            if box.conf < self.confidence_threshold:
                continue
            class_index = int(box.cls)
            self.draw_rect(image, box)
            counts[class_index] += 1

        text = ""

        for i, description in enumerate(self.classes_descriptions):
            if counts[i] == 0:
                continue

            line = description["label"] + " - " + str(int(counts[i])) + " шт.\n"
            text += line

        return text

    @staticmethod
    def convert_to_array(image_as_bytes: bytes) -> np.ndarray | cv.Mat:
        np_file = np.frombuffer(image_as_bytes, dtype=np.uint8)
        file_mat = cv.imdecode(np_file, cv.IMREAD_COLOR)
        image = file_mat
        return image

    @staticmethod
    def convert_to_bytes(image_as_array: np.ndarray | cv.Mat) -> np.ndarray | bytes:
        as_bytes = cv.imencode(".png", image_as_array)
        if as_bytes[0]:
            return as_bytes[1]
        else:
            raise Exception("Wrong image, failed encode to bytes!")

    def get_response(self, image_as_bytes) -> Tuple[str, np.ndarray]:
        image = self.convert_to_array(image_as_bytes)
        text = self.parse_picture(image)
        encoded_image = self.convert_to_bytes(image)
        return text, encoded_image

    classes_descriptions = [
        {"label": "#0 Прилегающие дефекты", "color": [255, 0, 255]},
        {"label": "#1 Дефекты целостности", "color": [43, 193, 0]},
        {"label": "#2 Дефекты геометрии", "color": [177, 33, 25]},
        {"label": "#3 Дефекты постобработки", "color": [255, 255, 255]},
        {"label": "#4 Дефекты невыполнения", "color": [170, 0, 162]},
    ]
    
    rect_thickness: int = 20
    w_text_box: int = 240
    h_text_box: int = 320
    y_text_offset: int = -3
    font_thickness: int = 20
    font_scale: float = 12

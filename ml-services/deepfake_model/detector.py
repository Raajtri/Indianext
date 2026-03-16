import cv2
import numpy as np
import tensorflow as tf
from mtcnn import MTCNN
from tensorflow.keras.applications import Xception
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model

print("Loading Xception model...")

base_model = Xception(
    weights="xception_weights_tf_dim_ordering_tf_kernels_notop.h5",
    include_top=False,
    input_shape=(299,299,3)
)

x = base_model.output
x = GlobalAveragePooling2D()(x)
predictions = Dense(1, activation="sigmoid")(x)

model = Model(inputs=base_model.input, outputs=predictions)

detector = MTCNN()

print("Model loaded")


def preprocess(face):

    face = cv2.resize(face,(299,299))
    face = face/255.0
    face = np.expand_dims(face,0)

    return face


def detect_image(path):

    img = cv2.imread(path)

    faces = detector.detect_faces(img)

    if len(faces)==0:
        print("No face detected")
        return

    x,y,w,h = faces[0]['box']

    face = img[y:y+h,x:x+w]

    face = preprocess(face)

    pred = model.predict(face)[0][0]

    if pred > 0.5:
        print("⚠️ Deepfake Image")
    else:
        print("✅ Real Image")


def detect_video(video_path):

    cap = cv2.VideoCapture(video_path)

    scores = []
    frame_id = 0

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        frame_id += 1

        # analyze every 5th frame (speed boost)
        if frame_id % 5 != 0:
            continue

        faces = detector.detect_faces(frame)

        if len(faces)==0:
            continue

        x,y,w,h = faces[0]['box']

        face = frame[y:y+h,x:x+w]

        face = preprocess(face)

        pred = model.predict(face)[0][0]

        scores.append(pred)

    cap.release()

    if len(scores)==0:
        print("No faces detected")
        return

    fake_frames = sum([1 for s in scores if s>0.5])
    real_frames = len(scores)-fake_frames

    if fake_frames > real_frames:
        print("⚠️ Deepfake Video")
    else:
        print("✅ Real Video")


if __name__ == "__main__":

    detect_image("test.jpg")

    detect_video("test_video.mp4")
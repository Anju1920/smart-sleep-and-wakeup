from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import pygame
import time
import os
import threading

app = Flask(__name__)


# ============================================================
# SETTINGS
# ============================================================

VOICE1 = "voice1.mp3"
VOICE2 = "voice2.mp3"

CLOSED_THRESHOLD = 0.20
CLOSED_TIME_LIMIT = 10


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Camera could not be opened")


# ============================================================
# MEDIAPIPE
# ============================================================

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


# ============================================================
# EYE LANDMARKS
# ============================================================

LEFT_EYE = [
    362,
    385,
    387,
    263,
    373,
    380
]

RIGHT_EYE = [
    33,
    160,
    158,
    133,
    153,
    144
]


# ============================================================
# VARIABLES
# ============================================================

eyes_closed_start = None

previous_state = "UNKNOWN"

voice2_playing = False

current_state = "STARTING"

current_ratio = 0.0

current_closed_time = 0.0

camera_running = camera.isOpened()


# ============================================================
# AUDIO
# ============================================================

try:

    pygame.mixer.init()

    audio_ready = True

    print("Audio initialized")

except Exception as e:

    print("Audio error:", e)

    audio_ready = False


# ============================================================
# EYE RATIO
# ============================================================

def eye_ratio(
    landmarks,
    points,
    width,
    height
):

    p1 = landmarks[points[0]]
    p2 = landmarks[points[1]]
    p3 = landmarks[points[2]]
    p4 = landmarks[points[3]]
    p5 = landmarks[points[4]]
    p6 = landmarks[points[5]]

    x1 = int(p1.x * width)
    y1 = int(p1.y * height)

    x2 = int(p2.x * width)
    y2 = int(p2.y * height)

    x3 = int(p3.x * width)
    y3 = int(p3.y * height)

    x4 = int(p4.x * width)
    y4 = int(p4.y * height)

    x5 = int(p5.x * width)
    y5 = int(p5.y * height)

    x6 = int(p6.x * width)
    y6 = int(p6.y * height)

    vertical1 = (
        (x2 - x6) ** 2 +
        (y2 - y6) ** 2
    ) ** 0.5

    vertical2 = (
        (x3 - x5) ** 2 +
        (y3 - y5) ** 2
    ) ** 0.5

    horizontal = (
        (x1 - x4) ** 2 +
        (y1 - y4) ** 2
    ) ** 0.5

    if horizontal == 0:
        return 0

    return (
        vertical1 + vertical2
    ) / (
        2 * horizontal
    )


# ============================================================
# AUDIO FUNCTIONS
# ============================================================

def play_voice1():

    if not audio_ready:
        return

    if not os.path.exists(VOICE1):
        print("voice1.mp3 not found")
        return

    try:

        pygame.mixer.music.stop()

        pygame.mixer.music.load(
            VOICE1
        )

        pygame.mixer.music.play(
            0
        )

        print("Playing Voice 1 once")

    except Exception as e:

        print(
            "Voice 1 error:",
            e
        )


def start_voice2():

    global voice2_playing

    if not audio_ready:
        return

    if not os.path.exists(VOICE2):
        print("voice2.mp3 not found")
        return

    if voice2_playing:
        return

    try:

        pygame.mixer.music.stop()

        pygame.mixer.music.load(
            VOICE2
        )

        pygame.mixer.music.play(
            -1
        )

        voice2_playing = True

        print(
            "Playing Voice 2 repeatedly"
        )

    except Exception as e:

        print(
            "Voice 2 error:",
            e
        )


def stop_voice2():

    global voice2_playing

    if not voice2_playing:
        return

    try:

        pygame.mixer.music.stop()

    except Exception:
        pass

    voice2_playing = False

    print(
        "Voice 2 stopped"
    )


# ============================================================
# PROCESS CAMERA FRAME
# ============================================================

def process_frame(frame):

    global eyes_closed_start
    global previous_state
    global current_state
    global current_ratio
    global current_closed_time

    height, width, _ = frame.shape

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = face_mesh.process(
        rgb
    )

    # ========================================================
    # FACE FOUND
    # ========================================================

    if results.multi_face_landmarks:

        landmarks = (
            results
            .multi_face_landmarks[0]
            .landmark
        )

        left = eye_ratio(
            landmarks,
            LEFT_EYE,
            width,
            height
        )

        right = eye_ratio(
            landmarks,
            RIGHT_EYE,
            width,
            height
        )

        average = (
            left + right
        ) / 2

        current_ratio = average


        # ====================================================
        # EYES CLOSED
        # ====================================================

        if average < CLOSED_THRESHOLD:

            state = "CLOSED"

            if eyes_closed_start is None:

                eyes_closed_start = time.time()

                print(
                    "Eyes closed - timer started"
                )

            current_closed_time = (
                time.time()
                -
                eyes_closed_start
            )


            # -----------------------------------------------
            # 10 SECOND ALERT
            # -----------------------------------------------

            if (
                current_closed_time
                >= CLOSED_TIME_LIMIT
            ):

                if not voice2_playing:

                    print(
                        "10 seconds completed!"
                    )

                    start_voice2()


        # ====================================================
        # EYES OPEN
        # ====================================================

        else:

            state = "OPEN"

            current_closed_time = 0

            eyes_closed_start = None


            # -----------------------------------------------
            # STOP VOICE 2
            # -----------------------------------------------

            if voice2_playing:

                print(
                    "Eyes opened!"
                )

                stop_voice2()


            # -----------------------------------------------
            # CLOSED -> OPEN
            # -----------------------------------------------

            if previous_state == "CLOSED":

                play_voice1()


        previous_state = state

        current_state = state


    # ========================================================
    # NO FACE
    # ========================================================

    else:

        current_state = "NO FACE"

        current_ratio = 0

        current_closed_time = 0

        eyes_closed_start = None

        stop_voice2()

        previous_state = "UNKNOWN"


    # ========================================================
    # DRAW INFORMATION ON CAMERA
    # ========================================================

    cv2.putText(
        frame,
        f"State: {current_state}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Eye Ratio: {current_ratio:.3f}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Closed: {current_closed_time:.1f}s",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 200, 255),
        2
    )

    return frame


# ============================================================
# CAMERA GENERATOR
# ============================================================

def generate_frames():

    global camera_running

    while True:

        success, frame = camera.read()

        if not success:

            camera_running = False

            break

        camera_running = True

        frame = process_frame(
            frame
        )

        success, buffer = cv2.imencode(
            ".jpg",
            frame
        )

        if not success:
            continue

        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            +
            frame_bytes
            +
            b"\r\n"
        )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# ============================================================
# VIDEO
# ============================================================

@app.route("/video")
def video():

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ============================================================
# STATUS
# ============================================================

@app.route("/status")
def status():

    return jsonify({

        "state": current_state,

        "ratio": round(
            current_ratio,
            3
        ),

        "closed_time": round(
            current_closed_time,
            1
        ),

        "voice2_playing": voice2_playing,

        "camera_running": camera_running
    })


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "======================================"
    )

    print(
        "       ACTIVITY ALERT"
    )

    print(
        "======================================"
    )

    print()

    print(
        "Open browser:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True
    )

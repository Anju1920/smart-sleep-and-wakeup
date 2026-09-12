import cv2
import mediapipe as mp
import pygame
import time
import os


# ============================================================
# AUDIO FILES
# ============================================================

VOICE1 = "voice1.mp3"
VOICE2 = "voice2.mp3"


# ============================================================
# SETTINGS
# ============================================================

CLOSED_THRESHOLD = 0.20
CLOSED_TIME_LIMIT = 10


# ============================================================
# CHECK AUDIO FILES
# ============================================================

if not os.path.exists(VOICE1):

    print()
    print("ERROR: voice1.mp3 not found!")
    print("Make sure voice1.mp3 is in the project folder.")
    print()

    raise SystemExit


if not os.path.exists(VOICE2):

    print()
    print("ERROR: voice2.mp3 not found!")
    print("Make sure voice2.mp3 is in the project folder.")
    print()

    raise SystemExit


# ============================================================
# INITIALIZE AUDIO
# ============================================================

try:

    pygame.mixer.init()

    print("Audio initialized")

except Exception as e:

    print()
    print("ERROR: Could not initialize audio")
    print(e)
    print()

    raise SystemExit


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
# EYE RATIO FUNCTION
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
# AUDIO STATE
# ============================================================

voice2_playing = False


# ============================================================
# PLAY VOICE 1
# ============================================================

def play_voice1():

    global voice2_playing


    # --------------------------------------------------------
    # If Voice 1 is already playing, don't restart it
    # --------------------------------------------------------

    if not voice2_playing and pygame.mixer.music.get_busy():

        return


    try:

        # Stop anything currently playing

        pygame.mixer.music.stop()


        # Load Voice 1

        pygame.mixer.music.load(
            VOICE1
        )


        # ----------------------------------------------------
        # Voice 1 repeats continuously
        # ----------------------------------------------------

        pygame.mixer.music.play(
            -1
        )


        voice2_playing = False


        print("Voice 1 playing")


    except Exception as e:

        print()
        print("ERROR playing Voice 1:")
        print(e)
        print()


# ============================================================
# PLAY VOICE 2
# ============================================================

def play_voice2():

    global voice2_playing


    # --------------------------------------------------------
    # Don't start Voice 2 again if already playing
    # --------------------------------------------------------

    if voice2_playing:

        return


    try:

        # Stop Voice 1

        pygame.mixer.music.stop()


        # Load Voice 2

        pygame.mixer.music.load(
            VOICE2
        )


        # ----------------------------------------------------
        # Voice 2 repeats continuously
        # ----------------------------------------------------

        pygame.mixer.music.play(
            -1
        )


        voice2_playing = True


        print()
        print("==============================")
        print("VOICE 2 PLAYING")
        print("==============================")
        print()


    except Exception as e:

        print()
        print("==============================")
        print("ERROR PLAYING VOICE 2")
        print("==============================")
        print(e)
        print()


# ============================================================
# STOP VOICE 2
# ============================================================

def stop_voice2():

    global voice2_playing


    # Stop audio immediately

    pygame.mixer.music.stop()


    # Reset state

    voice2_playing = False


    print("Voice 2 stopped")


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print()
    print("ERROR: Could not open camera!")
    print()

    pygame.quit()
    face_mesh.close()

    raise SystemExit


# ============================================================
# VARIABLES
# ============================================================

eyes_closed_start = None

previous_state = "UNKNOWN"


# ============================================================
# START MESSAGE
# ============================================================

print()
print("======================================")
print("       ACTIVITY ALERT STARTED")
print("======================================")
print()

print("Camera started")

print(
    "Eyes closed threshold:",
    CLOSED_THRESHOLD
)

print(
    "Voice 2 starts after:",
    CLOSED_TIME_LIMIT,
    "seconds"
)

print()

print("Audio behavior:")
print("OPEN       -> Voice 1")
print("CLOSED     -> Voice 1 for 10 seconds")
print("10 seconds -> Voice 2")
print("OPEN again -> Voice 2 stops + Voice 1")

print()

print("Press Q to quit")
print()


# ============================================================
# MAIN LOOP
# ============================================================

while True:


    # ========================================================
    # READ CAMERA
    # ========================================================

    ret, frame = cap.read()


    if not ret:

        print(
            "ERROR: Could not read camera frame"
        )

        break


    height, width, _ = frame.shape


    # ========================================================
    # BGR → RGB
    # ========================================================

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # ========================================================
    # MEDIAPIPE
    # ========================================================

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


        # ====================================================
        # LEFT EYE
        # ====================================================

        left = eye_ratio(

            landmarks,

            LEFT_EYE,

            width,

            height
        )


        # ====================================================
        # RIGHT EYE
        # ====================================================

        right = eye_ratio(

            landmarks,

            RIGHT_EYE,

            width,

            height
        )


        # ====================================================
        # AVERAGE EYE RATIO
        # ====================================================

        average = (
            left + right
        ) / 2


        # ====================================================
        # EYES CLOSED
        # ====================================================

        if average < CLOSED_THRESHOLD:


            state = "CLOSED"


            # ------------------------------------------------
            # START CLOSED TIMER
            # ------------------------------------------------

            if eyes_closed_start is None:


                eyes_closed_start = time.time()


                print()
                print(
                    "Eyes closed - timer started"
                )


                # ------------------------------------------------
                # Voice 1 continues during first 10 seconds
                # ------------------------------------------------

                if not voice2_playing:

                    play_voice1()


            # ------------------------------------------------
            # CALCULATE CLOSED TIME
            # ------------------------------------------------

            closed_time = (
                time.time()
                -
                eyes_closed_start
            )


            # ------------------------------------------------
            # DISPLAY
            # ------------------------------------------------

            cv2.putText(

                frame,

                "EYES CLOSED",

                (30, 50),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                (0, 0, 255),

                2
            )


            cv2.putText(

                frame,

                f"Closed: {closed_time:.1f} sec",

                (30, 90),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.8,

                (0, 255, 255),

                2
            )


            cv2.putText(

                frame,

                f"Eye Ratio: {average:.3f}",

                (30, 130),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (255, 255, 0),

                2
            )


            # ------------------------------------------------
            # 10 SECOND CHECK
            # ------------------------------------------------

            if closed_time >= CLOSED_TIME_LIMIT:


                if not voice2_playing:


                    print()
                    print(
                        "10 seconds completed!"
                    )

                    print(
                        "Stopping Voice 1"
                    )


                    # ------------------------------------------------
                    # Stop Voice 1
                    # ------------------------------------------------

                    pygame.mixer.music.stop()


                    # ------------------------------------------------
                    # Start Voice 2
                    # ------------------------------------------------

                    play_voice2()


        # ====================================================
        # EYES OPEN
        # ====================================================

        else:


            state = "OPEN"


            # ------------------------------------------------
            # RESET TIMER
            # ------------------------------------------------

            eyes_closed_start = None


            # ------------------------------------------------
            # DISPLAY
            # ------------------------------------------------

            cv2.putText(

                frame,

                "EYES OPEN",

                (30, 50),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                (0, 255, 0),

                2
            )


            cv2.putText(

                frame,

                f"Eye Ratio: {average:.3f}",

                (30, 90),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (255, 255, 0),

                2
            )


            # =================================================
            # VOICE 2 WAS PLAYING
            # =================================================

            if voice2_playing:


                print()
                print(
                    "Eyes opened!"
                )

                print(
                    "Stopping Voice 2 immediately"
                )


                # ------------------------------------------------
                # STOP VOICE 2
                # ------------------------------------------------

                stop_voice2()


                # ------------------------------------------------
                # START VOICE 1
                # ------------------------------------------------

                play_voice1()


            # =================================================
            # NOTHING PLAYING
            # =================================================

            elif not pygame.mixer.music.get_busy():


                # ------------------------------------------------
                # Make sure Voice 1 is running
                # ------------------------------------------------

                play_voice1()


        # ----------------------------------------------------
        # SAVE STATE
        # ----------------------------------------------------

        previous_state = state


    # ========================================================
    # NO FACE DETECTED
    # ========================================================

    else:


        cv2.putText(

            frame,

            "NO FACE DETECTED",

            (30, 50),

            cv2.FONT_HERSHEY_SIMPLEX,

            1,

            (0, 165, 255),

            2
        )


        # ------------------------------------------------
        # RESET TIMER
        # ------------------------------------------------

        eyes_closed_start = None


        previous_state = "UNKNOWN"


        # ------------------------------------------------
        # Stop Voice 2 if face disappears
        # ------------------------------------------------

        if voice2_playing:


            print(
                "Face lost - stopping Voice 2"
            )


            stop_voice2()


        # ------------------------------------------------
        # Start Voice 1
        # ------------------------------------------------

        if not pygame.mixer.music.get_busy():

            play_voice1()


    # ========================================================
    # SHOW CAMERA
    # ========================================================

    cv2.imshow(

        "Activity Alert",

        frame
    )


    # ========================================================
    # Q TO QUIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

print()
print("Stopping Activity Alert...")


# Stop audio

pygame.mixer.music.stop()


# Release camera

cap.release()


# Close OpenCV

cv2.destroyAllWindows()


# Close MediaPipe

face_mesh.close()


# Quit pygame

pygame.quit()


print(
    "Program stopped"
)

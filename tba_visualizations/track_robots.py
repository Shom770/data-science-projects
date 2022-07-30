from os import environ

import cv2
import cv2.legacy
import matplotlib.pyplot as plt
import yt_dlp
from dotenv import load_dotenv
from scipy.interpolate import interp1d
from tbapy import TBA

load_dotenv()

WIDTH = 1920
HEIGHT = 1080
tba = TBA(environ["TBA_API_KEY"])


def center_of_bbox(bbox):
    return bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2


def track_robots(match_key: str) -> None:
    video_url = f"https://youtube.com/watch?v={tba.match(key=match_key)['videos'][0]['key']}"

    with yt_dlp.YoutubeDL({}) as ydl:
        ydl.download([video_url])

    vs = cv2.VideoCapture("Einstein Final 1 - 2022 FIRST Championship [EgPMnpp-PnQ].mp4")

    tracker = cv2.legacy.TrackerCSRT_create()

    initBB = None

    positions_x = []
    positions_y = []

    figure, ax = plt.subplots(figsize=(12, 6))

    grabbed = True
    initialized = False

    while grabbed:
        grabbed, frame = vs.read()

        if initBB is not None:
            # grab the new bounding box coordinates of the object
            (success, box) = tracker.update(frame)
            # check to see if the tracking was a success
            if success:
                (x, y, w, h) = [int(v) for v in box]
                positions_x.append(interp_x(x + w / 2))
                positions_y.append(interp_y(y + h / 2))
                cv2.rectangle(
                    frame, (x, y), (x + w, y + h),
                    (0, 255, 0), 2
                )

        key = cv2.waitKey(1) & 0xFF
        cv2.imshow("Frame", frame)

        # if the 's' key is selected, we are going to "select" a bounding
        # box to track
        if key == ord("s"):
            initBB = cv2.selectROI("Frame", frame, fromCenter=False,
                                   showCrosshair=True)
            # start OpenCV object tracker using the supplied bounding box
            # coordinates, then start the FPS throughput estimator as well
            if not initialized:
                tracker.init(frame, initBB)
                initialized = True
            else:
                tracker = cv2.legacy.TrackerCSRT_create()
                tracker.init(frame, initBB)
        elif key == ord("i"):
            upper_l = center_of_bbox(
                cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
            )
            upper_r = center_of_bbox(
                cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
            )
            lower_l = center_of_bbox(
                cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
            )
            lower_r = center_of_bbox(
                cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
            )

            interp_x = interp1d([min(upper_l[0], lower_l[0]), max(upper_r[0], lower_r[0])], [0, 54])
            interp_y = interp1d([min(upper_l[1], upper_r[1]), max(lower_l[1], lower_r[1])], [0, 27])

            initBB = cv2.selectROI("Frame", frame, fromCenter=False,
                                   showCrosshair=True)
            # start OpenCV object tracker using the supplied bounding box
            # coordinates, then start the FPS throughput estimator as well
            if not initialized:
                tracker.init(frame, initBB)
                initialized = True
            else:
                tracker = cv2.legacy.TrackerCSRT_create()
                tracker.init(frame, initBB)

        elif key == ord("q"):
            break

    background = plt.imread("field.png")

    ax.imshow(background, zorder=0)

    adjust_x = interp1d([0, 54], [0, ax.get_xlim()[-1]])
    adjust_y = interp1d([0, 27], [0, ax.get_ylim()[0]])

    ax.plot(adjust_x(positions_x), adjust_y(positions_y), zorder=1, color="white")

    plt.show()

    vs.release()
    cv2.destroyAllWindows()


track_robots(match_key="2022cmptx_f1m1")

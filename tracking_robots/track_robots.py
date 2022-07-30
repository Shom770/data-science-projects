import json
from os import environ

import cv2
import cv2.legacy
import matplotlib.pyplot as plt
import yt_dlp
from dotenv import load_dotenv
from scipy.interpolate import interp1d
from tbapy import TBA

load_dotenv()

tba = TBA(environ["TBA_API_KEY"])


def center_of_bbox(bbox: tuple) -> tuple:
    return bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2


def track_robots(match_key: str) -> None:
    video_key = tba.match(key=match_key)['videos'][0]['key']
    video_url = f"https://youtube.com/watch?v={video_key}"

    with (
        yt_dlp.YoutubeDL({}) as ydl,
        open("config.json") as file
    ):
        config = json.load(file)
        info = ydl.extract_info(video_url, download=True)
        configured = info["fulltitle"] in config.values()

    vs = cv2.VideoCapture(f"{info['fulltitle']} [{video_key}].mp4")

    tracker = cv2.legacy.TrackerCSRT_create()

    init_bbox = None

    positions_x = []
    positions_y = []

    figure, ax = plt.subplots(figsize=(12, 6))

    grabbed = True
    initialized = False

    while grabbed:
        grabbed, frame = vs.read()

        if init_bbox is not None:
            # grab the new bounding box coordinates of the object
            (success, box) = tracker.update(frame)
            # check to see if the tracking was a success
            if success:
                (x, y, w, h) = [int(v) for v in box]
                try:
                    positions_x.append(interp_x(x + w / 2))
                    positions_y.append(interp_y(y + h / 2))
                except ValueError:
                    if len(positions_x) - len(positions_y) != 0:
                        positions_x.pop()

                cv2.rectangle(
                    frame, (x, y), (x + w, y + h),
                    (0, 255, 0), 2
                )

        key = cv2.waitKey(1) & 0xFF

        cv2.imshow("Frame", frame)

        # if the 's' key is selected, we are going to "select" a bounding
        # box to track
        if key == ord("s"):
            init_bbox = cv2.selectROI("Frame", frame, fromCenter=False,
                                   showCrosshair=True)
            # start OpenCV object tracker using the supplied bounding box
            # coordinates, then start the FPS throughput estimator as well
            if not initialized:
                tracker.init(frame, init_bbox)
                initialized = True
            else:
                tracker = cv2.legacy.TrackerCSRT_create()
                tracker.init(frame, init_bbox)

        elif key == ord("i"):
            if config.get("video_name") and config["video_name"] == info["fulltitle"]:
                upper_l = config["upper_l"]
                upper_r = config["upper_r"]
                lower_l = config["lower_l"]
                lower_r = config["lower_r"]
            else:
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

                with open("config.json", "w") as file:
                    config["video_name"] = info["fulltitle"]
                    config["upper_l"] = upper_l
                    config["upper_r"] = upper_r
                    config["lower_l"] = lower_l
                    config["lower_r"] = lower_r

                    json.dump(config, file)

            interp_x = interp1d([min(upper_l[0], lower_l[0]), max(upper_r[0], lower_r[0])], [0, 54])
            interp_y = interp1d([min(upper_l[1], upper_r[1]), max(lower_l[1], lower_r[1])], [0, 27])

            init_bbox = cv2.selectROI("Frame", frame, fromCenter=False,
                                   showCrosshair=True)
            # start OpenCV object tracker using the supplied bounding box
            # coordinates, then start the FPS throughput estimator as well
            tracker.init(frame, init_bbox)
            initialized = True

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

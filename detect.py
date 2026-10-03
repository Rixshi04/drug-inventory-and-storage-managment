import argparse

import cv2


def highlight_face(net, frame, conf_threshold=0.7):
    """Detect faces and return an annotated frame plus bounding boxes."""
    frame_height, frame_width = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(
        frame, 1.0, (300, 300), [104, 117, 123], True, False
    )
    net.setInput(blob)
    detections = net.forward()

    face_boxes = []
    for i in range(detections.shape[2]):
        confidence = float(detections[0, 0, i, 2])
        if confidence <= conf_threshold:
            continue

        x1 = max(0, int(detections[0, 0, i, 3] * frame_width))
        y1 = max(0, int(detections[0, 0, i, 4] * frame_height))
        x2 = min(frame_width - 1, int(detections[0, 0, i, 5] * frame_width))
        y2 = min(frame_height - 1, int(detections[0, 0, i, 6] * frame_height))

        if x2 <= x1 or y2 <= y1:
            continue

        face_boxes.append([x1, y1, x2, y2])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return frame, face_boxes


def detect_hands(frame, face_box):
    """Return the simplified region above a face used by the SOS demo."""
    x1, y1, x2, _ = face_box
    face_height = max(1, face_box[3] - y1)
    y_start = max(0, y1 - int(1.5 * face_height))
    return [(x1, y_start, x2, y1)]


def check_sos_gesture(face_box, hands):
    return any(hand[1] < face_box[1] for hand in hands)


def main():
    parser = argparse.ArgumentParser(
        description="OpenCV age/gender demo with a simplified SOS region detector."
    )
    parser.add_argument("--image", help="Video file path. Omit to use the webcam.")
    args = parser.parse_args()

    face_proto = "opencv_face_detector.pbtxt"
    face_model = "opencv_face_detector_uint8.pb"
    age_proto = "age_deploy.prototxt"
    age_model = "age_net.caffemodel"
    gender_proto = "gender_deploy.prototxt"
    gender_model = "gender_net.caffemodel"

    model_mean_values = (78.4263377603, 87.7689143744, 114.895847746)
    age_list = ["(0-2)", "(4-6)", "(8-12)", "(15-20)", "(25-32)", "(38-43)", "(48-53)", "(60-100)"]
    gender_list = ["Male", "Female"]

    face_net = cv2.dnn.readNet(face_model, face_proto)
    age_net = cv2.dnn.readNet(age_model, age_proto)
    gender_net = cv2.dnn.readNet(gender_model, gender_proto)

    video = cv2.VideoCapture(args.image if args.image else 0)
    if not video.isOpened():
        raise RuntimeError("Could not open the camera or video file.")

    padding = 20

    try:
        while True:
            has_frame, frame = video.read()
            if not has_frame:
                break

            result_img, face_boxes = highlight_face(face_net, frame)
            male_count = female_count = 0

            for face_box in face_boxes:
                x1, y1, x2, y2 = face_box
                face = frame[
                    max(0, y1 - padding): min(y2 + padding, frame.shape[0]),
                    max(0, x1 - padding): min(x2 + padding, frame.shape[1]),
                ]
                if face.size == 0:
                    continue

                blob = cv2.dnn.blobFromImage(
                    face, 1.0, (227, 227), model_mean_values, swapRB=False
                )

                gender_net.setInput(blob)
                gender = gender_list[int(gender_net.forward()[0].argmax())]
                male_count += gender == "Male"
                female_count += gender == "Female"

                age_net.setInput(blob)
                age = age_list[int(age_net.forward()[0].argmax())]
                print(f"Gender: {gender}, Age: {age[1:-1]} years")

                cv2.putText(
                    result_img, f"{gender}, {age}", (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA
                )

                hands = detect_hands(frame, face_box)
                for hx1, hy1, hx2, hy2 in hands:
                    cv2.rectangle(result_img, (hx1, hy1), (hx2, hy2), (255, 0, 0), 2)

                if check_sos_gesture(face_box, hands):
                    cv2.putText(
                        result_img, "SOS Detected!", (x1, max(30, y1 - 50)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA
                    )

            cv2.putText(
                result_img, f"Male: {male_count}, Female: {female_count}",
                (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA
            )
            cv2.imshow("Detection Demo", result_img)

            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                break
    finally:
        video.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

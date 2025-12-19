import cv2


def show_resized(window_name, image, max_width=1200, max_height=800):
    h, w = image.shape[:2]
    scale = min(max_width / w, max_height / h, 1.0)

    resized = cv2.resize(
        image,
        (int(w * scale), int(h * scale)),
        interpolation=cv2.INTER_AREA
    )

    cv2.imshow(window_name, resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

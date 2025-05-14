import cv2
import os

# Global variables
drawing = False
ix, iy = -1, -1
bounding_boxes = []
current_image_index = 0
image_files = []

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, bounding_boxes, img

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = img.copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('image', img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        bounding_boxes.append((ix, iy, x, y))
        cv2.rectangle(img, (ix, iy), (x, y), (0, 255, 0), 2)

def annotate_images(image_folder):
    global img, current_image_index, image_files, bounding_boxes

    image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', draw_rectangle)

    while current_image_index < len(image_files):
        bounding_boxes = []
        img_path = os.path.join(image_folder, image_files[current_image_index])
        img = cv2.imread(img_path)
        img_copy = img.copy()

        while True:
            cv2.imshow('image', img)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('n'):  # Press 'n' to go to the next image
                if bounding_boxes:
                    save_annotations(image_folder, image_files[current_image_index], bounding_boxes)
                current_image_index += 1
                break
            elif key == ord('q'):  # Press 'q' to quit
                return
            elif key == ord('u'):  # Press 'u' to undo the last bounding box
                if bounding_boxes:
                    bounding_boxes.pop()
                    img = img_copy.copy()
                    for bbox in bounding_boxes:
                        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                cv2.imshow('image', img)

        if current_image_index >= len(image_files):
            break

    cv2.destroyAllWindows()

def save_annotations(image_folder, image_filename, bounding_boxes):
    annotation_filename = os.path.splitext(image_filename)[0] + '.txt'
    annotation_path = os.path.join(image_folder, annotation_filename)

    with open(annotation_path, 'w') as f:
        for bbox in bounding_boxes:
            f.write(f'{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}\n')

# Example usage
image_folder = r"...\frame_1" 
annotate_images(image_folder)
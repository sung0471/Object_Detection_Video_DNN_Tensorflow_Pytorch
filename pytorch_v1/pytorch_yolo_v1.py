from __future__ import division
import argparse
import time
import cv2
import sys
import torch
from pytorch_v1.darknet_pytorch_v1 import Darknet
from pytorch_v1.detection_boxes_pytorch_v1 import DetectBoxes

def arg_parse():
    """ Parsing Arguments for detection """

    parser = argparse.ArgumentParser(description='Pytorch Yolov3')
    parser.add_argument("--video", help="Path where video is located",
                        default="../assets/cars.mp4", type=str)
    parser.add_argument("--config",  help="Yolov3 config file", default="../darknet/yolov3.cfg")
    parser.add_argument("--weight",  help="Yolov3 weight file", default="../darknet/yolov3.weights")
    parser.add_argument("--conf", dest="confidence", help="Confidence threshold for predictions", default=0.5)
    parser.add_argument("--nms", dest="nmsThreshold", help="NMS threshold", default=0.4)
    parser.add_argument("--resolution", dest='resol', help="Input resolution of network. Higher "
                                                           "increases accuracy but decreases speed",
                        default="320", type=str)
    parser.add_argument("--webcam", help="Detect with web camera", default=False)
    return parser.parse_args()


def main():
    args = arg_parse()

    VIDEO_PATH = args.video if not args.webcam else 0

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("Loading network.....")
    model = Darknet(args.config).to(device)
    model.load_weights(args.weight)
    print("Network successfully loaded")

    model.net_info["height"] = args.resol
    inp_dim = int(model.net_info["height"])
    assert inp_dim % 32 == 0
    assert inp_dim > 32

    model.eval()

    PATH_TO_LABELS = '../labels/coco.names'

    # load detection class, default confidence threshold is 0.5
    detect = DetectBoxes(PATH_TO_LABELS, conf_threshold=args.confidence, nms_threshold=args.nmsThreshold)

    # Set window
    winName = 'YOLO-Pytorch'

    try:
        # Read Video file
        cap = cv2.VideoCapture(VIDEO_PATH)
    except IOError:
        print("Input video file", VIDEO_PATH, "doesn't exist")
        sys.exit(1)

    while cap.isOpened():
        hasFrame, frame = cap.read()

        if not hasFrame:
            break

        start = time.time()
        detect.bounding_box_yolo_v1(frame, inp_dim, model)
        end = time.time()

        cv2.putText(frame, '{:.2f}ms'.format((end - start) * 1000), (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (255, 0, 0), 2)

        cv2.imshow(winName, frame)
        print("FPS {:5.2f}".format(1 / (end - start)))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Video ended")

    # releases video and removes all windows generated by the program
    cap.release()
    cv2.destroyAllWindows()


# Starting a program
if __name__ == "__main__":
    main()
import math
import sys

def flatten_bbox(bbox):
    bbox = [ index for j in bbox for index in j ]
    return bbox

def flatten_bboxes(bboxes):
    bboxes = [ flatten_bbox(i) for i in bboxes ]
    return bboxes

def get_bbox_tl_br_corner(bbox):
    tl_x, tl_y, tr_x, tr_y, br_x, br_y, bl_x, bl_y = bbox
    min_x = min(tl_x, tr_x, br_x, bl_x)
    min_y = min(tl_y, tr_y, br_y, bl_y)
    max_x = max(tl_x, tr_x, br_x, bl_x)
    max_y = max(tl_y, tr_y, br_y, bl_y)
    bbox = [ min_x, min_y, max_x, max_y ]
    return bbox

def get_bboxes_tl_br_corner(bboxes):
    return [ get_bbox_tl_br_corner(i) for i in bboxes ]

def dilate_bbox(bbox, domain_size=[0, 0, sys.maxsize, sys.maxsize], padding=5):
    domain_min_x, domain_min_y, domain_max_x, domain_max_y = domain_size
    bbox = [
        max(domain_min_x, bbox[0] - padding),
        max(domain_min_y, bbox[1] - padding),
        min(domain_max_x, bbox[2] + padding),
        min(domain_max_y, bbox[3] + padding),    
    ]
    return bbox

def dilate_bboxes(bboxes, domain_size=[0, 0, sys.maxsize, sys.maxsize], padding=5):
    bboxes = [ dilate_bbox(i, domain_size=domain_size, padding=padding) for i in bboxes ]
    return bboxes

def calculate_distance(box1, box2):
    center1_x = (box1[0] + box1[2]) / 2
    center1_y = (box1[1] + box1[3]) / 2
    center2_x = (box2[0] + box2[2]) / 2
    center2_y = (box2[1] + box2[3]) / 2
    return math.sqrt((center1_x - center2_x)**2 + (center1_y - center2_y)**2)

def merge_bounding_boxes_based_on_distance(boxes, distance_threshold=50):
    merged_boxes = []
    remaining_boxes = list(boxes)

    while remaining_boxes:
        current_box = remaining_boxes.pop(0)
        merged_box = [current_box]

        for i in range(len(remaining_boxes) - 1, -1, -1):
            other_box = remaining_boxes[i]
            if calculate_distance(current_box, other_box) <= distance_threshold:
                merged_box.append(other_box)
                remaining_boxes.pop(i)

        min_x = min([box[0] for box in merged_box])
        min_y = min([box[1] for box in merged_box])
        max_x = max([box[2] for box in merged_box])
        max_y = max([box[3] for box in merged_box])
        merged_boxes.append([min_x, min_y, max_x, max_y])
    return merged_boxes

def calculate_iou(box1, box2):
    # box: [x_tl, y_tl, x_br, y_br]
    x1_tl, y1_tl, x1_br, y1_br = box1
    x2_tl, y2_tl, x2_br, y2_br = box2

    # Calculate intersection coordinates
    x_intersect_tl = max(x1_tl, x2_tl)
    y_intersect_tl = max(y1_tl, y2_tl)
    x_intersect_br = min(x1_br, x2_br)
    y_intersect_br = min(y1_br, y2_br)

    # Calculate intersection area
    width_intersect = x_intersect_br - x_intersect_tl
    height_intersect = y_intersect_br - y_intersect_tl

    if width_intersect <= 0 or height_intersect <= 0:
        return 0.0

    area_intersect = width_intersect * height_intersect

    # Calculate union area
    area_box1 = (x1_br - x1_tl) * (y1_br - y1_tl)
    area_box2 = (x2_br - x2_tl) * (y2_br - y2_tl)
    area_union = area_box1 + area_box2 - area_intersect

    if area_union == 0:
        return 0.0

    return area_intersect / area_union

def merge_boxes_iou(boxes, iou_threshold=0.05):
    merged_boxes = []
    # Create a list of booleans to track if a box has been merged
    merged_flags = [False] * len(boxes)

    for i in range(len(boxes)):
        if merged_flags[i]:
            continue

        current_cluster = [boxes[i]]
        merged_flags[i] = True

        # Keep merging as long as new boxes are added to the cluster
        while True:
            boxes_added_in_pass = False
            for j in range(len(boxes)):
                if not merged_flags[j]:
                    should_merge = False
                    for cluster_box in current_cluster:
                        if calculate_iou(cluster_box, boxes[j]) > iou_threshold:
                            should_merge = True
                            break
                    if should_merge:
                        current_cluster.append(boxes[j])
                        merged_flags[j] = True
                        boxes_added_in_pass = True
            if not boxes_added_in_pass:
                break
        
        # Calculate the bounding box of the entire cluster
        min_x = min([box[0] for box in current_cluster])
        min_y = min([box[1] for box in current_cluster])
        max_x = max([box[2] for box in current_cluster])
        max_y = max([box[3] for box in current_cluster])
        merged_boxes.append([min_x, min_y, max_x, max_y])
    return merged_boxes
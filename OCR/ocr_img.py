import time
from paddleocr import PaddleOCR

# 模型路径下必须含有model和params文件
# your_det_model_dir = 'D:/OCR/inference/ch_ppocr_server_v1.1_det_infer/'
# your_rec_model_dir = 'D:/OCR/inference/ch_ppocr_server_v1.1_rec_infer/'
# your_cls_model_dir = 'D:/OCR/inference/ch_ppocr_mobile_v1.1_cls_infer/'
#
# ocr = PaddleOCR(use_angle_cls=True, use_gpu=False, cls_thresh=0.4, det_model_dir=your_det_model_dir, rec_model_dir=your_rec_model_dir, cls_model_dir=your_cls_model_dir)
ocr = PaddleOCR(use_angle_cls=True, use_gpu=False)
img_path = '1.png'

result = ocr.ocr(img_path, cls=True)
# print(result)
for line in result:
    print(line)

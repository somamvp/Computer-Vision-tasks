# SOMA-vision-task

Jupyter ipython Colab files will be archived here

Based on **Yolov5** algorithm

Classes will be targeted to pedestrian environment

---

### Yolov5 pretrained specs
Trained image size: 640 * 640, Inference image size: 640 * 640

(자동 리사이징 되므로 원본 이미지 크기에 신경 쓸 필요는 없음)

모델에 들어갈땐 정사각형으로 맞춰서 들어감. Aspect Ratio 유지하려면 --rect 옵션 필수로 추가해줘야 함. (회색 padding이 생겨서 정사각형 모양 맞춰진다)

yolov5s (small) model is default / n,s,m,l,x model exists

Small or Medium is recommended

### Yolov7 specs
yolov7.pt 기본 모델이 v5 Medium 모델보다 크다.

추론 시간은 medium보다 살짝 느린 정도

직사각형 이미지 크기 지정 가능

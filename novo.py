from ultralytics import YOLO

# Sem balanceamento
model16_50 = YOLO("yolov8s.pt")
results_50 = model16_50.train(data="Vet_v8.yaml", epochs=50, imgsz=640, batch=16, plots=True, name="novo_v8s_50ep_detect")

model16_50val = YOLO("runs/detect/novo_v8s_50ep_detect/weights/best.pt")
metrics = model16_50val.val(data="Vet_v8_test.yaml", imgsz=640, batch=16, plots=True, conf=0.5, name="novo_v8s_50ep_detect_val")


model16_100 = YOLO("runs/detect/novo_v8s_50ep_detect/weights/last.pt")
results = model16_100.train(data="Vet_v8.yaml", epochs=50, imgsz=640, batch=16, plots=True, name="novo_v8s_100ep_detect")

model16_100val = YOLO("runs/detect/novo_v8s_100ep_detect/weights/best.pt")
metrics = model16_100val.val(data="Vet_v8_test.yaml", imgsz=640, batch=16, plots=True, conf=0.5, name="novo_v8s_100ep_detect_val")

# Com balanceamento
model16_50_balanced = YOLO("yolov8s.pt")
results_50 = model16_50_balanced.train(data="Vet_v8_balanced.yaml", epochs=50, imgsz=640, batch=16, plots=True, name="v8s_50ep_detect_balanced")

model16_50val_balanced = YOLO("runs/detect/v8s_50ep_detect_balanced/weights/best.pt")
metrics = model16_50val_balanced.val(data="Vet_v8_balanced_test.yaml", imgsz=640, batch=16, plots=True, conf=0.5, name="v8s_50ep_detect_balanced_val")

model16_100_balanced = YOLO("runs/detect/v8s_50ep_detect_balanced/weights/last.pt")
results = model16_100_balanced.train(data="Vet_v8_balanced.yaml", epochs=50, imgsz=640, batch=16, plots=True, name="v8s_100ep_detect_balanced")

model16_100val_balanced = YOLO("runs/detect/v8s_100ep_detect_balanced/weights/best.pt")
metrics = model16_100val_balanced.val(data="Vet_v8_balanced_test.yaml", imgsz=640, batch=16, plots=True, conf=0.5, name="v8s_100ep_detect_balanced_val")

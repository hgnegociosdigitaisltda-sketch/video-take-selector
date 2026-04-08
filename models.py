import streamlit as st
from ultralytics import YOLO
from faster_whisper import WhisperModel
import torch


def load_yolo_model():
    if st.session_state.model_yolo is None:
        model_size = st.session_state.yolo_model_size
        tracker_type = st.session_state.yolo_tracker.replace(".yaml", "")
        imgsz = st.session_state.yolo_imgsz
        conf = st.session_state.yolo_conf

        # Detecção automática de dispositivo
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"

        st.session_state.yolo_device = device
        st.session_state.yolo_half = (device == "cuda")

        with st.spinner(f"Carregando YOLOv10 + {tracker_type} em {device}..."):
            st.session_state.model_yolo = YOLO(model_size)
            st.session_state.model_yolo.to(device)

            # === WARM-UP SEGURO ===
            dummy = torch.zeros(1, 3, imgsz, imgsz, dtype=torch.float32, device=device)
            st.session_state.model_yolo.track(
                dummy,
                verbose=False,
                imgsz=imgsz,
                conf=conf,
                iou=0.45,
                max_det=20,
                tracker=f"{tracker_type}.yaml",
                persist=True,
                half=st.session_state.yolo_half
            )

    return st.session_state.model_yolo


def load_whisper_model():
    if st.session_state.use_whisper and st.session_state.whisper_model is None:
        with st.spinner("Carregando Whisper local (small)..."):
            st.session_state.whisper_model = WhisperModel(
                "small",
                device="cpu",
                compute_type="int8"
            )
    return st.session_state.whisper_model

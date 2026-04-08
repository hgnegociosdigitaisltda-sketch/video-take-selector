import tempfile
import os
import streamlit as st
import srt

def init_session_state():
    if "model_yolo" not in st.session_state: st.session_state.model_yolo = None
    if "whisper_model" not in st.session_state: st.session_state.whisper_model = None
    if "temp_dir" not in st.session_state:
        st.session_state.temp_dir = tempfile.mkdtemp()

    defaults = {
        "threshold_corte": 27, "padding": 0.1, "frames_por_take": 12,
        "max_takes_por_segmento": 5, "modo_sem_roteiro": False,
        "trim_inicial": 0.3, "use_audio": True, "use_whisper": True,
        "peso_audio": 1.3, "peso_whisper": 1.8, "run_analysis": False,
        "yolo_model_size": "yolov10n.pt", "yolo_tracker": "bytetrack.yaml",
        "yolo_imgsz": 640, "yolo_conf": 0.25, "yolo_device": "cpu",
        "yolo_half": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_config():
    return {k: st.session_state[k] for k in [
        "threshold_corte", "padding", "frames_por_take", "max_takes_por_segmento",
        "trim_inicial", "modo_sem_roteiro", "use_audio", "use_whisper",
        "peso_audio", "peso_whisper"
    ]}

def carregar_roteiro(srt_bytes):
    content = srt_bytes.decode("utf-8")
    subs = list(srt.parse(content))
    return [{"ordem": i+1, "texto": sub.content.strip(), "duracao": (sub.end - sub.start).total_seconds()} for i, sub in enumerate(subs)]
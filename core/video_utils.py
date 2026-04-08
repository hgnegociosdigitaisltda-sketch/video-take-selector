import os
import cv2
import numpy as np
from moviepy.editor import VideoFileClip
import streamlit as st
from collections import defaultdict

# ====================== FUNÇÃO PRINCIPAL QUE FALTAVA ======================
def analisar_take_frame_por_frame(clip, inicio, fim, caminho_video, model_yolo):
    """Analisa vários frames do take e calcula pontuação final"""
    duracao = fim - inicio
    if duracao < 1.8:  # mínimo de 1.8 segundos
        return None

    num_frames = st.session_state.get("frames_por_take", 12)
    step = max(duracao / (num_frames + 1), 0.1)
    resultados = []
    erros_frame = 0

    for i in range(1, num_frames + 1):
        tempo = inicio + i * step
        try:
            frame = clip.get_frame(tempo)
            frame_bgr = (frame * 255).astype(np.uint8)
            analise = analisar_frame_com_yolo(frame_bgr, model_yolo)
            if analise:
                resultados.append(analise)
        except Exception:
            erros_frame += 1
            continue

    if erros_frame > 0:
        st.warning(f"⚠️ {erros_frame} frames ignorados em {os.path.basename(caminho_video)} ({inicio:.1f}s–{fim:.1f}s)")

    if not resultados:
        return None

    # Média das pontuações
    pontuacao_media = sum(r["pontuacao_base"] for r in resultados) / len(resultados)
    product_detected = any(r["product_detected"] for r in resultados)
    bbox_ratio_media = sum(r["bbox_ratio"] for r in resultados) / len(resultados)

    return {
        "video": caminho_video,
        "inicio": round(inicio, 2),
        "fim": round(fim, 2),
        "duracao": round(duracao, 2),
        "pontuacao": round(pontuacao_media, 4),
        "product_detected": product_detected,
        "bbox_ratio_media": round(bbox_ratio_media, 4),
        "angulo_yolo": resultados[0].get("angulo_yolo", "indefinido")
    }


def detectar_angulo_camera(clip, inicio, fim, model_yolo):
    if model_yolo is None:
        return "indefinido"

    try:
        tempo_meio = (inicio + fim) / 2
        frame = clip.get_frame(tempo_meio)
        frame_bgr = (frame * 255).astype(np.uint8)
        results = model_yolo(frame_bgr, verbose=False)

        if len(results[0].boxes) == 0:
            return "indefinido"

        boxes = results[0].boxes.cpu()
        areas = [box.xywh[0][2] * box.xywh[0][3] for box in boxes]
        best_idx = np.argmax(areas)
        box = boxes[best_idx]

        x, y, w, h = box.xywh[0].tolist()
        conf = float(box.conf[0])
        frame_h, frame_w = frame_bgr.shape[:2]
        bbox_area = w * h
        frame_area = frame_w * frame_h
        bbox_ratio = bbox_area / frame_area
        center_y = y / frame_h

        if bbox_ratio > 0.35 or conf > 0.85:
            return "close_up"
        elif bbox_ratio > 0.18 and center_y < 0.45:
            return "top_view"
        elif 0.12 < bbox_ratio <= 0.35:
            return "medium_front" if center_y < 0.5 else "side_view"
        else:
            return "wide_shot"
    except Exception:
        return "indefinido"


# ====================== DETECÇÃO DE CORTES (AGORA USA CONFIG) ======================
def detectar_cortes_secos(caminho_video):
    threshold = st.session_state.get("threshold_corte", 25)
    padding = st.session_state.get("padding", 0.1)

    cap = cv2.VideoCapture(caminho_video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_skip = max(1, int(fps / 5))  # amostra ~5fps em vez de fps completo

    cortes = []
    frame_anterior = None
    ultimo_corte = 0.0
    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_skip == 0:
            if frame_anterior is not None:
                diff = cv2.absdiff(frame, frame_anterior)
                if np.mean(diff) > threshold:
                    timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                    corte_ajustado = round(timestamp - padding, 2)
                    if corte_ajustado > ultimo_corte + 0.5:
                        cortes.append(corte_ajustado)
                        ultimo_corte = corte_ajustado
            frame_anterior = frame.copy()
        frame_idx += 1

    cap.release()
    return sorted(list(set(cortes)))


# ====================== FUNÇÕES AUXILIARES ======================
def analisar_frame_individual(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    nitidez = cv2.Laplacian(gray, cv2.CV_64F).var()
    iluminacao = np.mean(gray)
    contraste = np.std(gray)
    edges = cv2.Canny(gray, 50, 150)
    densidade_bordas = np.mean(edges) / 255.0
    return {"nitidez": nitidez, "iluminacao": iluminacao, "contraste": contraste, "densidade_bordas": densidade_bordas}


def analisar_frame_com_yolo(frame, model_yolo):
    if model_yolo is None:
        # Modo sem IA: análise básica apenas
        metrics = analisar_frame_individual(frame)
        return {
            "pontuacao_base": round(metrics["nitidez"] / 2000 * 0.4 + metrics["densidade_bordas"] * 0.4 + 0.2, 4),
            "product_detected": False,
            "bbox_ratio": 0.0,
            "angulo_yolo": "indefinido"
        }

    results = model_yolo(frame, verbose=False)[0]
    boxes = results.boxes.cpu() if hasattr(results.boxes, 'cpu') else results.boxes

    product_detected = False
    bbox_ratio = 0.0

    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        w = x2 - x1
        h = y2 - y1
        area = w * h
        frame_area = frame.shape[0] * frame.shape[1]
        bbox_ratio = area / frame_area

        if cls == 0:   # produto (chinelo)
            product_detected = True

    metrics = analisar_frame_individual(frame)

    pontuacao = (
        (metrics["nitidez"] / 2000 * 0.22) +
        (metrics["densidade_bordas"] * 0.20) +
        (1.0 if product_detected else 0.0) * 0.25 +
        (bbox_ratio * 0.18) +
        0.15
    )

    return {
        "pontuacao_base": round(pontuacao, 4),
        "product_detected": product_detected,
        "bbox_ratio": bbox_ratio,
        "angulo_yolo": "indefinido"
    }


def classificar_take(clip, caminho_video, inicio, fim, model_yolo, config):
    take = analisar_take_frame_por_frame(clip, inicio, fim, caminho_video, model_yolo)
    if not take:
        return None

    angulo = detectar_angulo_camera(clip, inicio, fim, model_yolo)
    take["angulo"] = angulo

    # Boost em ângulos bons
    if angulo in ["close_up", "top_view", "medium_front", "person_wearing"]:
        take["pontuacao"] = take.get("pontuacao", 0) * 1.4

    return take
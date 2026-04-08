import streamlit as st


def render_sidebar():
    # ====================== CONFIGURAÇÃO DO MODELO ======================
    st.header("🤖 Modelo de IA")

    model_size = st.selectbox(
        "📏 Tamanho do modelo YOLO",
        options=["yolov10n.pt", "yolov10s.pt", "yolov10m.pt"],
        index=["yolov10n.pt", "yolov10s.pt", "yolov10m.pt"].index(st.session_state.yolo_model_size)
    )
    tracker = st.selectbox(
        "🔗 Tracker",
        options=["bytetrack", "botsort"],
        index=0 if st.session_state.yolo_tracker == "bytetrack.yaml" else 1,
        help="ByteTrack = mais rápido | BoTSORT = mais preciso"
    )
    imgsz = st.selectbox(
        "📐 Tamanho de entrada",
        options=[480, 640, 800],
        index=[480, 640, 800].index(st.session_state.yolo_imgsz)
    )
    conf = st.slider("🔍 Confiança mínima", 0.15, 0.45, st.session_state.yolo_conf, step=0.05)

    device_label = st.session_state.get("yolo_device", "cpu").upper()
    st.info(f"🖥️ Dispositivo: **{device_label}**")

    # Aplica mudanças de config e força reload se necessário
    config_changed = (
        model_size != st.session_state.yolo_model_size or
        f"{tracker}.yaml" != st.session_state.yolo_tracker or
        imgsz != st.session_state.yolo_imgsz or
        conf != st.session_state.yolo_conf
    )
    st.session_state.yolo_model_size = model_size
    st.session_state.yolo_tracker = f"{tracker}.yaml"
    st.session_state.yolo_imgsz = imgsz
    st.session_state.yolo_conf = conf

    if config_changed and st.session_state.model_yolo is not None:
        st.warning("⚠️ Configuração alterada. Clique em Recarregar para aplicar.")

    if st.button("🔄 Recarregar Modelos", use_container_width=True):
        st.session_state.model_yolo = None
        st.session_state.whisper_model = None
        st.rerun()

    # ====================== CONFIGURAÇÕES DE PROCESSAMENTO ======================
    st.divider()
    st.header("⚙️ Configurações")
    st.session_state.threshold_corte = st.slider("Threshold de corte seco", 20, 40, st.session_state.threshold_corte)
    st.session_state.padding = st.slider("Padding entre takes (segundos)", 0.0, 0.5, st.session_state.padding, step=0.05)
    st.session_state.frames_por_take = st.slider("Frames analisados por take", 6, 20, st.session_state.frames_por_take)
    st.session_state.max_takes_por_segmento = st.slider("Máx. takes por segmento", 3, 10, st.session_state.max_takes_por_segmento)
    st.session_state.trim_inicial = st.slider("Corte inicial em cada take (segundos)", 0.0, 1.0, st.session_state.trim_inicial, step=0.1)

    st.divider()
    st.session_state.use_audio = st.toggle("🔊 Ativar Análise Avançada de Áudio", value=st.session_state.use_audio)
    st.session_state.peso_audio = st.slider("Peso da análise de áudio", 0.5, 3.0, st.session_state.peso_audio, step=0.1)
    st.session_state.use_whisper = st.toggle("📝 Usar Whisper (transcrição local)", value=st.session_state.use_whisper)
    st.session_state.peso_whisper = st.slider("Peso da transcrição Whisper", 0.5, 3.0, st.session_state.peso_whisper, step=0.1)

    st.divider()
    st.session_state.modo_sem_roteiro = st.toggle("🔄 Modo sem roteiro", value=st.session_state.modo_sem_roteiro)

    # ====================== UPLOADS ======================
    st.divider()
    uploaded_srt = st.file_uploader("📄 Upload do roteiro.srt", type=["srt"]) if not st.session_state.modo_sem_roteiro else None
    uploaded_videos = st.file_uploader("🎥 Upload dos vídeos (.mp4)", type=["mp4"], accept_multiple_files=True)

    if st.button("🚀 INICIAR ANÁLISE", type="primary", use_container_width=True):
        if not uploaded_videos:
            st.error("❌ Envie pelo menos um vídeo!")
        elif not st.session_state.modo_sem_roteiro and not uploaded_srt:
            st.error("❌ Envie o .srt ou ative o Modo sem roteiro!")
        else:
            st.session_state.run_analysis = True
            st.session_state.uploaded_srt = uploaded_srt
            st.session_state.uploaded_videos = uploaded_videos

    return uploaded_srt, uploaded_videos

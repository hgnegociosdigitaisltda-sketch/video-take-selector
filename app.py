import streamlit as st
import os
import warnings
import logging
from datetime import datetime

# ====================== VERIFICAÇÃO DE DEPENDÊNCIAS CRÍTICAS ======================
try:
    import cv2
    print("✅ OpenCV importado com sucesso")
except ImportError as e:
    st.error(f"❌ Erro crítico: OpenCV não pode ser importado: {e}")
    st.error("Isso pode indicar um problema com as dependências do sistema.")
    st.stop()

# ====================== IMPORTS DO SEU PROJETO ======================
from core.processor import (
    processar_video,
    alinhar_e_selecionar,
    exportar_take,
    gerar_relatorio_e_zip
)
from core.config import init_session_state, get_config, carregar_roteiro
from core.models import load_yolo_model, load_whisper_model
from ui.sidebar import render_sidebar
from ui.styles import apply_custom_styles
from moviepy.editor import VideoFileClip

# ====================== SUPRESSÃO TOTAL DE WARNINGS (M4) ======================
warnings.filterwarnings("ignore", message="missing ScriptRunContext")
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
os.environ["STREAMLIT_LOGGER_LEVEL"] = "error"
os.environ["PYTHONWARNINGS"] = "ignore"
logging.getLogger("streamlit").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime.scriptrunner").setLevel(logging.ERROR)

st.set_page_config(
    page_title="🎬 Seleção Inteligente de Takes",
    layout="wide",
    page_icon="🎥"
)

apply_custom_styles()

st.title("🎬 Seleção Inteligente de Takes")
st.markdown("YOLOv10 + Ângulos Automáticos — Otimizado para Apple Silicon M4")

# ====================== INICIALIZAÇÃO ======================
init_session_state()
model_yolo = load_yolo_model()
whisper_model = load_whisper_model()

# ====================== PASTAS ======================
UPLOAD_DIR = os.path.join(st.session_state.temp_dir, "uploads")
TODOS_DIR = os.path.join(st.session_state.temp_dir, "todos_takes_detectados")
TAKES_DIR = os.path.join(st.session_state.temp_dir, "takes_selecionados")
REPORT_DIR = os.path.join(st.session_state.temp_dir, "relatorios")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TODOS_DIR, exist_ok=True)
os.makedirs(TAKES_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# ====================== SIDEBAR ======================
uploaded_srt, uploaded_videos = render_sidebar()

# ====================== EXECUÇÃO DA ANÁLISE ======================
if st.session_state.get("run_analysis") and uploaded_videos:
    with st.spinner("🚀 Processando vídeos com IA no M4..."):
        config = get_config()

        # Salva os vídeos enviados
        video_paths = []
        for vid in uploaded_videos:
            path = os.path.join(UPLOAD_DIR, vid.name)
            with open(path, "wb") as f:
                f.write(vid.getbuffer())
            video_paths.append(path)

        # Carrega roteiro ou modo sem roteiro
        if not config["modo_sem_roteiro"] and uploaded_srt:
            segmentos = carregar_roteiro(uploaded_srt.getbuffer())
        else:
            clips = [VideoFileClip(p) for p in video_paths]
            total_dur = sum(c.duration for c in clips)
            for c in clips:
                c.close()
            segmentos = [{"ordem": 1, "texto": "Seleção automática", "duracao": total_dur}]

        # ====================== PROCESSAMENTO ======================
        todos_takes = []
        progress_bar = st.progress(0)

        from functools import partial
        process_fn = partial(processar_video, config=config, model_yolo=model_yolo, whisper_model=whisper_model)

        for i, video_path in enumerate(video_paths):
            takes = process_fn(video_path)
            todos_takes.extend(takes)
            progress_bar.progress((i + 1) / len(video_paths))

        st.write(f"**🔍 Total de takes detectados:** {len(todos_takes)}")

        # Alinhamento inteligente (já agrupa por qualidade e ângulo)
        alinhamento_final = alinhar_e_selecionar(
            todos_takes,
            segmentos,
            config["max_takes_por_segmento"]
        )

        # ====================== EXPORTAÇÃO ======================
        # Ordena todos os takes por ângulo antes de exportar
        todos_takes_ordenados = sorted(todos_takes, key=lambda t: t.get("angulo", "indefinido"))
        angulo_counters_todos = {}
        angulo_ids_todos = {}
        for take in todos_takes_ordenados:
            exportar_take(take, TODOS_DIR, angulo_counters=angulo_counters_todos, angulo_ids=angulo_ids_todos)

        alinhamento_ordenado = sorted(alinhamento_final, key=lambda i: i["take"].get("angulo", "indefinido"))
        angulo_counters_sel = {}
        angulo_ids_sel = {}
        for item in alinhamento_ordenado:
            exportar_take(item, TAKES_DIR, angulo_counters=angulo_counters_sel, angulo_ids=angulo_ids_sel)

        # === Relatório + ZIP ===
        zip_path, csv_path = gerar_relatorio_e_zip(alinhamento_final, TODOS_DIR)

        st.success(f"🎉 Análise concluída! {len(todos_takes)} takes processados e agrupados por ângulo.")

        # ====================== DOWNLOADS ======================
        col1, col2 = st.columns(2)
        with col1:
            if zip_path and os.path.exists(zip_path):
                with open(zip_path, "rb") as f:
                    st.download_button(
                        "⬇️ Baixar TODOS os Takes (ZIP)",
                        f,
                        file_name=os.path.basename(zip_path),
                        mime="application/zip"
                    )
        with col2:
            if csv_path and os.path.exists(csv_path):
                with open(csv_path, "rb") as f:
                    st.download_button(
                        "⬇️ Baixar Relatório CSV",
                        f,
                        file_name="relatorio_selecao.csv",
                        mime="text/csv"
                    )

        # ====================== PREVIEW ======================
        st.subheader("👀 Preview dos takes selecionados")
        for item in alinhamento_final[:6]:
            nome_preview = f"{item['ordem_roteiro']:02d}_Take{item['posicao_qualidade']:02d}_{item['video_origem']}.mp4"
            video_file = os.path.join(TAKES_DIR, nome_preview)
            if os.path.exists(video_file):
                st.video(video_file)
                st.caption(
                    f"**Ordem {item['ordem_roteiro']}** • "
                    f"Ângulo: **{item['take'].get('angulo', 'N/A')}** • "
                    f"Pontuação: **{item['take']['pontuacao']}**"
                )
            else:
                st.warning(f"Preview não encontrado: {nome_preview}")

        # Reseta para próxima execução
        st.session_state.run_analysis = False
import os
import zipfile
from datetime import datetime
import pandas as pd
import streamlit as st
from moviepy.editor import VideoFileClip

def processar_video(video_path, config, model_yolo, whisper_model=None):
    try:
        clip = VideoFileClip(video_path)
        cortes = detectar_cortes_secos(video_path)

        # REFORÇO MÁXIMO se não detectar cortes
        if len(cortes) < 3:
            st.info(f"⚠️ Poucos cortes em {os.path.basename(video_path)}. Forçando modo ultra-sensível.")
            cortes = [i * (clip.duration / 10) for i in range(1, 10)]

        cortes_completos = [0.0] + cortes + [clip.duration]
        takes = []

        for i in range(len(cortes_completos) - 1):
            inicio = cortes_completos[i]
            fim = cortes_completos[i + 1]
            take = classificar_take(clip, video_path, inicio, fim, model_yolo, config)
            if take:
                takes.append(take)

        clip.close()
        st.info(f"📹 {os.path.basename(video_path)} → **{len(takes)} takes** gerados")
        return takes

    except Exception as e:
        st.error(f"Erro ao processar {os.path.basename(video_path)}: {str(e)}")
        return []


def alinhar_e_selecionar(todos_takes, segmentos, max_takes):
    """VERSÃO TURBINADA - REFORÇO MÁXIMO (aceita quase tudo)"""
    alinhamento = []
    usados = set()

    st.write(f"🔍 Total de takes detectados: **{len(todos_takes)}**")

    for seg in segmentos:
        candidatos = [t for t in todos_takes if (t["video"], round(t["inicio"], 2), round(t["fim"], 2)) not in usados]
        if not candidatos:
            continue

        # Filtra por duração compatível com o segmento (máx 2x a duração esperada)
        duracao_seg = seg.get("duracao", float("inf"))
        candidatos_por_duracao = [t for t in candidatos if t["duracao"] <= duracao_seg * 2.0]
        if not candidatos_por_duracao:
            candidatos_por_duracao = candidatos  # fallback: aceita todos se nenhum bater

        candidatos_filtrados = sorted(candidatos_por_duracao, key=lambda x: x.get("pontuacao", 0), reverse=True)
        selecionados = candidatos_filtrados[:max_takes * 2]

        for pos, take in enumerate(selecionados[:max_takes]):
            chave = (take["video"], round(take["inicio"], 2), round(take["fim"], 2))
            usados.add(chave)
            alinhamento.append({
                "ordem_roteiro": seg["ordem"],
                "posicao_qualidade": pos + 1,
                "video_origem": os.path.basename(take["video"]),
                "contagem_video": f"take_{pos + 1}",
                "take": take,
                "texto_roteiro": seg.get("texto", "")
            })

    total_selecionados = len(alinhamento)
    st.success(f"✅ Takes selecionados: **{total_selecionados}** (máximo {max_takes} por segmento)")
    st.info(f"📊 Takes únicos utilizados: **{len(usados)}** de {len(todos_takes)}")
    return alinhamento


# As outras funções permanecem iguais (exportar, gerar_relatorio, etc.)
def exportar_take(item, output_dir, angulo_counters=None, angulo_ids=None, prefix=""):
    try:
        take = item if isinstance(item, dict) and "inicio" in item else item["take"]
        angulo = take.get("angulo", "indefinido").replace(" ", "_")
        video_nome = os.path.basename(take["video"]).replace(".mp4", "").replace(" ", "_").replace("-", "_")

        if angulo_counters is not None and angulo_ids is not None:
            # Atribui número fixo ao ângulo na primeira vez que aparece
            if angulo not in angulo_ids:
                angulo_ids[angulo] = len(angulo_ids) + 1
            angulo_num = angulo_ids[angulo]
            angulo_counters[angulo] = angulo_counters.get(angulo, 0) + 1
            contador = angulo_counters[angulo]
            nome_base = f"{prefix}{angulo_num}_{contador:02d}_{video_nome}"
        else:
            nome_base = f"{prefix}{angulo}_{video_nome}"

        nome_arquivo = f"{nome_base}.mp4"
        caminho_saida = os.path.join(output_dir, nome_arquivo)

        counter = 1
        while os.path.exists(caminho_saida):
            nome_arquivo = f"{nome_base}_{counter}.mp4"
            caminho_saida = os.path.join(output_dir, nome_arquivo)
            counter += 1

        inicio_com_trim = take["inicio"] + st.session_state.get("trim_inicial", 0.0)
        fim_com_trim = take["fim"]

        clip = VideoFileClip(take["video"]).subclipped(inicio_com_trim, fim_com_trim)
        clip.write_videofile(
            caminho_saida, codec="libx264", audio=True,
            preset="fast", ffmpeg_params=["-crf", "23"], threads=4
        )
        clip.close()
        st.success(f"✅ Exportado: **{nome_arquivo}**")
        return True
    except Exception as e:
        st.error(f"Erro ao exportar: {str(e)}")
        return False


def gerar_relatorio_e_zip(alinhamento_final, todos_dir):
    zip_path = None
    csv_path = None

    try:
        zip_path = os.path.join(os.path.dirname(todos_dir), f"todos_takes_{datetime.now().strftime('%Y%m%d_%H%M')}.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, _, files in os.walk(todos_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), file)
    except Exception as e:
        st.error(f"❌ Erro ao gerar ZIP: {e}")
        zip_path = None

    try:
        csv_path = os.path.join(os.path.dirname(todos_dir), "relatorio_selecao.csv")
        df = pd.DataFrame([
            {
                "ordem": item["ordem_roteiro"],
                "posicao": item["posicao_qualidade"],
                "video": item["video_origem"],
                "take": item["contagem_video"],
                "angulo": item["take"].get("angulo", "N/A"),
                "inicio": item["take"]["inicio"],
                "fim": item["take"]["fim"],
                "duracao": item["take"]["duracao"],
                "pontuacao": item["take"]["pontuacao"],
                "texto_roteiro": item.get("texto_roteiro", "")
            }
            for item in alinhamento_final
        ])
        df.to_csv(csv_path, index=False, encoding="utf-8")
    except Exception as e:
        st.error(f"❌ Erro ao gerar CSV: {e}")
        csv_path = None

    return zip_path, csv_path
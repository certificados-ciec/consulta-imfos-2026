import html
import os
from pathlib import Path

import streamlit as st

from imfos_data import DataSourceError, load_submissions, search_by_id


st.set_page_config(
    page_title="Consulta de sugerencias | ImFoS 2026",
    page_icon="🔬",
    layout="centered",
)

st.markdown(
    """
    <style>
      .block-container {max-width: 760px; padding-top: 3rem;}
      .imfos-card {
        border: 1px solid rgba(49, 51, 63, 0.18);
        border-radius: 14px;
        padding: 1.2rem 1.3rem;
        margin: 0.8rem 0 1.2rem;
        background: rgba(248, 249, 251, 0.55);
      }
      .imfos-card h3 {margin: 0 0 0.8rem; font-size: 1.12rem;}
      .imfos-card p {margin-bottom: 0; line-height: 1.55;}
      .privacy-note {color: #5f6368; font-size: 0.9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Consulta de sugerencias")
st.write(
    "Ingresa tu número de identificación para consultar las sugerencias "
    "asociadas a tu ponencia en ImFoS 2026."
)


def configured_source() -> dict[str, str | None]:
    try:
        remote_url = st.secrets.get("DATA_EXCEL_URL") or st.secrets.get(
            "ONEDRIVE_EXCEL_URL"
        )
        local_value = st.secrets.get(
            "LOCAL_EXCEL_PATH", "Inscripciones ImFos (2026).xlsx"
        )
    except FileNotFoundError:
        remote_url = os.getenv("DATA_EXCEL_URL") or os.getenv("ONEDRIVE_EXCEL_URL")
        local_value = os.getenv(
            "LOCAL_EXCEL_PATH", "Inscripciones ImFos (2026).xlsx"
        )
    return {
        "remote_url": remote_url,
        "local_path": str(Path(local_value)),
    }


@st.cache_data(ttl=300, show_spinner=False)
def current_records(source: dict[str, str | None]):
    return load_submissions(
        remote_url=source["remote_url"],
        local_path=Path(source["local_path"] or ""),
    )


with st.form("consulta", clear_on_submit=False):
    identification = st.text_input(
        "Número de identificación",
        placeholder="Escribe el número sin puntos ni espacios",
        type="password",
        autocomplete="off",
    )
    submitted = st.form_submit_button("Consultar", type="primary", use_container_width=True)

st.markdown(
    '<p class="privacy-note">El número se utiliza únicamente para realizar esta consulta.</p>',
    unsafe_allow_html=True,
)

if submitted:
    source = configured_source()

    try:
        records = current_records(source)
    except DataSourceError:
        st.error(
            "No fue posible consultar la información en este momento. "
            "Por favor, intenta nuevamente más tarde."
        )
        st.stop()

    matches = search_by_id(records, identification)

    if matches.empty:
        st.warning(
            "No encontramos ponencias asociadas a ese número. "
            "Verifica el dato e intenta de nuevo."
        )
    else:
        author = html.escape(matches.iloc[0]["name"])
        count = len(matches)
        st.success(
            f"Encontramos {count} {'ponencia' if count == 1 else 'ponencias'} "
            f"a nombre de {author}."
        )

        for position, row in enumerate(matches.itertuples(index=False), start=1):
            title = html.escape(row.title or "Ponencia sin título registrado")
            suggestion = html.escape(
                row.suggestion or "Aún no hay una sugerencia registrada."
            )
            st.markdown(
                f"""
                <section class="imfos-card">
                  <h3>{position}. {title}</h3>
                  <p><strong>Sugerencia para enriquecer el trabajo</strong></p>
                  <p>{suggestion}</p>
                </section>
                """,
                unsafe_allow_html=True,
            )

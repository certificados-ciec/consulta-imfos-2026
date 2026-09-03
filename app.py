import html
import os
from pathlib import Path

import streamlit as st

from imfos_data import DataSourceError, load_submissions, search_by_id


st.set_page_config(
    page_title="Consulta de sugerencias | ImFoS 2026",
    page_icon="🔬",
    layout="wide",
)

st.markdown(
    """
    <style>
      :root {
        --imfos-navy: #001a4d;
        --imfos-blue: #0067d9;
        --imfos-gold: #f5b820;
        --imfos-ink: #17324d;
        --imfos-surface: #ffffff;
      }

      .stApp {
        background:
          radial-gradient(circle at 8% 8%, rgba(0, 103, 217, 0.12), transparent 24rem),
          radial-gradient(circle at 92% 18%, rgba(245, 184, 32, 0.12), transparent 20rem),
          linear-gradient(180deg, #f6f9ff 0%, #ffffff 45%, #f7faff 100%);
      }

      [data-testid="stHeader"] {background: transparent;}
      [data-testid="stToolbar"], footer {visibility: hidden;}

      .block-container {
        max-width: 980px;
        padding-top: 1.2rem;
        padding-bottom: 3rem;
      }

      [data-testid="stImage"] {
        border: 2px solid rgba(245, 184, 32, 0.8);
        border-radius: 20px;
        box-shadow: 0 16px 38px rgba(0, 26, 77, 0.24);
        overflow: hidden;
      }

      [data-testid="stImage"] img {display: block; width: 100%;}

      .imfos-intro {
        margin: 1.5rem auto 1.15rem;
        text-align: center;
      }

      .imfos-kicker {
        display: inline-block;
        margin-bottom: 0.55rem;
        padding: 0.35rem 0.85rem;
        border: 1px solid rgba(0, 103, 217, 0.22);
        border-radius: 999px;
        background: rgba(0, 103, 217, 0.07);
        color: var(--imfos-blue);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }

      .imfos-intro h1 {
        margin: 0;
        color: var(--imfos-navy);
        font-size: clamp(1.8rem, 4vw, 2.65rem);
        line-height: 1.12;
      }

      .imfos-intro p {
        max-width: 680px;
        margin: 0.7rem auto 0;
        color: #50647b;
        font-size: 1.02rem;
      }

      [data-testid="stForm"] {
        max-width: 720px;
        margin: 0 auto;
        padding: 1.35rem 1.45rem 1.25rem;
        border: 1px solid rgba(0, 103, 217, 0.2);
        border-top: 5px solid var(--imfos-gold);
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.94);
        box-shadow: 0 12px 30px rgba(0, 45, 105, 0.1);
      }

      [data-testid="stForm"] label p {
        color: var(--imfos-navy);
        font-weight: 750;
      }

      [data-baseweb="input"] {
        border-radius: 11px;
        background: #f8fbff;
      }

      .stButton > button,
      [data-testid="stFormSubmitButton"] > button {
        min-height: 3rem;
        border: 1px solid #f4c847;
        border-radius: 11px;
        background: linear-gradient(135deg, #ffc928 0%, #ee9f00 100%);
        color: var(--imfos-navy);
        font-weight: 850;
        box-shadow: 0 7px 16px rgba(238, 159, 0, 0.24);
        transition: transform 160ms ease, box-shadow 160ms ease;
      }

      .stButton > button:hover,
      [data-testid="stFormSubmitButton"] > button:hover {
        border-color: #ffd75f;
        color: var(--imfos-navy);
        transform: translateY(-1px);
        box-shadow: 0 10px 20px rgba(238, 159, 0, 0.3);
      }

      .privacy-note {
        max-width: 720px;
        margin: 0.7rem auto 1.35rem;
        color: #64758a;
        font-size: 0.88rem;
        text-align: center;
      }

      [data-testid="stAlert"] {
        max-width: 720px;
        margin-left: auto;
        margin-right: auto;
        border-radius: 13px;
      }

      .imfos-card {
        position: relative;
        max-width: 720px;
        margin: 1rem auto 1.25rem;
        padding: 1.3rem 1.4rem 1.4rem;
        overflow: hidden;
        border: 1px solid rgba(0, 103, 217, 0.2);
        border-left: 6px solid var(--imfos-blue);
        border-radius: 15px;
        background: var(--imfos-surface);
        box-shadow: 0 10px 24px rgba(0, 45, 105, 0.09);
      }

      .imfos-card::after {
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        width: 92px;
        height: 5px;
        background: var(--imfos-gold);
      }

      .imfos-card h3 {
        margin: 0 0 0.85rem;
        color: var(--imfos-navy);
        font-size: 1.13rem;
        line-height: 1.4;
      }

      .imfos-card .suggestion-label {
        margin: 0 0 0.35rem;
        color: var(--imfos-blue);
        font-size: 0.77rem;
        font-weight: 850;
        letter-spacing: 0.06em;
        text-transform: uppercase;
      }

      .imfos-card p:last-child {
        margin: 0;
        color: var(--imfos-ink);
        line-height: 1.65;
      }

      @media (max-width: 640px) {
        .block-container {padding: 0.65rem 0.8rem 2rem;}
        [data-testid="stImage"] {border-radius: 13px;}
        .imfos-intro {margin-top: 1.2rem;}
        [data-testid="stForm"] {padding: 1.05rem;}
      }
    </style>
    """,
    unsafe_allow_html=True,
)

banner_path = Path(__file__).parent / "assets" / "banner-imfos-2026.png"
st.image(str(banner_path), width="stretch")

st.markdown(
    """
    <section class="imfos-intro">
      <span class="imfos-kicker">Portal para autores</span>
      <h1>Consulta de sugerencias</h1>
      <p>Ingresa tu número de identificación para consultar las sugerencias
      asociadas a tu ponencia en ImFoS 2026.</p>
    </section>
    """,
    unsafe_allow_html=True,
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
    submitted = st.form_submit_button("Consultar", type="primary", width="stretch")

st.markdown(
    '<p class="privacy-note">🔒 El número se utiliza únicamente para realizar esta consulta.</p>',
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
                  <p class="suggestion-label">Sugerencia para enriquecer el trabajo</p>
                  <p>{suggestion}</p>
                </section>
                """,
                unsafe_allow_html=True,
            )

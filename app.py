import streamlit as st

from src.providers.config import load_environment
from src.streamlit_app.pages.logic import render_logic_page
from src.streamlit_app.pages.study import render_study_page


def configure_app() -> None:
    load_environment()

    st.set_page_config(
        page_title="PDF Study Assistant",
        page_icon="\U0001F4DA",
        layout="wide",
    )

    st.markdown(
        """
        <style>
        .block-container {
            max-width: 920px;
            padding-top: 2rem;
        }
        textarea {
            font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_navigation():
    return st.navigation(
        [
            st.Page(
                render_study_page,
                title="Study",
                icon="\U0001F4DA",
                url_path="study",
                default=True,
            ),
            st.Page(
                render_logic_page,
                title="RAG logic",
                icon="\U0001F50E",
                url_path="logic",
            ),
        ]
    )


configure_app()
build_navigation().run()

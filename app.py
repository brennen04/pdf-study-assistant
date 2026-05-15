import streamlit as st

from src.chunker import chunk_text
from src.embedding_client import embed_texts
from src.pdf_loader import extract_text_from_pdf


st.set_page_config(
    page_title="PDF Study Assistant",
    page_icon="\U0001F4DA",
    layout="wide"
)

st.title("\U0001F4DA PDF Study Assistant")

st.write(
    "Upload a lecture note PDF and extract its text. "
    "Later, this app will let you ask questions grounded in the PDF."
)

uploaded_file = st.file_uploader(
    "Upload a PDF",
    type=["pdf"]
)

if uploaded_file is not None:
    st.success(f"Uploaded: {uploaded_file.name}")

    with st.spinner("Extracting text from PDF..."):
        extracted_text = extract_text_from_pdf(uploaded_file)

    st.subheader("Extracted Text Preview")

    if extracted_text.strip():
        chunks = chunk_text(extracted_text)

        st.text_area(
            "PDF text",
            extracted_text[:5000],
            height=400
        )

        st.info(f"Extracted approximately {len(extracted_text):,} characters.")

        st.subheader("Chunk Preview")
        st.write(f"Created {len(chunks):,} text chunks.")

        st.text_area(
            "First chunk",
            chunks[0],
            height=250
        )

        with st.spinner("Generating embeddings for chunks..."):
            embeddings = embed_texts(chunks)

        if embeddings:
            st.subheader("Embedding Summary")
            st.write(f"Generated {len(embeddings):,} embeddings.")
            st.write(f"Each embedding has {len(embeddings[0]):,} dimensions.")

            st.text_area(
                "First embedding preview",
                str(embeddings[0][:10]),
                height=120
            )
    else:
        st.warning(
            "No text could be extracted. This PDF may be scanned or image-based."
        )

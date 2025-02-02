import os
import fitz  # PyMuPDF
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image


def generate_thumbnail(pdf_path, page_number):
    """Generate a thumbnail for a specific page using PyMuPDF."""
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    pix = page.get_pixmap(dpi=100)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img


def remove_pages_from_pdf(pdf_path, pages_to_remove, output_path):
    """Remove selected pages from the PDF."""
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page_number, page in enumerate(reader.pages):
        if page_number not in pages_to_remove:
            writer.add_page(page)

    with open(output_path, "wb") as output_file:
        writer.write(output_file)

# SEO-оптимизация
st.markdown(
    """
    <head>
        <title>PDF Slicer - Easily Remove Pages from PDFs</title>
        <meta name="description" content="PDF Slicer: A simple tool to remove pages from PDF files. Upload, select pages, and download the edited file.">
        <meta name="keywords" content="PDF, remove pages, edit PDF, PDF tool, Streamlit">
        <meta name="author" content="Kamil">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta property="og:title" content="PDF Slicer - Easily Remove Pages from PDFs">
        <meta property="og:description" content="Quickly and easily remove pages from your PDF files. Fast, secure, and free!">
        <meta property="og:image" content="https://pdfslicer.streamlit.app/static/og-preview.png">
        <meta property="og:url" content="https://pdfslicer.streamlit.app/">
        <meta property="og:type" content="website">
        <link rel="icon" href="https://pdfslicer.streamlit.app/static/favicon.ico" type="image/x-icon">
        <link rel="canonical" href="https://pdfslicer.streamlit.app/">
    </head>
    """,
    unsafe_allow_html=True
)

# Google Search Console verification
st.markdown(
    """
    <div style="display: none;">
        <meta name="google-site-verification" content="aAyfkeeM2Px0gDxLIQIOGAR72U0S5Dvjljl8t0MbS-4" />
    </div>
    """,
    unsafe_allow_html=True
)


# Заголовок приложения
st.title("PDF Page Remover")

# Функционал загрузки PDF-файлов
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    pdf_path = os.path.join("temp", uploaded_file.name)
    if not os.path.exists("temp"):
        os.makedirs("temp")

    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    st.sidebar.header("Navigation")
    current_page = st.sidebar.number_input(
        "Go to page",
        min_value=1,
        max_value=total_pages,
        step=1,
        value=1
    )

    # Генерация и отображение миниатюры страницы
    st.write(f"**Page {current_page} of {total_pages}**")
    image = generate_thumbnail(pdf_path, current_page - 1)
    st.image(image, caption=f"Page {current_page}", use_container_width=True)

    st.sidebar.header("Page Selection")
    page_input = st.sidebar.text_input("Enter pages to remove (e.g., 2-3,5):")


    def parse_page_input(page_input, total_pages):
        """Parse a string input for page ranges."""
        pages = set()
        try:
            for part in page_input.split(","):
                if "-" in part:
                    start, end = map(int, part.split("-"))
                    pages.update(range(start, end + 1))
                else:
                    pages.add(int(part))
            return sorted([p - 1 for p in pages if 1 <= p <= total_pages])
        except ValueError:
            st.sidebar.error("Invalid page input format.")
            return []


    pages_to_remove = parse_page_input(page_input, total_pages)

    if st.button("Remove Selected Pages"):
        if not pages_to_remove:
            st.warning("No pages selected for removal.")
        else:
            output_path = os.path.join("temp", f"edited_{uploaded_file.name}")
            remove_pages_from_pdf(pdf_path, pages_to_remove, output_path)

            with open(output_path, "rb") as f:
                st.download_button(
                    label="Download Edited PDF",
                    data=f,
                    file_name=f"edited_{uploaded_file.name}",
                    mime="application/pdf"
                )

            st.success("Edited PDF is ready to download.")

import os
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path


def generate_page_preview(pdf_path, page_number, output_dir="previews"):
    """Generate a preview image for a specific page of a PDF."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    page_image = convert_from_path(pdf_path, first_page=page_number + 1, last_page=page_number + 1, dpi=100)[0]
    preview_path = os.path.join(output_dir, f"page_{page_number}.png")
    page_image.save(preview_path, "PNG")
    return preview_path


def remove_pages_from_pdf(pdf_path, pages_to_remove, output_path):
    """Remove the selected pages from the PDF and save the new file."""
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page_number, page in enumerate(reader.pages):
        if page_number not in pages_to_remove:
            writer.add_page(page)

    with open(output_path, "wb") as output_file:
        writer.write(output_file)


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
        # Convert to zero-based indexing
        return sorted([p - 1 for p in pages if 1 <= p <= total_pages])
    except ValueError:
        st.sidebar.error("Invalid page input format.")
        return []


st.title("PDF Page Remover")
st.markdown("Upload a PDF file, select pages to remove, and download the result.")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    # Save the uploaded file
    pdf_path = os.path.join("temp", uploaded_file.name)
    if not os.path.exists("temp"):
        os.makedirs("temp")

    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    # Page navigation and preview
    st.sidebar.header("Navigation")
    current_page = st.sidebar.number_input(
        "Go to page",
        min_value=1,
        max_value=total_pages,
        step=1,
        value=1,
        format="%d"
    )
    preview_path = generate_page_preview(pdf_path, current_page - 1)
    st.image(preview_path, caption=f"Page {current_page}", use_container_width=True)

    # Page selection for removal
    st.sidebar.header("Page Selection")
    page_input = st.sidebar.text_input(
        "Enter pages to remove (e.g., 2-3,5):"
    )
    pages_to_remove = parse_page_input(page_input, total_pages)

    if st.sidebar.button("Show Selected Pages"):
        st.sidebar.write(f"Selected pages for removal: {', '.join(map(str, [p + 1 for p in pages_to_remove]))}")

    # Remove pages
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

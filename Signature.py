import os
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def add_image_to_pdf(input_pdf, output_pdf, image_path):
    """
    Ajoute une image en bas à droite de la première page d'un PDF.

    Args:
        input_pdf (str): Chemin du fichier PDF d'entrée.
        output_pdf (str): Chemin du fichier PDF de sortie.
        image_path (str): Chemin de l'image à insérer.
    """
    temp_pdf = "temp.pdf"

    # Crée un PDF temporaire avec l'image
    c = canvas.Canvas(temp_pdf, pagesize=letter)
    width, height = letter
    c.drawImage(image_path, width - 250, height - 150, width=200, preserveAspectRatio=True, mask='auto')
    c.save()

    # Fusionne le PDF temporaire avec l'original
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Ajoute l'image uniquement à la première page
    page = reader.pages[0]
    with open(temp_pdf, "rb") as temp_file:
        temp_reader = PdfReader(temp_file)
        overlay_page = temp_reader.pages[0]
        page.merge_page(overlay_page)
        writer.add_page(page)

    # Ajoute les pages restantes
    for i in range(1, len(reader.pages)):
        writer.add_page(reader.pages[i])

    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

    # Supprime le fichier temporaire
    os.remove(temp_pdf)

def search_and_sign_documents(pdf_directory, keyword, image_path):
    """
    Parcourt tous les fichiers PDF d'un répertoire, ajoute une signature (image) si le fichier contient un mot-clé.

    Args:
        pdf_directory (str): Chemin du répertoire contenant les fichiers PDF.
        keyword (str): Mot-clé à rechercher dans les fichiers.
        image_path (str): Chemin de l'image à insérer.
    """
    modified_files = []
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_directory, filename)
            output_path = file_path.replace(".pdf", "_signed.pdf")
            if search_and_add_signature(file_path, output_path, keyword, image_path):
                modified_files.append(filename)
    return modified_files

def search_and_add_signature(input_pdf, output_pdf, keyword, image_path):
    """
    Ajoute une signature (image) à un PDF si le fichier contient un mot-clé.

    Args:
        input_pdf (str): Chemin du fichier PDF d'entrée.
        output_pdf (str): Chemin du fichier PDF de sortie.
        keyword (str): Mot-clé à rechercher dans le fichier.
        image_path (str): Chemin de l'image à insérer.

    Returns:
        bool: True si le fichier a été modifié, False sinon.
    """
    reader = PdfReader(input_pdf)
    content = "".join([page.extract_text() for page in reader.pages])
    if keyword in content:
        add_image_to_pdf(input_pdf, output_pdf, image_path)
        return True
    return False

# Interface utilisateur Streamlit
st.title("Outil de signature automatique des documents PDF")

uploaded_pdf_directory = st.file_uploader("Téléchargez le dossier contenant les fichiers PDF", type="directory")
search_keyword = st.text_input("Entrez le mot-clé à rechercher")
signature_image = st.file_uploader("Téléchargez une image de signature", type=["png", "jpg", "jpeg"])

if st.button("Lancer la signature"):
    if uploaded_pdf_directory and search_keyword and signature_image:
        # Sauvegarde de l'image de signature temporairement
        image_path = f"temp_{signature_image.name}"
        with open(image_path, "wb") as f:
            f.write(signature_image.read())

        with st.spinner("Traitement en cours..."):
            modified_files = search_and_sign_documents(uploaded_pdf_directory, search_keyword, image_path)

        if modified_files:
            st.success(f"Les fichiers suivants ont été signés avec succès :")
            for filename in modified_files:
                st.info(filename)
        else:
            st.warning("Aucun fichier n'a été modifié.")

        # Nettoyage du fichier temporaire
        os.remove(image_path)
    else:
        st.error("Veuillez fournir un répertoire, un mot-clé et une image de signature.")

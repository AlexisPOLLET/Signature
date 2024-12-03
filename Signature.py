import os
import zipfile
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pdf2image import convert_from_path
import pytesseract

def add_image_to_pdf(input_pdf, output_pdf, image_path):
    """
    Ajoute une image en bas à droite de chaque page d'un PDF, en petite taille et avec transparence.

    Args:
        input_pdf (str): Chemin du fichier PDF d'entrée.
        output_pdf (str): Chemin du fichier PDF de sortie.
        image_path (str): Chemin de l'image à insérer.
    """
    temp_pdf = "temp_page.pdf"

    # Crée un PDF temporaire avec l'image sur chaque page
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        # Crée une page temporaire avec la signature
        c = canvas.Canvas(temp_pdf, pagesize=letter)
        width, height = letter

        # Réduction de la taille et positionnement en bas à droite
        image_width = 150
        image_height = 100
        x_position = width - image_width - 10
        y_position = 150

        # Transparence (créée via une multiplication de l'opacité sur le PDF complet)
        c.setFillAlpha(0.5)

        c.drawImage(image_path, x_position, y_position, width=image_width, height=image_height, preserveAspectRatio=True, mask='auto')
        c.save()

        # Fusionne la page temporaire avec la page actuelle
        with open(temp_pdf, "rb") as temp_file:
            temp_reader = PdfReader(temp_file)
            overlay_page = temp_reader.pages[0]
            page.merge_page(overlay_page)
            writer.add_page(page)

    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

    # Supprime le fichier temporaire
    os.remove(temp_pdf)

def extract_text_from_pdf(input_pdf):
    """
    Extrait le texte d'un fichier PDF, y compris via OCR pour les pages scannées.

    Args:
        input_pdf (str): Chemin du fichier PDF.

    Returns:
        str: Texte extrait du PDF.
    """
    text = ""
    reader = PdfReader(input_pdf)

    for page_num, page in enumerate(reader.pages):
        # Extraire le texte de la page
        page_text = page.extract_text()
        if page_text.strip():
            text += page_text
        else:
            # Effectuer l'OCR sur la page si aucun texte n'est trouvé
            images = convert_from_path(input_pdf, first_page=page_num + 1, last_page=page_num + 1)
            for image in images:
                text += pytesseract.image_to_string(image)

    return text

def process_files_and_sign_documents(uploaded_files, keyword, image_path):
    """
    Traite les fichiers PDF ou les archives ZIP téléversées et ajoute une signature (image) à ceux qui contiennent un mot-clé.

    Args:
        uploaded_files (list): Liste des fichiers téléversés (PDF ou ZIP).
        keyword (str): Mot-clé à rechercher dans les fichiers.
        image_path (str): Chemin de l'image à insérer.

    Returns:
        list: Liste des fichiers modifiés.
    """
    modified_files = []
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        temp_path = f"temp_{file_name}"

        # Sauvegarde temporaire
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())

        if file_name.endswith(".zip"):
            # Traiter l'archive ZIP
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                extract_dir = f"temp_extracted_{file_name}"
                zip_ref.extractall(extract_dir)

                for root, _, files in os.walk(extract_dir):
                    for file in files:
                        if file.endswith(".pdf"):
                            pdf_path = os.path.join(root, file)
                            output_path = pdf_path.replace(".pdf", "_signed.pdf")
                            if search_and_add_signature(pdf_path, output_path, keyword, image_path):
                                modified_files.append(output_path)

        elif file_name.endswith(".pdf"):
            # Traiter les fichiers PDF individuels
            output_path = temp_path.replace(".pdf", "_signed.pdf")
            if search_and_add_signature(temp_path, output_path, keyword, image_path):
                modified_files.append(output_path)

        # Supprime le fichier temporaire
        os.remove(temp_path)

    return modified_files

def search_and_add_signature(input_pdf, output_pdf, keyword, image_path):
    """
    Ajoute une signature (image) à chaque page d'un PDF si le fichier contient un mot-clé.

    Args:
        input_pdf (str): Chemin du fichier PDF d'entrée.
        output_pdf (str): Chemin du fichier PDF de sortie.
        keyword (str): Mot-clé à rechercher dans le fichier.
        image_path (str): Chemin de l'image à insérer.

    Returns:
        bool: True si le fichier a été modifié, False sinon.
    """
    text = extract_text_from_pdf(input_pdf)
    if keyword in text:
        add_image_to_pdf(input_pdf, output_pdf, image_path)
        return True
    return False

# Interface utilisateur Streamlit
st.title("Outil de signature automatique des documents PDF")

st.write("**Instructions :** Vous pouvez téléverser plusieurs fichiers PDF ou une archive ZIP contenant des fichiers PDF.")
st.code("pip install PyPDF2 reportlab pdf2image pytesseract streamlit")

uploaded_files = st.file_uploader("Téléchargez des fichiers ZIP ou PDF", type=["zip", "pdf"], accept_multiple_files=True)
search_keyword = st.text_input("Entrez le mot-clé à rechercher")
signature_image = st.file_uploader("Téléchargez une image de signature", type=["png", "jpg", "jpeg"])

if st.button("Lancer la signature"):
    if uploaded_files and search_keyword and signature_image:
        # Sauvegarde de l'image temporairement
        image_path = f"temp_{signature_image.name}"
        with open(image_path, "wb") as f:
            f.write(signature_image.read())

        modified_files = []

        with st.spinner("Traitement en cours..."):
            modified_files = process_files_and_sign_documents(uploaded_files, search_keyword, image_path)

        if modified_files:
            st.success(f"Les fichiers suivants ont été signés avec succès :")
            for file_path in modified_files:
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"Télécharger {os.path.basename(file_path)}",
                        data=f,
                        file_name=os.path.basename(file_path),
                        mime="application/pdf"
                    )
        else:
            st.warning("Aucun fichier n'a été modifié.")

        # Nettoyage du fichier temporaire
        os.remove(image_path)
        for file_path in modified_files:
            os.remove(file_path)
    else:
        st.error("Veuillez fournir des fichiers ZIP ou PDF, un mot-clé et une image de signature.")

# Gestion des erreurs pour les bibliothèques manquantes
try:
    import PyPDF2
    from reportlab.pdfgen import canvas
    from pdf2image import convert_from_path
    import pytesseract
except ImportError as e:
    st.error(f"Erreur d'importation des bibliothèques : {str(e)}. Veuillez installer les dépendances indiquées ci-dessus.")


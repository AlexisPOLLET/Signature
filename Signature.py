import os
import zipfile
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
from io import BytesIO
import fitz  # PyMuPDF

def add_image_to_pdf_with_text(input_pdf, output_pdf, image_path, position="bottom-right"):
    """
    Ajoute une image en bas de chaque page d'un PDF contenant du texte.

    Args:
        input_pdf (str): Chemin du fichier PDF d'entrée.
        output_pdf (str): Chemin du fichier PDF de sortie.
        image_path (str): Chemin de l'image à insérer.
        position (str): Position de la signature ("bottom-right" ou "bottom-left").
    """
    pdf_document = fitz.open(input_pdf)
    image = Image.open(image_path).convert("RGBA")
    alpha = 128  # Transparence

   # Appliquer une rotation de 90 degrés
    rotated_image = image.rotate(90, expand=True)
    transparent_image = Image.new("RGBA", rotated_image.size, (255, 255, 255, 0))
    for x in range(rotated_image.width):
        for y in range(rotated_image.height):
            r, g, b, a = rotated_image.getpixel((x, y))
            transparent_image.putpixel((x, y), (r, g, b, int(a * (alpha / 255.0))))
    temp_image_path = "temp_transparent_image.png"
    transparent_image.save(temp_image_path, "PNG")

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]

        # Définir la position de la signature pour les PDF avec texte
        width, height = page.rect.width, page.rect.height
        image_width = 150
        image_height = 75

        if position == "bottom-right":
            x_position = width - image_width - 50
            y_position = height - image_height - 150
        elif position == "bottom-left":
            x_position = 50
            y_position = height - image_height - 150
        else:
            raise ValueError("Position non prise en charge. Utilisez 'bottom-right' ou 'bottom-left'.")

        # Ajouter l'image sur la page
        page.insert_image(
            fitz.Rect(x_position, y_position, x_position + image_width, y_position + image_height),
            filename=temp_image_path
        )

    pdf_document.save(output_pdf)
    pdf_document.close()

    # Supprimer l'image temporaire
    os.remove(temp_image_path)

def add_image_to_pdf_with_images(input_pdf, output_pdf, image_path, position="bottom-right"):
    """
    Ajoute une image en bas de chaque page d'un PDF contenant uniquement des images.

    Args:
        input_pdf (str): Chemin du fichier PDF d'entrée.
        output_pdf (str): Chemin du fichier PDF de sortie.
        image_path (str): Chemin de l'image à insérer.
        position (str): Position de la signature ("bottom-right" ou "bottom-left").
    """
    pdf_document = fitz.open(input_pdf)
    image = Image.open(image_path).convert("RGBA")
    alpha = 128  # Transparence

    transparent_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
    for x in range(image.width):
        for y in range(image.height):
            r, g, b, a = image.getpixel((x, y))
            transparent_image.putpixel((x, y), (r, g, b, int(a * (alpha / 255.0))))
    temp_image_path = "temp_transparent_image.png"
    transparent_image.save(temp_image_path, "PNG")

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]

        # Définir la position de la signature pour les PDF avec images uniquement
        width, height = page.rect.width, page.rect.height
        image_width = 150
        image_height = 75

        if position == "bottom-right":
            x_position = width - image_width - 200
            y_position = 50
        elif position == "bottom-left":
            x_position = 200
            y_position = 50
        else:
            raise ValueError("Position non prise en charge. Utilisez 'bottom-right' ou 'bottom-left'.")

        # Ajouter l'image sur la page
        page.insert_image(
            fitz.Rect(x_position, y_position, x_position + image_width, y_position + image_height),
            filename=temp_image_path
        )

    pdf_document.save(output_pdf)
    pdf_document.close()

    # Supprimer l'image temporaire
    os.remove(temp_image_path)

def extract_text_from_pdf(input_pdf):
    """
    Extrait le texte d'un fichier PDF.

    Args:
        input_pdf (str): Chemin du fichier PDF.

    Returns:
        str: Texte extrait du PDF.
    """
    text = ""

    # Tenter d'extraire le texte directement
    reader = PdfReader(input_pdf)
    for page in reader.pages:
        text += page.extract_text()

    return text

def process_files_and_sign_documents(uploaded_files, keyword, image_path, position, include_images):
    """
    Traite les fichiers PDF ou les archives ZIP téléversées et ajoute une signature (image) à ceux qui contiennent un mot-clé ou aux fichiers sans texte détectable.

    Args:
        uploaded_files (list): Liste des fichiers téléversés (PDF ou ZIP).
        keyword (str): Mot-clé à rechercher dans les fichiers.
        image_path (str): Chemin de l'image à insérer.
        position (str): Position de la signature ("bottom-right" ou "bottom-left").
        include_images (bool): Inclure les fichiers avec uniquement des images.

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
                            if search_and_add_signature(pdf_path, output_path, keyword, image_path, position, include_images):
                                modified_files.append(output_path)

        elif file_name.endswith(".pdf"):
            # Traiter les fichiers PDF individuels
            output_path = temp_path.replace(".pdf", "_signed.pdf")
            if search_and_add_signature(temp_path, output_path, keyword, image_path, position, include_images):
                modified_files.append(output_path)

        # Supprime le fichier temporaire
        os.remove(temp_path)

    return modified_files

def search_and_add_signature(input_pdf, output_pdf, keyword, image_path, position, include_images):
    """
    Ajoute une signature (image) à chaque page d'un PDF, même si aucun texte n'est détectable.

    Args:
        input_pdf (str): Chemin du fichier PDF d'entrée.
        output_pdf (str): Chemin du fichier PDF de sortie.
        keyword (str): Mot-clé à rechercher dans le fichier.
        image_path (str): Chemin de l'image à insérer.
        position (str): Position de la signature ("bottom-right" ou "bottom-left").
        include_images (bool): Inclure les fichiers avec uniquement des images.

    Returns:
        bool: True si le fichier a été modifié, False sinon.
    """
    # Réinitialiser le fichier de sortie s'il existe déjà
    if os.path.exists(output_pdf):
        os.remove(output_pdf)

    text = extract_text_from_pdf(input_pdf)

    # Ajouter la signature si le mot-clé est présent ou si le PDF contient uniquement des images
    if keyword in text:
        add_image_to_pdf_with_text(input_pdf, output_pdf, image_path, position)
        return True
    elif include_images and not text.strip():
        add_image_to_pdf_with_images(input_pdf, output_pdf, image_path, position)
        return True

    return False

# Interface utilisateur Streamlit
st.title("Outil de signature automatique des documents PDF")

st.write("**Instructions :** Vous pouvez téléverser plusieurs fichiers PDF ou une archive ZIP contenant des fichiers PDF.")
st.code("pip install PyPDF2 reportlab streamlit pillow pymupdf")

uploaded_files = st.file_uploader("Téléchargez des fichiers ZIP ou PDF", type=["zip", "pdf"], accept_multiple_files=True)
search_keyword = st.text_input("Entrez le mot-clé à rechercher")
signature_image = st.file_uploader("Téléchargez une image de signature", type=["png", "jpg", "jpeg"])
position = st.radio("Choisissez la position de la signature :", ["bottom-right", "bottom-left"])
include_images = st.checkbox("Signer les fichiers contenant uniquement des images")

if st.button("Lancer la signature"):
    if uploaded_files and signature_image:
        # Sauvegarde de l'image temporairement
        image_path = f"temp_{signature_image.name}"
        with open(image_path, "wb") as f:
            f.write(signature_image.read())

        modified_files = []

        with st.spinner("Traitement en cours..."):
            modified_files = process_files_and_sign_documents(uploaded_files, search_keyword, image_path, position, include_images)

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

            # Ajouter un bouton pour télécharger tous les fichiers signés en une seule archive ZIP
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for file_path in modified_files:
                    zip_file.write(file_path, os.path.basename(file_path))
            zip_buffer.seek(0)

            st.download_button(
                label="Télécharger tous les fichiers signés (ZIP)",
                data=zip_buffer,
                file_name="fichiers_signes.zip",
                mime="application/zip"
            )
        else:
            st.warning("Aucun fichier n'a été modifié.")

        # Nettoyage des fichiers temporaires
        os.remove(image_path)
        for file_path in modified_files:
            os.remove(file_path)
    else:
        st.error("Veuillez fournir des fichiers ZIP ou PDF et une image de signature.")

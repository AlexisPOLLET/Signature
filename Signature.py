import os
import zipfile
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def add_image_to_pdf(input_pdf, output_pdf, image_path):
    """
    Ajoute une image en bas de la première page d'un PDF.

    Args:
        input_pdf (str): Chemin du fichier PDF d'entrée.
        output_pdf (str): Chemin du fichier PDF de sortie.
        image_path (str): Chemin de l'image à insérer.
    """
    temp_pdf = "temp.pdf"

    # Crée un PDF temporaire avec l'image
    c = canvas.Canvas(temp_pdf, pagesize=letter)
    width, height = letter
    c.drawImage(image_path, 50, 50, width=200, preserveAspectRatio=True, mask='auto')
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

def process_zip_and_sign_documents(zip_path, keyword, image_path):
    """
    Traite un fichier ZIP contenant des fichiers PDF et ajoute une signature (image) à ceux qui contiennent un mot-clé.

    Args:
        zip_path (str): Chemin de l'archive ZIP.
        keyword (str): Mot-clé à rechercher dans les fichiers.
        image_path (str): Chemin de l'image à insérer.

    Returns:
        list: Liste des fichiers modifiés.
    """
    modified_files = []
    extract_dir = "temp_extracted"

    # Extraire le contenu du ZIP
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    # Parcourir les fichiers extraits
    for root, _, files in os.walk(extract_dir):
        for file in files:
            if file.endswith(".pdf"):
                file_path = os.path.join(root, file)
                output_path = file_path.replace(".pdf", "_signed.pdf")
                if search_and_add_signature(file_path, output_path, keyword, image_path):
                    modified_files.append(output_path)

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

st.write("**Instructions :** Vous pouvez téléverser un fichier ZIP contenant des fichiers PDF ou un fichier PDF unique.")
st.code("pip install PyPDF2 reportlab streamlit")

uploaded_file = st.file_uploader("Téléchargez un fichier ZIP ou PDF", type=["zip", "pdf"])
search_keyword = st.text_input("Entrez le mot-clé à rechercher")
signature_image = st.file_uploader("Téléchargez une image de signature", type=["png", "jpg", "jpeg"])

if st.button("Lancer la signature"):
    if uploaded_file and search_keyword and signature_image:
        # Sauvegarde des fichiers temporairement
        input_path = f"temp_{uploaded_file.name}"
        image_path = f"temp_{signature_image.name}"

        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        with open(image_path, "wb") as f:
            f.write(signature_image.read())

        modified_files = []

        with st.spinner("Traitement en cours..."):
            if uploaded_file.name.endswith(".zip"):
                modified_files = process_zip_and_sign_documents(input_path, search_keyword, image_path)
            elif uploaded_file.name.endswith(".pdf"):
                output_path = input_path.replace(".pdf", "_signed.pdf")
                if search_and_add_signature(input_path, output_path, search_keyword, image_path):
                    modified_files.append(output_path)

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

        # Nettoyage des fichiers temporaires
        os.remove(input_path)
        os.remove(image_path)
        for file_path in modified_files:
            os.remove(file_path)
    else:
        st.error("Veuillez fournir un fichier ZIP ou PDF, un mot-clé et une image de signature.")

# Gestion des erreurs pour les bibliothèques manquantes
try:
    import PyPDF2
    from reportlab.pdfgen import canvas
except ImportError as e:
    st.error(f"Erreur d'importation des bibliothèques : {str(e)}. Veuillez installer les dépendances indiquées ci-dessus.")
    

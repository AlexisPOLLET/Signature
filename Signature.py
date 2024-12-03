import os
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

def search_and_sign_documents(file, keyword, image_path):
    """
    Ajoute une signature (image) à un PDF si le fichier contient un mot-clé.

    Args:
        file (str): Chemin du fichier PDF.
        keyword (str): Mot-clé à rechercher dans le fichier.
        image_path (str): Chemin de l'image à insérer.

    Returns:
        str: Chemin du fichier modifié ou None si aucune modification n'est effectuée.
    """
    reader = PdfReader(file)
    content = "".join([page.extract_text() for page in reader.pages])

    if keyword in content:
        output_path = file.replace(".pdf", "_signed.pdf")
        add_image_to_pdf(file, output_path, image_path)
        return output_path

    return None

# Interface utilisateur Streamlit
st.title("Outil de signature automatique des documents PDF")

st.write("**Instructions :** Assurez-vous que les dépendances suivantes sont installées avant de lancer ce script :")
st.code("pip install PyPDF2 reportlab streamlit")

uploaded_file = st.file_uploader("Téléchargez un fichier PDF", type="pdf")
search_keyword = st.text_input("Entrez le mot-clé à rechercher")
signature_image = st.file_uploader("Téléchargez une image de signature", type=["png", "jpg", "jpeg"])

if st.button("Lancer la signature"):
    if uploaded_file and search_keyword and signature_image:
        # Sauvegarde des fichiers temporairement
        input_pdf_path = f"temp_{uploaded_file.name}"
        image_path = f"temp_{signature_image.name}"

        with open(input_pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        with open(image_path, "wb") as f:
            f.write(signature_image.read())

        with st.spinner("Traitement en cours..."):
            result = search_and_sign_documents(input_pdf_path, search_keyword, image_path)

        if result:
            with open(result, "rb") as f:
                st.download_button(
                    label="Télécharger le fichier signé",
                    data=f,
                    file_name=os.path.basename(result),
                    mime="application/pdf"
                )
            st.success("Fichier signé avec succès !")
        else:
            st.warning("Aucun mot-clé trouvé dans le document. Pas de signature ajoutée.")

        # Nettoyage des fichiers temporaires
        os.remove(input_pdf_path)
        os.remove(image_path)
        if result:
            os.remove(result)
    else:
        st.error("Veuillez fournir un fichier PDF, un mot-clé et une image de signature.")

# Gestion des erreurs pour les bibliothèques manquantes
try:
    import PyPDF2
    from reportlab.pdfgen import canvas
except ImportError as e:
    st.error(f"Erreur d'importation des bibliothèques : {str(e)}. Veuillez installer les dépendances indiquées ci-dessus.")

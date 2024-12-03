import os
import streamlit as st

def select_and_sign_files(directory, search_word, signature):
    """
    Sélectionne les fichiers contenant un mot spécifique et sans signature,
    puis ajoute automatiquement la signature.

    :param directory: Chemin du répertoire à parcourir
    :param search_word: Mot à rechercher dans les fichiers
    :param signature: Signature à ajouter aux fichiers
    :return: Liste des fichiers modifiés
    """
    modified_files = []
    
    # Vérifier que le répertoire existe
    if not os.path.exists(directory):
        st.error(f"Le répertoire {directory} n'existe pas!")
        return modified_files

    # Parcourir tous les fichiers du répertoire
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        # Vérifier si c'est un fichier
        if os.path.isfile(filepath):
            try:
                # Lire le contenu du fichier
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Vérifier si le mot recherché est dans le fichier
                if search_word in content:
                    # Vérifier si la signature n'est pas déjà présente
                    if signature not in content:
                        # Ajouter la signature à la fin du fichier
                        with open(filepath, 'a', encoding='utf-8') as file:
                            file.write('\n' + signature)
                        
                        modified_files.append(filename)
            
            except Exception as e:
                st.error(f"Erreur lors du traitement du fichier {filename}: {e}")

    return modified_files

def main():
    st.title("🖊️ Signature Automatique de Fichiers")
    
    # Entrées utilisateur
    directory = st.text_input("Chemin du répertoire", placeholder="/chemin/vers/votre/repertoire")
    search_word = st.text_input("Mot à rechercher", placeholder="exemple")
    signature = st.text_area("Signature à ajouter", placeholder="--- Signé automatiquement ---")
    
    # Bouton de traitement
    if st.button("Ajouter les Signatures"):
        if directory and search_word and signature:
            # Vérifier que le répertoire existe
            if os.path.exists(directory):
                # Exécuter la fonction de signature
                modified_files = select_and_sign_files(directory, search_word, signature)
                
                # Afficher les résultats
                if modified_files:
                    st.success(f"{len(modified_files)} fichiers ont été modifiés :")
                    for file in modified_files:
                        st.info(file)
                else:
                    st.warning("Aucun fichier n'a été modifié.")
            else:
                st.error("Le répertoire spécifié n'existe pas.")
        else:
            st.warning("Veuillez remplir tous les champs.")

# Configuration de la page Streamlit
st.set_page_config(page_title="Signature de Fichiers", page_icon="🖊️")

# Exécution de l'application
if __name__ == "__main__":
    main()

import os
import re

def select_and_sign_files(directory, search_word, signature):
    """
    Sélectionne les fichiers contenant un mot spécifique et sans signature,
    puis ajoute automatiquement la signature.

    :param directory: Chemin du répertoire à parcourir
    :param search_word: Mot à rechercher dans les fichiers
    :param signature: Signature à ajouter aux fichiers
    """
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
                        
                        print(f"Signature ajoutée au fichier : {filename}")
            
            except Exception as e:
                print(f"Erreur lors du traitement du fichier {filename}: {e}")

# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration
    repertoire = "/chemin/vers/votre/repertoire"  # Remplacez par le chemin de votre répertoire
    mot_recherche = "exemple"  # Le mot à rechercher
    signature = "--- Signé par mon script Python ---"  # Votre signature

    # Appel de la fonction
    select_and_sign_files(repertoire, mot_recherche, signature)

import csv
import os
from concurrent.futures.thread import ThreadPoolExecutor

import requests
import argparse
from urllib.request import urlretrieve

OPEN_FOOD_FACTS_API_BASE_URL="https://world.openfoodfacts.org"
SEARCH_API="/api/v2/search"


def downlaod_product_image(image_url: str, img_dest: str):
    urlretrieve(image_url, img_dest)

def get_products(output_dir: str):
    query_params = {
        'search_terms': 'champagne',
        'page_size': 10,
        'fields': 'code,product_name,categories,ingredients_text,image_url,'
    }

    response = requests.get(
        f"{OPEN_FOOD_FACTS_API_BASE_URL}/{SEARCH_API}",
        params=query_params
    )

    if response.status_code == 200:
        products = response.json().get('products', [])
        images = []
        # Ouvrir le fichier CSV en mode écriture
        with open(f"{output_dir}/produits_champagne.csv", mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Écrire l'en-tête du CSV
            writer.writerow(['foodId', 'label', 'category', 'foodContentsLabel', 'image'])

            # Parcourir les produits et écrire les informations dans le CSV

            for product in products:
                food_id = product.get('code', '')
                label = product.get('product_name', '')
                category = product.get('categories', '')
                food_contents_label = product.get('ingredients_text', '')
                image = product.get('image_url', '')
                writer.writerow([food_id, label, category, food_contents_label, image])
                if image != '':
                    images.append({'image_url': image, 'img_dest': f"{output_dir}/images/{food_id}.jpg" })

        #Telechargement des mages
        with ThreadPoolExecutor() as executor:
            executor.map(lambda img: downlaod_product_image(image_url=img['image_url'], img_dest=img['img_dest']), images)

        print(f"Extraction terminée. Les données ont été enregistrées dans '{output_dir}/produits_champagne.csv'.")
    else:
        print(f"Erreur lors de la requête à l'API. Statut : {response.status_code}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--o', help="Le dossier de destination", default="samples")

    args = parser.parse_args()
    output_dir = args.o

    # Création du dossier de destination s'il n'existe pas.
    os.makedirs(output_dir+'/images', exist_ok=True)

    get_products(output_dir=output_dir)

if __name__=="__main__":
    main()
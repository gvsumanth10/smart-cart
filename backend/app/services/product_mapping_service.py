from app.db.session import mongo_db
from app.utils.quantity_parser import normalize_quantity_to_grams
from typing import List, Dict, Tuple

def map_ingredients_to_products(ingredients: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """
    Maps a list of ingredients to the best-matching products from the MongoDB Catalogue, Prioritizing the nearest appropriate quantity."""

    products_collection = mongo_db.get_collection("raw_products")

    final_product_list = []
    not_found_ingredients = []

    for item in ingredients:
        ingredient_name = item.get("ingredient_name")
        required_quantity = item.get("quantity")
        main_cat_hints = item.get("main_category_hints",[])
        sub_cat_hints = item.get("sub_category_hints",[])
        synonyms = ' '.join(item.get('synonyms', []))
        search_term_hints = item.get("search_term_hints", [ingredient_name])

        if not ingredient_name:
            continue

        search_query = f'"{ingredient_name}" {synonyms}'

        print(f'---- Mapping ingredient: {ingredient_name} with required quantity: {required_quantity} ----')

        matching_products = []


        for search_term in search_term_hints:
            # Iterative search logic
            # First, try searching with category hints for high accuracy

            # 1. Iterative Search with Category Hints
            if main_cat_hints and sub_cat_hints:
                for main_cat in main_cat_hints:
                    for sub_cat in sub_cat_hints:
                        print(f"  -> Searching for '{search_term}' in: {main_cat} > {sub_cat}")
                        query = {
                            "$text": {"$search": search_term},
                            "main_category": main_cat,
                            "sub_category": sub_cat
                        }
                        results = list(products_collection.find(query))
                        if results:
                            matching_products = results
                            break
                    if matching_products:
                        break

            # 2. Fallback Broad Search (if category search fails for this term)
            if not matching_products:
                print(f"  -> No hint match for '{search_term}'. Trying broad search...")
                results = list(products_collection.find(
                    {"$text": {"$search": search_term}},
                    {'score': {'$meta': 'textScore'}}
                ).sort([('score', {'$meta': 'textScore'})]))
                if results:
                    matching_products = results
            
            # 3. If we found a match with THIS search term, we're done searching.
            if matching_products:
                print(f"  -> Found match using search term: '{search_term}'")
                break # IMPORTANT: This exits the outer 'for search_term in...' loop


        
        # --- After all search attempts, proceed with the results ---
        if not matching_products:
            print(f'-> No products found for ingredient: {ingredient_name}')
            not_found_ingredients.append(f'{ingredient_name} ({required_quantity})')
            continue

        # --- Quantity Matching Logic ---
        required_quantity = normalize_quantity_to_grams(required_quantity)
        best_match_product = None

        if required_quantity:
            req_value, req_unit = required_quantity
            print(f"  -> Normalized requirement: {req_value} {req_unit}")

            if req_unit == 'g':
                best_fit_products = []
                for prod in matching_products:
                    available_qty = normalize_quantity_to_grams(prod.get("quantity", ""))
                    if available_qty and available_qty[1] == 'g' and available_qty[0] >= req_value:
                        best_fit_products.append((prod, available_qty[0]))
                if best_fit_products:
                    best_fit_products.sort(key=lambda x: x[1])
                    best_match_product = best_fit_products[0][0]

            elif req_unit == 'pcs':
                all_available_products = []
                for prod in matching_products:
                    available_qty = normalize_quantity_to_grams(prod.get("quantity", ""))
                    if available_qty and available_qty[1] == 'g':
                        all_available_products.append((prod, available_qty[0]))
                if all_available_products:
                    all_available_products.sort(key=lambda x: x[1])
                    best_match_product = all_available_products[0][0]

        if not best_match_product:
            best_match_product = matching_products[0]

        print(f"  -> FINAL MAPPED PRODUCT: '{best_match_product['product_name']}'")
        final_product_list.append(best_match_product)
            
    return final_product_list, not_found_ingredients


    #     normalized_quantity = normalize_quantity_to_grams(required_quantity)
    #     best_match_product = None

    #     if normalized_quantity:
    #         req_value, req_unit = normalized_quantity
    #         print(f"-> Normalized requirement: {req_value} {req_unit}")

    #         # Logic for weight based items (g)
    #         if req_unit == 'g':
    #             best_fit_products = []
    #             for prod in matching_products:
    #                 available_qty = normalize_quantity_to_grams(prod.get("quantity",""))[0] if normalize_quantity_to_grams(prod.get("quantity", "")) else None

    #                 if available_qty and available_qty >= req_value:
    #                     best_fit_products.append((prod, available_qty))
                
    #             if best_fit_products:
    #                 best_fit_products.sort(key=lambda x:x[1])
    #                 best_match_product = best_fit_products[0][0]

    #         # Logic for piece based items (pcs)
    #         elif req_unit == 'pcs':
    #             # For items like nuts or onions, we just want the SMALLEST available pack
    #             all_available_products = []
    #             for prod in matching_products:
    #                 available_qty = normalized_quantity(prod.get("quantity",""))[0] if normalized_quantity(prod.get("quantity", "")) else None
                    
    #                 if available_qty:
    #                     all_available_products.append((prod, available_qty))
                
    #             if all_available_products:
    #                 # Sort by the smallest quantity, regardless of unit type, to find the smallest pack

    #                 all_available_products.sort(key=lambda x: x[1])
    #                 best_match_product = all_available_products[0][0]
        
    #     # Fallback: if no logic above found a match, pick the most relevant text search result
    #     if not best_match_product:
    #         best_match_product = matching_products[0]
        
    #     print(f" -> Mapped to: '{best_match_product['product_name']}")

    #     final_product_list.append(best_match_product)

    # return final_product_list, not_found_ingredients

    #     # 2. Normalize the required quantity to grams
    #     try:
    #         normalized_quantity = normalize_quantity_to_grams(required_quantity)
    #     except ValueError as e:
    #         print(f'-> Error normalizing quantity for {ingredient_name}: {e}')
    #         not_found_ingredients.append(f'{ingredient_name} ({required_quantity})')
    #         continue

    #     print(f'-> Normalized quantity for {ingredient_name}: {normalized_quantity} grams')

    #     best_match_product = None

    #     # 3. Find the best matching product based on quantity
    #     if normalized_quantity is not None:
    #         # Find the smallest product that meets or exceeds the required quantity
    #         best_fit_products = []
    #         for product in matching_products:
    #             available_quantity = normalize_quantity_to_grams(product.get('quantity', ''))
    #             if available_quantity and available_quantity >= normalized_quantity:
    #                 best_fit_products.append((product, available_quantity))

    #         # Sort by the smalled quantity that meets the requirement
    #         if best_fit_products:
    #             best_fit_products.sort(key=lambda x: x[1])
    #             best_match_product = best_fit_products[0][0]

    #     # 4. Fallback Logic: If no perfect fit, or if quantity is unit-based (eg. '1 pc') 
    #     if not best_match_product:
    #         # Pick the product with the closest quantity as default
    #         # This is useful for items like "1 Onion" where gram conversion is not feasible
    #         best_match_product = matching_products[0]  # Fallback to the first product if no quantities are found
    #     print(f"  -> Mapped to: '{best_match_product['product_name']}'")
    #     # Ensure the full, original document is always appended
    #     final_product_list.append(best_match_product)
    # return final_product_list, not_found_ingredients


            
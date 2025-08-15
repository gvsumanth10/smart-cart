import re
from typing import Tuple, Optional 

def normalize_quantity_to_grams(quantity_str: str)-> Optional[Tuple[float, str]]:
    """
    Parses a quantity string (e.g "1 cup", "200 grams", "2 tablespoons") and converts it to grams.
    Returns the quantity in grams as a float.
    """
    if not quantity_str or not isinstance(quantity_str, str):
        return None
    
    quantity_str = str(quantity_str).lower().strip()

    # Prioritize standard units (kg, g, l, ml) first
    
    priority_match = re.search(r'(\d+\.?\d*)\s*(kg|g|l|ml|litre)', quantity_str)
    if priority_match:
        value = float(priority_match.group(1))
        unit = priority_match.group(2)

        unit_out = 'g' #Standardize all to grams
        if unit == 'kg': 
            value *= 1000
        if unit == 'l' or unit == 'litre':
            value *= 1000
        # ml and g are treated as 1:1
        return value, unit_out 
    
    # Handle ranges like "15-20" by taking the second number
    range_match = re.search(r'\d+\.?\d*\s*-\s*(\d+\.?\d*)', quantity_str)
    if range_match:
        value = float(range_match.group(1))
    else:
        # Handle single numbers
        num_match = re.search(r'(\d+\.?\d*)', quantity_str)
        if not num_match:
            return None # Handles cases like "To taste"
        value = float(num_match.group(1))

    # Identify the non-priority units
    if any(unit in quantity_str for unit in ['pc', 'pcs', 'piece', 'pieces', 'cloves', 'seeds', 'nuts', 'nut', 'large', 'medium', 'small']):
        return value, 'pcs'
    
    if any(unit in quantity_str for unit in ['tbsp', 'tsp', 'cup', 'bunch']):
        unit_out = 'g' # Standardize all weights/volumes to grams for comparison  
        if 'tbsp' in quantity_str: 
            value *= 15
        if 'tsp' in quantity_str: 
            value *= 5
        if 'cup' in quantity_str: 
            value *= 240
        if 'bunch' in quantity_str: 
            value *= 100
        
        return value, unit_out

    return None # Return None if unit is not recognized

    

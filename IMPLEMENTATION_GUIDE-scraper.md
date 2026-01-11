# Implementation Guide: Daily Menu Feature for UCSB Dining Scraper

## Overview
This guide explains how to add support for scraping daily menus (Breakfast/Lunch/Dinner/Brunch)
from Portola, Carrillo, and De La Guerra dining commons, while keeping "Always Available" 
items separate.

## Changes Required

### 1. Add the parse_daily_menu_structure method (ALREADY DONE)

This method has been added to the scraper at line ~185. It:
- Looks for today's date in the HTML
- Finds meal links (Breakfast/Lunch/Dinner/Brunch) for today
- Returns a list of meals to scrape

### 2. Update scrape_dining_hall method (NEEDS TO BE DONE)

The `scrape_dining_hall` method (starting around line 490) needs major updates.

**Current behavior:**
- Processes all child units equally
- Doesn't distinguish between "Daily Menu" and "Salad Bar" etc.

**New behavior needed:**
1. When processing child units, separate them into two categories:
   - **Daily Menu units** (e.g., "Portola's Daily Menu")
   - **Always Available** categories (Salad Bar, Beverages, etc.)

2. For "Daily Menu" units:
   - Select the child unit
   - Parse the daily menu structure to find today's meals
   - For each meal (Breakfast/Lunch/Dinner/Brunch):
     - Select that menu
     - Scrape all items
     - Create a Meal object with the meal name

3. For "Always Available" categories:
   - Scrape all items from each category
   - Combine them into a single "Always Available" meal

4. For Ortega (no changes):
   - Keep existing behavior

## Detailed Implementation

### Step 2A: Modify child unit processing

Find this code in `scrape_dining_hall`:
```python
if child_units:
    print(f"   ✓ Found {len(child_units)} child units")
    
    # Process each child unit
    for child_unit in child_units:
        child_id = child_unit['id']
        child_name = child_unit['name']
        ...
```

Replace with:
```python
if child_units:
    print(f"   ✓ Found {len(child_units)} child units")
    
    # Separate "Daily Menu" from "always available" categories
    always_available_categories = ['Salad Bar', 'Condiments', 'Breads and Cereals', 'Beverages']
    always_available_items = []
    daily_menu_unit = None
    
    for child_unit in child_units:
        child_name = child_unit['name']
        
        # Check if this is a "Daily Menu"
        if "Daily Menu" in child_name:
            daily_menu_unit = child_unit
            print(f"   ✓ Found daily menu unit: {child_name}")
        elif child_name in always_available_categories:
            # Collect items from this category
            # (see full code in the detailed implementation below)
            pass
    
    # Process daily menu if found
    if daily_menu_unit:
        # (see full code below)
        pass
```

### Step 2B: Process "Always Available" categories

For each "Always Available" category:
```python
elif child_name in always_available_categories:
    print(f"\n3. Processing always-available category: {child_name}")
    child_id = child_unit['id']
    child_response = self.select_child_unit(child_id)
    
    if child_response.get('success'):
        items_html = self.extract_panel_html(child_response, 'itemPanel')
        if items_html and len(items_html) > 100:
            items = self.parse_menu_items(items_html)
            print(f"   ✓ Found {len(items)} items in {child_name}")
            
            # Get nutrition for each item
            for item_data in items:
                detail_oid = item_data['detail_oid']
                menu_oid = item_data['menu_oid']
                item_name = item_data['name']
                
                nutrition_response = self.get_nutrition_label(detail_oid, menu_oid)
                if nutrition_response.get('success'):
                    if nutrition_response.get('is_direct_html'):
                        nutrition_html = nutrition_response.get('html', '')
                    else:
                        nutrition_html = self.extract_panel_html(nutrition_response, 'cbo_nn_nutritionDialogInner')
                    
                    if nutrition_html:
                        nutrition_item = self.parse_nutrition_label(nutrition_html, item_name)
                        always_available_items.append(nutrition_item)
                
                time.sleep(0.3)
        
        time.sleep(0.5)
```

### Step 2C: Process Daily Menu

After collecting "Always Available" items:
```python
if daily_menu_unit:
    child_id = daily_menu_unit['id']
    child_name = daily_menu_unit['name']
    
    print(f"\n3. Selecting daily menu unit: {child_name}")
    child_response = self.select_child_unit(child_id)
    
    if child_response.get('success'):
        time.sleep(0.5)
        
        # Get the menu list panel
        menu_list_html = self.extract_panel_html(child_response, 'menuPanel')
        if not menu_list_html:
            menu_list_html = self.extract_panel_html(child_response, 'childUnitsPanel')
        
        if menu_list_html and len(menu_list_html) > 100:
            # Parse daily menu structure to find today's meals
            todays_meals = self.parse_daily_menu_structure(menu_list_html)
            
            if todays_meals:
                print(f"   ✓ Found {len(todays_meals)} meals for today")
                
                # Process each meal (Breakfast/Lunch/Dinner/Brunch)
                for meal_data in todays_meals:
                    meal_id = meal_data['id']
                    meal_name = meal_data['name']
                    
                    print(f"\n4. Processing meal: {meal_name}")
                    
                    # Select the menu
                    menu_response = self.select_menu(meal_id)
                    
                    if not menu_response.get('success'):
                        print(f"   ✗ Failed to load menu")
                        continue
                    
                    time.sleep(0.5)
                    
                    # Get items
                    items_html = self.extract_panel_html(menu_response, 'itemPanel')
                    if not items_html:
                        continue
                    
                    items = self.parse_menu_items(items_html)
                    print(f"   ✓ Found {len(items)} items")
                    
                    # Create meal object
                    meal = Meal(name=meal_name, meal_id=meal_id)
                    
                    # Process items
                    for item_data in items:
                        detail_oid = item_data['detail_oid']
                        menu_oid = item_data['menu_oid']
                        item_name = item_data['name']
                        
                        # Get nutrition
                        nutrition_response = self.get_nutrition_label(detail_oid, menu_oid)
                        
                        if nutrition_response.get('success'):
                            if nutrition_response.get('is_direct_html'):
                                nutrition_html = nutrition_response.get('html', '')
                            else:
                                nutrition_html = self.extract_panel_html(nutrition_response, 'cbo_nn_nutritionDialogInner')
                            
                            if nutrition_html:
                                nutrition_item = self.parse_nutrition_label(nutrition_html, item_name)
                                meal.items.append(nutrition_item)
                        
                        time.sleep(0.3)
                    
                    dining_hall.meals.append(meal)
```

### Step 2D: Add "Always Available" meal

At the end, after processing all meals:
```python
# Add "Always Available" meal if we collected items
if always_available_items:
    always_available_meal = Meal(name="Always Available", meal_id=None)
    always_available_meal.items = always_available_items
    dining_hall.meals.append(always_available_meal)
    print(f"\n✓ Added 'Always Available' category with {len(always_available_items)} items")
```

## Testing

1. Run with option 4 (one hall, limited items) first
2. Check the output JSON structure:
   ```json
   {
     "name": "Portola Dining Commons",
     "meals": [
       {"name": "Dinner", "items": [...]},
       {"name": "Brunch", "items": [...]},
       {"name": "Always Available", "items": [...]}
     ]
   }
   ```

3. Verify:
   - Ortega still works (unchanged)
   - Portola/Carrillo/De La Guerra have separate meals
   - "Always Available" contains items from all 4 categories

## Expected Output Structure

**For Ortega (no changes):**
```json
{
  "name": "Takeout at Ortega Commons",
  "meals": [
    {"name": "Ortega's Daily Menu", "items": [...]}
  ]
}
```

**For Portola/Carrillo/De La Guerra (weekday):**
```json
{
  "name": "Portola Dining Commons",
  "meals": [
    {"name": "Breakfast", "items": [...]},
    {"name": "Lunch", "items": [...]},
    {"name": "Dinner", "items": [...]},
    {"name": "Always Available", "items": [...]}
  ]
}
```

**For Portola/Carrillo/De La Guerra (weekend):**
```json
{
  "name": "Portola Dining Commons",
  "meals": [
    {"name": "Brunch", "items": [...]},
    {"name": "Dinner", "items": [...]},
    {"name": "Always Available", "items": [...]}
  ]
}
```

## Alternative: Complete Rewrite

If manual implementation is too difficult, I can provide a complete rewritten
version of the scraper with all changes integrated. Let me know if you'd prefer that approach.

# Fixed UCSB Dining Nutrition Scraper - Simplified Output

# Suppress SSL warnings
import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL 1.1.1+')

import requests
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from urllib.parse import urljoin
import html
from bs4 import BeautifulSoup

@dataclass
class NutritionItem:
    """Represents a single food item with nutrition information"""
    name: str
    serving_size: str = ""
    calories: float = 0
    protein: float = 0
    total_carbohydrates: float = 0
    total_fat: float = 0

@dataclass
class Meal:
    """Represents a meal (Breakfast, Lunch, Dinner, etc.)"""
    name: str
    meal_id: Optional[int] = None
    items: List[NutritionItem] = field(default_factory=list)

@dataclass 
class DiningHall:
    """Represents a dining hall with its meals"""
    name: str
    unit_id: int
    meals: List[Meal] = field(default_factory=list)

class UCSBDiningScraper:
    """Improved scraper for UCSB Dining NetNutrition website"""
    
    BASE_URL = "https://nutrition.info.dining.ucsb.edu/NetNutrition/1"
    
    # Dining halls with their unit IDs
    DINING_HALLS = {
        "Takeout at Ortega Commons": 1,
        "De La Guerra Dining Commons": 3,
        "Carrillo Dining Commons": 9,
        "Portola Dining Commons": 15
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': self.BASE_URL,
        })
        
        # Initialize session
        self._init_session()
    
    def _init_session(self):
        """Initialize the session by loading the main page"""
        try:
            response = self.session.get(self.BASE_URL)
            response.raise_for_status()
            print("✓ Session initialized")
        except Exception as e:
            print(f"Warning: Could not initialize session: {e}")
    
    def _make_post_request(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a POST request to the API"""
        url = urljoin(self.BASE_URL + "/", endpoint)
        
        try:
            response = self.session.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            # Try to parse as JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                # If not JSON, return the HTML directly in a structure
                # This happens with nutrition label endpoint
                if 'NutritionDetail' in endpoint:
                    return {
                        'success': True,
                        'html': response.text,
                        'is_direct_html': True
                    }
                else:
                    print(f"Warning: Response from {endpoint} is not JSON")
                    return {'success': False, 'panels': []}
                
        except requests.RequestException as e:
            print(f"Error making request to {endpoint}: {e}")
            return {'success': False, 'panels': []}
    
    def select_unit(self, unit_id: int) -> Dict[str, Any]:
        """Select a dining hall unit"""
        return self._make_post_request("Unit/SelectUnitFromUnitsList", {'unitOid': unit_id})
    
    def select_child_unit(self, unit_id: int) -> Dict[str, Any]:
        """Select a child unit (like a daily menu)"""
        return self._make_post_request("Unit/SelectUnitFromChildUnitsList", {'unitOid': unit_id})
    
    def select_menu(self, menu_id: int) -> Dict[str, Any]:
        """Select a specific menu"""
        return self._make_post_request("Menu/SelectMenu", {'menuOid': menu_id})
    
    def get_nutrition_label(self, detail_oid: int, menu_oid: int = None) -> Dict[str, Any]:
        """Get nutrition label for an item"""
        params = {'detailOid': detail_oid}
        if menu_oid and menu_oid > 0:
            params['menuOid'] = menu_oid
        
        return self._make_post_request("NutritionDetail/ShowItemNutritionLabel", params)
    
    def extract_panel_html(self, response: Dict[str, Any], panel_name: str) -> str:
        """Extract HTML from a panel in the response"""
        if not response.get('success'):
            print(f"      DEBUG: Response not successful")
            return ""
        
        panels = response.get('panels', [])
        print(f"      DEBUG: Found {len(panels)} panels in response")
        
        for panel in panels:
            print(f"      DEBUG: Panel ID: {panel.get('id')}")
            if panel.get('id') == panel_name:
                html_length = len(panel.get('html', ''))
                print(f"      DEBUG: Found target panel '{panel_name}' with {html_length} chars")
                return panel.get('html', '')
        
        print(f"      DEBUG: Panel '{panel_name}' not found")
        return ""
    
    def parse_child_units(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse child units panel to extract child unit links"""
        print(f"      DEBUG: Parsing child units HTML ({len(html_content)} chars)")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        child_units = []
        
        # Look for unit links with onclick handlers
        all_links = soup.find_all('a', href='#')
        print(f"      DEBUG: Found {len(all_links)} <a> tags")
        
        for idx, link in enumerate(all_links):
            onclick = link.get('onclick', '')
            
            # Look for unit selection calls
            match = re.search(r'childUnitsSelectUnit\(["\']?(\d+)["\']?\)', onclick)
            if not match:
                match = re.search(r'unitOid[:\s]*(\d+)', onclick)
            
            if match:
                unit_id = match.group(1)
                unit_name = link.get_text(strip=True)
                if unit_name:
                    print(f"      DEBUG: Found child unit [{idx}]: {unit_name} (ID: {unit_id})")
                    child_units.append({
                        'id': int(unit_id),
                        'name': unit_name
                    })
        
        print(f"      DEBUG: Total child units extracted: {len(child_units)}")
        return child_units
    
    def parse_daily_menu_structure(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Parse the daily menu page structure to find today's meals
        Returns list of meals for today only (Breakfast/Lunch/Dinner or Brunch/Dinner)
        """
        print(f"      DEBUG: Parsing daily menu structure ({len(html_content)} chars)")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get today's date
        from datetime import datetime
        today = datetime.now()
        
        # Format: "Saturday, January 10, 2026"
        today_str = today.strftime("%A, %B %d, %Y")
        print(f"      DEBUG: Looking for today's date: {today_str}")
        
        # Find the header element containing today's date
        todays_meals = []
        
        # Find all header elements
        headers = soup.find_all('header', class_='card-title')
        print(f"      DEBUG: Found {len(headers)} date headers")
        
        for header in headers:
            header_text = header.get_text(strip=True)
            
            # Check if this header matches today's date
            if today_str in header_text:
                print(f"      DEBUG: Found today's date header: {header_text}")
                
                # Find the sibling div that contains meal links
                parent = header.parent
                if parent:
                    # Find the div with meal links (d-flex flex-wrap)
                    meal_container = parent.find('div', class_='d-flex')
                    
                    if meal_container:
                        # Find all links within this container
                        meal_links = meal_container.find_all('a', class_='cbo_nn_menuLink')
                        print(f"      DEBUG: Found {len(meal_links)} meal links for today")
                        
                        for link in meal_links:
                            meal_name = link.get_text(strip=True)
                            onclick = link.get('onclick', '')
                            
                            # Extract menu ID from: menuListSelectMenu(246910)
                            match = re.search(r'menuListSelectMenu\((\d+)\)', onclick)
                            
                            if match:
                                menu_id = int(match.group(1))
                                todays_meals.append({
                                    'id': menu_id,
                                    'name': meal_name,
                                    'meal_type': meal_name.lower()
                                })
                                print(f"      DEBUG: Found meal: {meal_name} (ID: {menu_id})")
                
                break  # Found today, no need to check other dates
        
        if not todays_meals:
            print(f"      ⚠ Could not find meals for today")
        
        print(f"      DEBUG: Total meals for today: {len(todays_meals)}")
        return todays_meals
    
    def parse_menu_list(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse menu list to extract available menus"""
        print(f"      DEBUG: Parsing menu list HTML ({len(html_content)} chars)")
        
        # Save HTML for inspection
        with open('debug_menu_list.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"      DEBUG: Saved HTML to debug_menu_list.html")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        menus = []
        
        # Look for menu links with data-menuoid or onclick handlers
        menu_links = soup.find_all('a', href='#')
        print(f"      DEBUG: Found {len(menu_links)} <a> tags with href='#'")
        
        for idx, link in enumerate(menu_links):
            # Try data attribute first
            menu_id = link.get('data-menuoid')
            
            # Try onclick attribute
            if not menu_id:
                onclick = link.get('onclick', '')
                match = re.search(r'menuOid[:\s]*(\d+)', onclick)
                if match:
                    menu_id = match.group(1)
            
            if menu_id:
                menu_name = link.get_text(strip=True)
                if menu_name:  # Only add if we have a name
                    print(f"      DEBUG: Found menu [{idx}]: {menu_name} (ID: {menu_id})")
                    menus.append({
                        'id': int(menu_id),
                        'name': menu_name
                    })
        
        print(f"      DEBUG: Total menus extracted: {len(menus)}")
        return menus
    
    def parse_menu_items(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse menu detail panel to extract food items"""
        soup = BeautifulSoup(html_content, 'html.parser')
        items = []
        seen_items = set()
        
        # Look for all <a> tags with getItemNutritionLabel in onclick
        nutrition_links = soup.find_all('a', onclick=re.compile(r'getItemNutritionLabel'))
        print(f"      DEBUG: Found {len(nutrition_links)} nutrition links")
        
        for link in nutrition_links:
            onclick = link.get('onclick', '')
            
            # Extract detail_oid from onclick
            match = re.search(r'getItemNutritionLabel(?:OnClick)?\s*\(\s*event\s*,\s*(\d+)\s*\)', onclick)
            if not match:
                match = re.search(r'getItemNutritionLabel(?:OnClick)?\s*\(\s*(\d+)\s*\)', onclick)
            
            if match:
                detail_oid = int(match.group(1))
                item_name = link.get_text(strip=True)
                menu_oid = 0
                
                if item_name:
                    item_key = (detail_oid, item_name)
                    if item_key not in seen_items:
                        items.append({
                            'detail_oid': detail_oid,
                            'menu_oid': menu_oid,
                            'name': item_name
                        })
                        seen_items.add(item_key)
                        print(f"      DEBUG: Found item: {item_name[:50]} (detail_oid: {detail_oid})")
        
        print(f"      DEBUG: Total unique items found: {len(items)}")
        return items
    
    def parse_nutrition_label(self, html_content: str, item_name: str = "unknown") -> NutritionItem:
        """Parse nutrition label HTML to extract nutrition facts (simplified)"""
        soup = BeautifulSoup(html_content, 'html.parser')
        item = NutritionItem(name=item_name)
        
        # Extract serving size
        serving_div = soup.find('div', class_='inline-div-right', string=re.compile(r'\(.*g\)'))
        if not serving_div:
            serving_label = soup.find('div', class_='inline-div-left', string='Serving Size')
            if serving_label:
                parent = serving_label.parent
                serving_div = parent.find('div', class_='inline-div-right')
        
        if serving_div:
            item.serving_size = serving_div.get_text(strip=True).replace('\xa0', ' ')
        
        # Extract calories
        calories_div = soup.find('div', class_='inline-div-right bold-text font-22')
        if calories_div:
            calories_text = calories_div.get_text(strip=True)
            try:
                item.calories = float(calories_text)
            except ValueError:
                pass
        
        # Helper function to extract nutrient value
        def extract_nutrient(label_text: str) -> float:
            label_span = soup.find('span', class_='bold-text', string=label_text)
            if not label_span:
                label_span = soup.find('span', string=label_text)
            
            if label_span:
                value_span = label_span.find_next_sibling('span')
                if value_span:
                    value_text = value_span.get_text(strip=True)
                    value_text = value_text.replace('\xa0', '').replace('&nbsp;', '')
                    match = re.search(r'(\d+\.?\d*)', value_text)
                    if match:
                        try:
                            return float(match.group(1))
                        except ValueError:
                            pass
            return 0.0
        
        # Extract only the nutrients we need
        item.protein = extract_nutrient('Protein')
        item.total_carbohydrates = extract_nutrient('Total Carbohydrate')
        item.total_fat = extract_nutrient('Total Fat')
        
        print(f"      ✓ Parsed: {item.serving_size}, {item.calories} cal, {item.protein}g protein, {item.total_carbohydrates}g carbs, {item.total_fat}g fat")
        
        return item
    
    def scrape_dining_hall(self, hall_name: str, unit_id: int, max_items_per_meal: int = None) -> DiningHall:
        """Scrape a single dining hall with daily menu support"""
        print("\n" + "="*60)
        print(f"Scraping: {hall_name} (Unit ID: {unit_id})")
        print("="*60)
        
        dining_hall = DiningHall(name=hall_name, unit_id=unit_id, meals=[])
        
        # Step 1: Select the dining hall
        print("1. Selecting dining hall...")
        unit_response = self.select_unit(unit_id)
        
        if not unit_response.get('success'):
            print(f"   ✗ Failed to select {hall_name}")
            return dining_hall
        
        print(f"   ✓ Selected {hall_name}")
        time.sleep(0.5)
        
        # Step 2: Check for child units (daily menus, etc.)
        print("2. Checking for child units...")
        child_units_html = self.extract_panel_html(unit_response, 'childUnitsPanel')
        
        # Track "always available" items
        always_available_categories = ['Salad Bar', 'Condiments', 'Breads and Cereals', 'Beverages']
        always_available_items = []
        
        if child_units_html and len(child_units_html) > 50:
            print("   ✓ Found child units panel")
            child_units = self.parse_child_units(child_units_html)
            
            if child_units:
                print(f"   ✓ Found {len(child_units)} child units")
                
                # Separate "Daily Menu" from "always available" categories
                daily_menu_unit = None
                
                for child_unit in child_units:
                    child_name = child_unit['name']
                    
                    # Check if this is a "Daily Menu"
                    if "Daily Menu" in child_name:
                        daily_menu_unit = child_unit
                        print(f"   ✓ Found daily menu unit: {child_name}")
                    elif child_name in always_available_categories:
                        # Process "always available" category
                        print(f"\n3. Processing always-available: {child_name}")
                        child_id = child_unit['id']
                        child_response = self.select_child_unit(child_id)
                        
                        if child_response.get('success'):
                            items_html = self.extract_panel_html(child_response, 'itemPanel')
                            if items_html and len(items_html) > 100:
                                items = self.parse_menu_items(items_html)
                                print(f"   ✓ Found {len(items)} items")
                                
                                items_to_process = items[:max_items_per_meal] if max_items_per_meal else items
                                
                                for item_data in items_to_process:
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
                                        else:
                                            always_available_items.append(NutritionItem(name=item_name))
                                    else:
                                        always_available_items.append(NutritionItem(name=item_name))
                                    
                                    time.sleep(0.3)
                            
                            time.sleep(0.5)
                
                # Now process the daily menu if found
                if daily_menu_unit:
                    child_id = daily_menu_unit['id']
                    child_name = daily_menu_unit['name']
                    
                    print(f"\n3. Selecting daily menu: {child_name}")
                    child_response = self.select_child_unit(child_id)
                    
                    if child_response.get('success'):
                        time.sleep(0.5)
                        
                        # Check if this shows a menu structure with dates
                        menu_list_html = self.extract_panel_html(child_response, 'menuPanel')
                        if not menu_list_html:
                            menu_list_html = self.extract_panel_html(child_response, 'childUnitsPanel')
                        
                        if menu_list_html and len(menu_list_html) > 100:
                            # Try to parse as daily menu structure
                            todays_meals = self.parse_daily_menu_structure(menu_list_html)
                            
                            if todays_meals:
                                print(f"   ✓ Found {len(todays_meals)} meals for today")
                                
                                # Process each meal
                                for meal_data in todays_meals:
                                    meal_id = meal_data['id']
                                    meal_name = meal_data['name']
                                    
                                    print(f"\n4. Processing meal: {meal_name}")
                                    menu_response = self.select_menu(meal_id)
                                    
                                    if not menu_response.get('success'):
                                        print(f"   ✗ Failed to load menu")
                                        continue
                                    
                                    time.sleep(0.5)
                                    
                                    items_html = self.extract_panel_html(menu_response, 'itemPanel')
                                    if not items_html:
                                        print(f"   ✗ No items found")
                                        continue
                                    
                                    items = self.parse_menu_items(items_html)
                                    print(f"   ✓ Found {len(items)} items")
                                    
                                    if not items:
                                        continue
                                    
                                    meal = Meal(name=meal_name, meal_id=meal_id)
                                    items_to_process = items[:max_items_per_meal] if max_items_per_meal else items
                                    
                                    for idx, item_data in enumerate(items_to_process, 1):
                                        detail_oid = item_data['detail_oid']
                                        menu_oid = item_data['menu_oid']
                                        item_name = item_data['name']
                                        
                                        print(f"      [{idx}/{len(items_to_process)}] {item_name}...")
                                        
                                        nutrition_response = self.get_nutrition_label(detail_oid, menu_oid)
                                        if nutrition_response.get('success'):
                                            if nutrition_response.get('is_direct_html'):
                                                nutrition_html = nutrition_response.get('html', '')
                                            else:
                                                nutrition_html = self.extract_panel_html(nutrition_response, 'cbo_nn_nutritionDialogInner')
                                            
                                            if nutrition_html:
                                                nutrition_item = self.parse_nutrition_label(nutrition_html, item_name)
                                                meal.items.append(nutrition_item)
                                            else:
                                                meal.items.append(NutritionItem(name=item_name))
                                        else:
                                            meal.items.append(NutritionItem(name=item_name))
                                        
                                        time.sleep(0.3)
                                    
                                    dining_hall.meals.append(meal)
                            else:
                                # Fallback to regular menu processing
                                self._process_menus_in_unit(child_response, dining_hall, child_name, max_items_per_meal)
                        else:
                            self._process_menus_in_unit(child_response, dining_hall, child_name, max_items_per_meal)
                else:
                    # No daily menu, process child units normally
                    for child_unit in child_units:
                        if child_unit['name'] not in always_available_categories:
                            child_id = child_unit['id']
                            child_name = child_unit['name']
                            
                            print(f"\n3. Selecting child unit: {child_name}")
                            child_response = self.select_child_unit(child_id)
                            
                            if not child_response.get('success'):
                                print(f"   ✗ Failed to select")
                                continue
                            
                            time.sleep(0.5)
                            self._process_menus_in_unit(child_response, dining_hall, child_name, max_items_per_meal)
                
                # Add "Always Available" meal
                if always_available_items:
                    always_meal = Meal(name="Always Available", meal_id=None)
                    always_meal.items = always_available_items
                    dining_hall.meals.append(always_meal)
                    print(f"\n✓ Added 'Always Available' with {len(always_available_items)} items")
            else:
                print("   ✗ No child units found")
        else:
            print("   No child units, processing directly...")
            self._process_menus_in_unit(unit_response, dining_hall, hall_name, max_items_per_meal)
        
        print(f"\n✓ Completed {hall_name}")
        print(f"  Found {len(dining_hall.meals)} meals")
        total_items = sum(len(meal.items) for meal in dining_hall.meals)
        print(f"  Total items: {total_items}")
        
        return dining_hall
    
    def _process_menus_in_unit(self, response: Dict[str, Any], dining_hall: DiningHall, 
                                unit_name: str, max_items_per_meal: int = None):
        """Process menus found in a unit response"""
        
        # Check if itemPanel has content (direct items, no menu selection needed)
        items_html = self.extract_panel_html(response, 'itemPanel')
        if items_html and len(items_html) > 1000:
            print(f"   ✓ Found items directly (no menu selection needed)")
            self._process_items_directly(items_html, dining_hall, unit_name, max_items_per_meal)
            return
        
        # Otherwise, look for menu list
        menu_list_html = None
        for panel_name in ['menuPanel', 'coursesPanel', 'childUnitsPanel']:
            html = self.extract_panel_html(response, panel_name)
            if html and len(html) > 50:
                menu_list_html = html
                break
        
        if not menu_list_html:
            print(f"   ✗ No menus found in {unit_name}")
            return
        
        menus = self.parse_menu_list(menu_list_html)
        print(f"   ✓ Found {len(menus)} menus in {unit_name}")
        
        if not menus:
            return
        
        # Process each menu
        for menu in menus:
            menu_id = menu['id']
            menu_name = menu['name']
            
            print(f"\n4. Processing menu: {menu_name}")
            
            menu_response = self.select_menu(menu_id)
            
            if not menu_response.get('success'):
                print(f"   ✗ Failed to load menu")
                continue
            
            time.sleep(0.5)
            
            items_html = self.extract_panel_html(menu_response, 'itemPanel')
            
            if not items_html:
                print(f"   ✗ No items panel found")
                continue
            
            items = self.parse_menu_items(items_html)
            print(f"   ✓ Found {len(items)} items")
            
            if not items:
                continue
            
            meal = Meal(name=menu_name, meal_id=menu_id)
            items_to_process = items[:max_items_per_meal] if max_items_per_meal else items
            
            for idx, item in enumerate(items_to_process, 1):
                item_name = item['name']
                detail_oid = item['detail_oid']
                menu_oid = item['menu_oid']
                
                print(f"      [{idx}/{len(items_to_process)}] {item_name[:40]}...")
                
                nutrition_response = self.get_nutrition_label(detail_oid, menu_oid)
                
                if nutrition_response.get('success'):
                    if nutrition_response.get('is_direct_html'):
                        nutrition_html = nutrition_response.get('html', '')
                    else:
                        nutrition_html = self.extract_panel_html(nutrition_response, 'cbo_nn_nutritionDialogInner')
                    
                    if nutrition_html:
                        nutrition_item = self.parse_nutrition_label(nutrition_html, item_name)
                        nutrition_item.name = item_name
                        meal.items.append(nutrition_item)
                    else:
                        meal.items.append(NutritionItem(name=item_name))
                else:
                    meal.items.append(NutritionItem(name=item_name))
                
                time.sleep(0.3)
            
            if meal.items:
                dining_hall.meals.append(meal)
    
    def _process_items_directly(self, items_html: str, dining_hall: DiningHall, 
                                 meal_name: str, max_items: int = None):
        """Process items when they're shown directly without menu selection"""
        items = self.parse_menu_items(items_html)
        print(f"   ✓ Found {len(items)} items")
        
        if not items:
            return
        
        meal = Meal(name=meal_name)
        items_to_process = items[:max_items] if max_items else items
        
        for idx, item in enumerate(items_to_process, 1):
            item_name = item['name']
            detail_oid = item['detail_oid']
            menu_oid = item['menu_oid']
            
            print(f"      [{idx}/{len(items_to_process)}] {item_name[:40]}...")
            
            nutrition_response = self.get_nutrition_label(detail_oid, menu_oid)
            
            if nutrition_response.get('success'):
                if nutrition_response.get('is_direct_html'):
                    nutrition_html = nutrition_response.get('html', '')
                else:
                    nutrition_html = self.extract_panel_html(nutrition_response, 'cbo_nn_nutritionDialogInner')
                
                if nutrition_html:
                    nutrition_item = self.parse_nutrition_label(nutrition_html, item_name)
                    nutrition_item.name = item_name
                    meal.items.append(nutrition_item)
                else:
                    meal.items.append(NutritionItem(name=item_name))
            else:
                meal.items.append(NutritionItem(name=item_name))
            
            time.sleep(0.3)
        
        if meal.items:
            dining_hall.meals.append(meal)
    
    def scrape_all_dining_halls(self, max_halls: int = None, max_items_per_meal: int = None) -> List[DiningHall]:
        """Scrape data for all specified dining halls"""
        dining_halls_data = []
        
        halls_to_scrape = list(self.DINING_HALLS.items())
        if max_halls:
            halls_to_scrape = halls_to_scrape[:max_halls]
        
        for hall_name, unit_id in halls_to_scrape:
            hall_data = self.scrape_dining_hall(hall_name, unit_id, max_items_per_meal)
            dining_halls_data.append(hall_data)
            
            time.sleep(2)
        
        return dining_halls_data
    
    def save_to_json(self, dining_halls: List[DiningHall], filename: str = None, use_timestamp: bool = False):
        """Save scraped data to JSON file"""
        if filename is None:
            if use_timestamp:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ucsb_dining_data_{timestamp}.json"
            else:
                filename = "ucsb_dining_data.json"
        
        # Convert dataclasses to dictionaries
        data = [asdict(hall) for hall in dining_halls]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Data saved to {filename}")
        return filename

def main():
    """Main function to run the scraper"""
    print("UCSB Dining Nutrition Scraper (Simplified Output)")
    print("=" * 60)
    
    scraper = UCSBDiningScraper()
    
    print("\nScraping Options:")
    print("1. Scrape ALL dining halls with ALL items")
    print("2. Scrape ONE dining hall with ALL items")
    print("3. Scrape ALL dining halls with LIMITED items (5 per meal - for testing)")
    print("4. Scrape ONE dining hall with LIMITED items (5 per meal - for testing)")
    
    choice = input("\nEnter choice (1-4, or press Enter for option 4): ").strip() or "4"
    
    print("\nOutput file options:")
    print("1. Use consistent filename 'ucsb_dining_data.json' (recommended for external programs)")
    print("2. Use timestamped filename (keeps historical data)")
    
    filename_choice = input("\nEnter choice (1-2, or press Enter for option 1): ").strip() or "1"
    use_timestamp = filename_choice == "2"
    
    max_halls = None
    max_items = None
    
    if choice in ["2", "4"]:
        max_halls = 1
        print(f"\nWill scrape: {list(scraper.DINING_HALLS.keys())[0]}")
    
    if choice in ["3", "4"]:
        max_items = 5
        print("Will limit to 5 items per meal")
    
    print("\nStarting scrape...")
    dining_halls = scraper.scrape_all_dining_halls(max_halls=max_halls, max_items_per_meal=max_items)
    
    filename = scraper.save_to_json(dining_halls, use_timestamp=use_timestamp)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SCRAPING SUMMARY")
    print("=" * 60)
    
    total_meals = 0
    total_items = 0
    
    for hall in dining_halls:
        hall_meals = len(hall.meals)
        hall_items = sum(len(meal.items) for meal in hall.meals)
        total_meals += hall_meals
        total_items += hall_items
        
        print(f"\n{hall.name}:")
        print(f"  Meals: {hall_meals}")
        print(f"  Items: {hall_items}")
        
        for meal in hall.meals:
            print(f"    - {meal.name}: {len(meal.items)} items")
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {total_items} items across {total_meals} meals")
    print(f"Data saved to: {filename}")
    print("=" * 60)
    
    # Show sample data
    if dining_halls and dining_halls[0].meals and dining_halls[0].meals[0].items:
        print("\nSAMPLE DATA:")
        sample_item = dining_halls[0].meals[0].items[0]
        print(f"  Item: {sample_item.name}")
        print(f"  Serving: {sample_item.serving_size}")
        print(f"  Calories: {sample_item.calories}")
        print(f"  Protein: {sample_item.protein}g")
        print(f"  Total Carbohydrates: {sample_item.total_carbohydrates}g")
        print(f"  Total Fat: {sample_item.total_fat}g")

if __name__ == "__main__":
    main()
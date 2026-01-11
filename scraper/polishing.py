#!/usr/bin/env python3
"""
Debug script to see why daily menus aren't being found
Run this to see what's happening with Portola's daily menu
"""

import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL 1.1.1+')

import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://nutrition.sa.ucsb.edu/NetNutrition"
session = requests.Session()

# Initialize
print("Initializing session...")
session.get(f"{BASE_URL}/1")

# Select Portola (unit_id = 5)
print("Selecting Portola...")
response = session.post(f"{BASE_URL}/Unit/SelectUnitFromUnitsList", data={'unitOid': '5'})
data = response.json()

# Get child units
for panel in data.get('panels', []):
    if panel.get('id') == 'childUnitsPanel':
        html = panel.get('html', '')
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all links
        links = soup.find_all('a')
        print(f"\nFound {len(links)} child unit links:")
        for link in links:
            print(f"  - {link.get_text(strip=True)}")
        
        # Find "Daily Menu" link
        daily_menu_link = None
        for link in links:
            if "Daily Menu" in link.get_text():
                daily_menu_link = link
                onclick = link.get('onclick', '')
                import re
                match = re.search(r'childUnitsSelectUnit\(["\']?(\d+)["\']?\)', onclick)
                if match:
                    daily_menu_id = int(match.group(1))
                    print(f"\n✓ Found Daily Menu with ID: {daily_menu_id}")
                    
                    # Select it
                    print("\nSelecting Daily Menu...")
                    response2 = session.post(
                        f"{BASE_URL}/Unit/SelectChildUnit",
                        data={'unitOid': str(daily_menu_id)}
                    )
                    data2 = response2.json()
                    
                    # Look at all panels
                    print("\nPanels in Daily Menu response:")
                    for panel2 in data2.get('panels', []):
                        panel_id = panel2.get('id')
                        panel_html = panel2.get('html', '')
                        print(f"  - {panel_id}: {len(panel_html)} chars")
                        
                        if panel_id in ['menuPanel', 'childUnitsPanel'] and len(panel_html) > 100:
                            # Save it
                            filename = f'debug_daily_menu_{panel_id}.html'
                            with open(filename, 'w', encoding='utf-8') as f:
                                f.write(panel_html)
                            print(f"    ✓ Saved to {filename}")
                            
                            # Look for today's date
                            today = datetime.now()
                            today_str = today.strftime("%A, %B %d, %Y")
                            print(f"\n    Looking for: {today_str}")
                            
                            if today_str in panel_html:
                                print(f"    ✓ Found today's date!")
                            else:
                                print(f"    ✗ Today's date not found")
                                # Try other formats
                                alt_formats = [
                                    today.strftime("%A, %B %-d, %Y"),
                                    today.strftime("%A, %b %d, %Y"),
                                    today.strftime("%B %d, %Y"),
                                ]
                                for fmt in alt_formats:
                                    if fmt in panel_html:
                                        print(f"    ✓ Found alternate format: {fmt}")
                                        break
                            
                            # Look for meal names
                            soup2 = BeautifulSoup(panel_html, 'html.parser')
                            meal_names = ['Breakfast', 'Lunch', 'Dinner', 'Brunch']
                            found_meals = []
                            for meal in meal_names:
                                meal_links = soup2.find_all('a', string=meal)
                                if meal_links:
                                    found_meals.append(meal)
                                    print(f"    ✓ Found meal link: {meal}")
                            
                            if not found_meals:
                                print(f"    ✗ No meal links found")
                                print(f"    All links in panel:")
                                all_links = soup2.find_all('a')
                                for link in all_links[:10]:  # First 10
                                    print(f"      - {link.get_text(strip=True)[:50]}")
                    
                    break

print("\n" + "="*60)
print("Debug complete! Check the debug_daily_menu_*.html files")
print("="*60)
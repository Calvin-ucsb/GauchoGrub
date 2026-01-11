# UCSB Dining Nutrition Scraper

A Python scraper for UCSB dining hall nutrition information.

## Features

- Scrapes all UCSB dining halls or select specific ones
- Extracts complete nutrition information for each menu item
- Saves data in clean JSON format
- Includes ingredients and allergen information

## Quick Start

```bash
# Run the scraper
python test.py

# View example usage
python example_usage.py
```

## Output Formats

### Option 1: Consistent Filename (Recommended for External Programs)

```bash
# Always writes to: ucsb_dining_data.json
# This file is overwritten each time
# Best for: Web apps, mobile apps, automated scripts
```

**Why use this:**
- External programs always know the filename
- Simple to integrate: just read `ucsb_dining_data.json`
- No file cleanup needed
- Latest data is always available

**Example integration:**
```python
import json

# Your web app/script can simply do this:
with open('ucsb_dining_data.json', 'r') as f:
    dining_data = json.load(f)
```

### Option 2: Timestamped Filename (For Historical Data)

```bash
# Creates: ucsb_dining_data_20250110_143052.json
# Each run creates a new file
# Best for: Data analysis, comparing menus over time
```

**Why use this:**
- Keep historical records
- Track menu changes over time
- Useful for data analysis projects

## Usage Recommendations

### For Web/Mobile Apps

1. **Use consistent filename** (Option 1)
2. **Run scraper on a schedule** (e.g., cron job every 6 hours)
3. **Your app reads the same file** (`ucsb_dining_data.json`)

Example cron job:
```bash
# Run every 6 hours
0 */6 * * * cd /path/to/scraper && python3 test.py <<< "1\n1\n"
```

The `<<< "1\n1\n"` provides automated input:
- First `1` = scrape all dining halls
- Second `1` = use consistent filename

### For Data Analysis

1. **Use timestamped filenames** (Option 2)
2. **Collect data over time**
3. **Analyze trends**

### For Development/Testing

Use the limited scraping options:
- Option 3: All halls, 5 items per meal
- Option 4: One hall, 5 items per meal (fastest)

## JSON Data Structure

```json
[
  {
    "name": "Takeout at Ortega Commons",
    "unit_id": 1,
    "meals": [
      {
        "name": "Ortega's Daily Menu",
        "meal_id": null,
        "items": [
          {
            "name": "Korean Chicken & Rice",
            "serving_size": "Plate (389g)",
            "calories": 340.0,
            "total_fat": 12.0,
            "saturated_fat": 2.5,
            "trans_fat": 0.0,
            "cholesterol": 70.0,
            "sodium": 1560.0,
            "total_carbohydrates": 47.0,
            "dietary_fiber": 2.0,
            "sugars": 20.0,
            "protein": 24.0,
            "vitamin_d": 0.0,
            "calcium": 51.0,
            "iron": 12.64,
            "potassium": 500.0,
            "nutrition_facts": { ... }
          }
        ]
      }
    ]
  }
]
```

## Integration Examples

See `example_usage.py` for detailed examples including:
- Listing all items
- Searching items
- Finding high-protein items
- Calculating meal totals
- Converting to API format

## Debugging

If something goes wrong, uncomment the debug lines in the code:

```python
# In parse_menu_items()
with open('debug_items_parse.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# In parse_nutrition_label()
safe_name = re.sub(r'[^\w\s-]', '', item_name)[:30]
debug_file = f'debug_nutrition_{safe_name}.html'
with open(debug_file, 'w', encoding='utf-8') as f:
    f.write(html_content)
```

This will save the raw HTML for inspection.

## Performance

- **Full scrape (all halls, all items)**: ~2-5 minutes
- **Single hall, limited items**: ~10-30 seconds
- **Rate limiting**: 1 second delay between items, 2 seconds between halls

## Best Practices

1. **Don't run too frequently** - Menus don't change that often
   - Recommended: Every 6-12 hours is plenty
   - Maximum: Once per hour

2. **Use consistent filename for production** - Makes integration easier

3. **Handle missing data gracefully** - Some items may have incomplete nutrition info

4. **Cache the data** - Don't scrape on every request in a web app
   - Scrape periodically and save to file
   - Serve from file/database

5. **Monitor for changes** - The website structure could change
   - Check debug files if scraping fails
   - Keep backup of working scraper version

## Error Handling in Your Code

```python
import json
from datetime import datetime
import os

def get_dining_data():
    """Load dining data with error handling"""
    filename = 'ucsb_dining_data.json'
    
    # Check if file exists
    if not os.path.exists(filename):
        return {'error': 'Data file not found'}
    
    # Check if file is recent (< 12 hours old)
    file_age = datetime.now().timestamp() - os.path.getmtime(filename)
    if file_age > 12 * 3600:  # 12 hours in seconds
        print("Warning: Data is more than 12 hours old")
    
    # Load the data
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {'error': 'Invalid JSON file'}
    except Exception as e:
        return {'error': str(e)}

# Usage
data = get_dining_data()
if 'error' in data:
    print(f"Error: {data['error']}")
else:
    print(f"Loaded data for {len(data)} dining halls")
```

## License

MIT License - Free to use for any purpose

## Contributing

Feel free to submit issues or pull requests!

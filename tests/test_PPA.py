import argparse
from search_ai import search

parser = argparse.ArgumentParser()
parser.add_argument('--org', required=True, help='Organization name, e.g., "ICICI Bank"')
parser.add_argument('--country', required=False, default=None, help='Optional country, e.g., "India"')
args = parser.parse_args()

org = args.org.strip()
country = args.country.strip() if args.country else None
query = f'{org} privacy policy'
if country:
    query = f'{query} {country}'

results = search(query)

for result in results:
    data = result.model_dump() if hasattr(result, 'model_dump') else (result.__dict__ if hasattr(result, '__dict__') else {})
    link = data.get('link')
    if link:
        print(link)
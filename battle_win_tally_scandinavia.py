import requests
import mwparserfromhell
import pandas as pd
import os

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

COUNTRY_CATEGORIES = {
    'Sweden': [
        'Category:Battles_involving_Sweden'
    ],
    'Norway': [
        'Category:Battles_involving_Norway'
    ],
    'Denmark': [
        'Category:Battles_involving_Denmark'
    ]
}

def get_category_members(category, cmcontinue=None):
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': category,
        'cmlimit': '500',
        'format': 'json'
    }
    if cmcontinue:
        params['cmcontinue'] = cmcontinue
    resp = requests.get(WIKIPEDIA_API_URL, params=params).json()
    members = [m['title'] for m in resp['query']['categorymembers']]
    if 'continue' in resp:
        members += get_category_members(category, resp['continue']['cmcontinue'])
    return members

def parse_infobox_result(page_title):
    params = {
        'action': 'parse',
        'page': page_title,
        'prop': 'wikitext',
        'format': 'json'
    }
    text = requests.get(WIKIPEDIA_API_URL, params=params).json()['parse']['wikitext']['*']
    wikicode = mwparserfromhell.parse(text)
    for tpl in wikicode.filter_templates():
        name = tpl.name.lower().strip()
        if 'infobox' in name:
            if tpl.has('result'):
                return str(tpl.get('result').value).strip()
    return None

def normalize_result(result_str):
    if not result_str:
        return 'unknown'
    s = result_str.lower()
    if 'victory' in s or 'win' in s or 'triumph' in s:
        return 'win'
    if 'defeat' in s or 'loss' in s or 'retreat' in s:
        return 'loss'
    if 'draw' in s or 'stalemate' in s:
        return 'draw'
    return 'other'

def main():
    print(f"Working directory: {os.getcwd()}")
    records = []
    for country, categories in COUNTRY_CATEGORIES.items():
        for cat in categories:
            print(f"\nFetching battles for {country} from category {cat}")
            titles = get_category_members(cat)
            print(f"Found {len(titles)} battles")
            for i, title in enumerate(titles, 1):
                print(f"[{country}] Processing {i}/{len(titles)}: {title}")
                try:
                    result = parse_infobox_result(title)
                    norm = normalize_result(result)
                except Exception as e:
                    print(f"Error processing {title}: {e}")
                    result = None
                    norm = 'unknown'
                records.append({
                    'battle': title,
                    'country': country,
                    'result': norm,
                    'source_url': f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                })
    print(f"\nProcessing complete. Total battles processed: {len(records)}")
    df = pd.DataFrame(records)

    try:
        df.to_csv('battle_results_raw_scandinavia.csv', index=False)
        print("Raw results written to battle_results_raw_scandinavia.csv")
    except Exception as e:
        print("Error writing raw results:", e)

    try:
        win_counts = df[df['result'] == 'win'].groupby('country').size().reset_index(name='wins')
        win_counts.to_csv('battle_win_counts_scandinavia.csv', index=False)
        print("Win counts written to battle_win_counts_scandinavia.csv")
        print("\nWin counts:")
        print(win_counts)
    except Exception as e:
        print("Error writing win counts:", e)

    print("\nScript completed and CSV files saved.")

if __name__ == '__main__':
    main()

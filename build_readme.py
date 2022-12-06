import requests
import pathlib
import re
import os

root = pathlib.Path(__file__).parent.resolve()


def replace_marker(content, marker, chunk):
    r = re.compile(
        r'<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->'.format(marker, marker),
        re.DOTALL,
    )
    chunk = '\n{}\n'.format(chunk)
    chunk = '<!-- {} starts -->{}<!-- {} ends -->'.format(marker, chunk, marker)
    return r.sub(chunk, content)


def fetch_projects():
    url = "http://strapi.schneider.today/api/projects"

    payload={}
    headers = {
    'Authorization': 'Bearer ' + os.environ['STRAPI_TOKEN']
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    entries = [entry["attributes"] for entry in response.json()['data']]
    # sort by newest date
    entries = sorted(entries, key=lambda k: k['date'], reverse=True)
    # change format from YYYY-MM-DD to DD.MM.YYYY for each date in entries
    for entry in entries:
        entry['date'] = entry['date'].split("-")
        entry['date'] = str(entry['date'][2] + "." + entry['date'][1] + "." + entry['date'][0])

    return [
               {
                   'title': entry['title'],
                   'url': entry['url'],
                   'published': entry['date']
               }
               for entry in entries
           ]


if __name__ == '__main__':
    readme_path = root / 'README.md'
    readme = readme_path.open(encoding='utf-8').read()
    entries = fetch_projects()
    print(f'{entries}')
    entries_md = '\n'.join(
        ['* [{title}]({url}) - {published}'.format(**entry) for entry in entries]
    )

    # Update entries
    rewritten_entries = replace_marker(readme, 'projects', entries_md)
    print(rewritten_entries)
    readme_path.open('w', encoding="utf-8").write(rewritten_entries)
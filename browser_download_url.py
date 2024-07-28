import requests

def get_latest_release(owner, repo):
    url = f"https://api.github.com/repos/01000001-01001110/dark_macro_tool/releases/latest"
    response = requests.get(url)
    release_data = response.json()
    download_url = release_data['assets'][0]['browser_download_url']
    return download_url

download_url = get_latest_release('01000001-01001110', 'dark_macro_tool')

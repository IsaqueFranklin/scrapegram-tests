import json
import httpx
from urllib.parse import quote 
from jmespath import parse_post

def scrape_user_posts(user_id: str, session: httpx.Client, page_size=12, max_pages: int = None):
    base_url = "https://www.instagram.com/graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables="
    variables = {
        "id": user_id,
        "first": page_size,
        "after": None,
    }

    _page_number = 1 
    while True:
        resp = session.get(base_url + quote(json.dumps(variables)))
        data = resp.json()
        posts = data["data"]["user"]["edge_owner_to_timeline_media"]
        for post in posts["edges"]:
            yield parse_post(post["node"]) # note: we're using parse_post function from the other file.
        page_info = posts["page_info"]

        if _page_number == 1:
            print(f"scraping total {posts['count']} posts of {user_id}")
        else:
            print(f"scraping page {_page_number}")
        if not page_info["has_next_page"]:
            break
        if variables["after"] == page_info["end_cursor"]:
            break
        variables["after"] = page_info["end_cursor"]
        _page_number += 1 
        if max_pages and _page_number > max_pages:
            break

#Example run:
if __name__ == "__main__":
    with httpx.Client(timeout=httpx.Timeout(20.0)) as session:
        posts = list(scrape_user_posts("1067259270", session, max_pages=3))
        print(json.dumps(posts, indent=2, ensure_ascii=False))

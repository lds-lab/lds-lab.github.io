import os
from bs4 import BeautifulSoup

MAX_ITEMS = 5  # Maximum content items per page

def load_page(page_num):
    """Load and parse page_{page_num}.html; create a new one if it does not exist."""
    filename = f"page_{page_num}.html"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    else:
        # Create a new minimal page with the container using the fixed attributes.
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Page {page_num}</title>
</head>
<body>
  <div data-id="pt-cv-page-1" class="pt-cv-page" data-cvc="1">
  </div>
  <div class="pt-cv-pagination-wrapper">
    <ul class="pt-cv-pagination pt-cv-normal pagination" data-totalpages="?" data-currentpage="{page_num}">
      <li><a role="button" onclick="loadContent('./page_{page_num}.html')">›</a></li>
    </ul>
  </div>
</body>
</html>'''
        soup = BeautifulSoup(html, "html.parser")
    return soup

def save_page(page_num, soup):
    """Save the soup back to page_{page_num}.html."""
    filename = f"page_{page_num}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(soup))

def get_content_container(soup):
    """Find (or create) the content container identified by data-id="pt-cv-page-1"."""
    container = soup.find("div", {"data-id": "pt-cv-page-1"})
    if container is None:
        container = soup.new_tag("div", **{"data-id": "pt-cv-page-1", "class": "pt-cv-page", "data-cvc": "1"})
        if soup.body:
            soup.body.insert(0, container)
        else:
            soup.append(container)
    return container

def remove_latest_content():
    """
    Remove the latest (top) content item from page_1.html, then shift items upward from subsequent pages.
    If after shifting a page becomes empty, remove that page.
    """
    page_num = 1
    # Load page_1.html
    soup = load_page(page_num)
    container = get_content_container(soup)
    items = container.find_all("div", class_="pt-cv-content-item")

    if not items:
        print("No content found on page_1.html to remove.")
        return

    # Remove the first content item from page_1.html (assuming newest item is at the top)
    removed_item = items[0]
    removed_item.extract()
    save_page(page_num, soup)
    print(f"Removed the latest content from page_1.html")

    # Now, for each page, if it has less than MAX_ITEMS, try to shift one item from the next page
    while True:
        current_soup = load_page(page_num)
        current_container = get_content_container(current_soup)
        current_items = current_container.find_all("div", class_="pt-cv-content-item")

        # If current page is full or if there is no next page, break out of the loop.
        if len(current_items) >= MAX_ITEMS:
            break

        next_page_num = page_num + 1
        next_filename = f"page_{next_page_num}.html"
        if not os.path.exists(next_filename):
            # No further pages exist; break out.
            break

        next_soup = load_page(next_page_num)
        next_container = get_content_container(next_soup)
        next_items = next_container.find_all("div", class_="pt-cv-content-item")

        if next_items:
            # Shift the first item from the next page into the end of the current page.
            shifting_item = next_items[0]
            shifting_item.extract()
            current_container.append(shifting_item)
            print(f"Shifted one item from page_{next_page_num}.html to page_{page_num}.html")
            save_page(page_num, current_soup)
            save_page(next_page_num, next_soup)
            # Continue; maybe current page is now full. Otherwise, loop again.
        else:
            # Next page is empty. Remove it and break out.
            os.remove(next_filename)
            print(f"Removed empty page_{next_page_num}.html")
            break

        page_num += 1  # Move to next page and repeat the check

def update_pagination_links(last_page_num):
    """Update the "next" arrow in the pagination area of pages 1..last_page_num to reference the new last page."""
    for page_num in range(1, last_page_num + 1):
        filename = f"page_{page_num}.html"
        if not os.path.exists(filename):
            continue
        with open(filename, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        wrapper = soup.find("div", class_="pt-cv-pagination-wrapper")
        if wrapper:
            # Find the next arrow (assumed to be an <a> with role="button" and text that is › or similar)
            next_link = None
            for a in wrapper.find_all("a", role="button"):
                if a.get_text(strip=True) in ("›", "&rsaquo;", "›"):
                    next_link = a
                    break
            if next_link:
                next_link["onclick"] = f"loadContent('./page_{last_page_num}.html')"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(str(soup))

def determine_last_page():
    """Determine the highest numbered page file (page_#.html) in the current directory."""
    page = 1
    while os.path.exists(f"page_{page+1}.html"):
        page += 1
    return page

# ===== Example usage =====

remove_latest_content()

last_page = determine_last_page()
update_pagination_links(last_page)

print(f"Removal complete. Last page is now page_{last_page}.html.")

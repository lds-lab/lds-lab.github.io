import os
from bs4 import BeautifulSoup

MAX_ITEMS = 5  # Maximum number of content items allowed per page
#need editing
def load_page(page_num):
    """Load and parse page_{page_num}.html. If it doesn't exist, create a new minimal page."""
    filename = f"page_{page_num}.html"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    else:
        # Create a new page structure with the expected container.
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Page {page_num}</title>
</head>
<body>
  <!-- This container is used for content items -->
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
    """Save the modified soup to page_{page_num}.html."""
    filename = f"page_{page_num}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(soup))

def get_content_container(soup):
    """Locate (or create) the container that holds the content items.
       In this version, we use the div with data-id="pt-cv-page-1". """
    container = soup.find("div", {"data-id": "pt-cv-page-1"})
    if container is None:
        # If not found, create it and insert it at the beginning of <body>
        container = soup.new_tag("div", **{"data-id": "pt-cv-page-1", "class": "pt-cv-page", "data-cvc": "1"})
        if soup.body:
            soup.body.insert(0, container)
        else:
            soup.append(container)
    return container

def insert_new_content(new_content_html):
    """
    Insert the new content item at the beginning of page_1.html's container.
    If the container exceeds MAX_ITEMS, remove the last item and shift it to the next page,
    repeating this process until no overflow remains.
    """
    # Parse the new content as a BeautifulSoup fragment
    new_item = BeautifulSoup(new_content_html, "html.parser")
    page_num = 1
    new_to_insert = new_item

    while True:
        soup = load_page(page_num)
        container = get_content_container(soup)

        # Insert the new item at the beginning of the container
        container.insert(0, new_to_insert)

        # Find all content items within this container
        items = container.find_all("div", class_="pt-cv-content-item")
        if len(items) > MAX_ITEMS:
            # Remove the last item (overflow) and prepare it to be shifted to the next page
            overflow_item = items[-1]
            overflow_item.extract()  # Remove it from the current container
            new_to_insert = BeautifulSoup(str(overflow_item), "html.parser")
        else:
            new_to_insert = None

        save_page(page_num, soup)

        if new_to_insert:
            page_num += 1  # Continue shifting to the next page
        else:
            break

def update_pagination_links(last_page_num):
    """
    Update the "next" arrow link in the pagination area of all page files (1 to last_page_num)
    so that it points to the newest (last) page.
    """
    for page_num in range(1, last_page_num + 1):
        filename = f"page_{page_num}.html"
        if not os.path.exists(filename):
            continue
        with open(filename, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        wrapper = soup.find("div", class_="pt-cv-pagination-wrapper")
        if wrapper:
            # Find the "next" button (here we assume it is the <a> with role="button" and text containing ›)
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

# New content snippet to insert (adjust this HTML snippet as needed)
new_content_html = '''
<div class="col-md-12 col-sm-12 col-xs-12 pt-cv-content-item pt-cv-2-col">
  <div class="pt-cv-ifield">
    <a href="./../icra-distributionally-robust-optimization-with-unscented-transform-for-learning-based-control/" 
       class="_self pt-cv-href-thumbnail pt-cv-thumb-right" target="_self">
      <img loading="lazy" decoding="async" width="1084" height="648" 
           src="./../wp-content/uploads/2023/03/Screen-Shot-2023-03-23-at-3.09.31-PM.jpg" 
           class="pt-cv-thumbnail img-none pull-right" alt="" />
    </a>
    <h4 class="pt-cv-title">
      <a href="./../icra-distributionally-robust-optimization-with-unscented-transform-for-learning-based-control/" 
         class="_self" target="_self">
        [ICRA] Distributionally robust optimization with unscented transform for learning-based control
      </a>
    </h4>
    <div class="pt-cv-meta-fields">
      <span class="entry-date">
        <time datetime="2023-03-23T15:09:53+09:00">March 23, 2023</time>
      </span>
    </div>
    <div class="pt-cv-content">HELLO HELLO</div>
  </div>
</div>
'''

# Insert the new content and shift overflow items
insert_new_content(new_content_html)

# Determine the current last page after shifting/insertion
last_page = determine_last_page()

# Update pagination next button links in all page files
update_pagination_links(last_page)

print(f"New content inserted. Last page is now page_{last_page}.html.")

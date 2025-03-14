import os
from bs4 import BeautifulSoup, NavigableString
from datetime import datetime

# Folders to exclude when scanning immediate subdirectories, now including "Publications"
EXCLUDED_DIRS = {"News", "Alumni", "Current Members", "Teaching", "Contact", "Publications"}

def truncate_text(text, max_words=36):
    """
    Truncates the text to max_words words, appending a trailing ellipsis ("...") 
    if the text exceeds the limit.
    """
    words = text.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + " ..."
    return text

def process_paragraph(p):
    """
    Processes a <p> tag so that when encountering a <br> tag, 
    a full stop is added (if the preceding text doesn't already end with punctuation).
    Returns the processed text.
    """
    parts = []
    for child in p.children:
        if child.name == "br":
            # When a <br> is found, check if the last part ends with punctuation.
            if parts and parts[-1] and parts[-1][-1] not in ".?!":
                parts[-1] = parts[-1].rstrip() + "."
            # Append a space to separate sentences.
            parts.append(" ")
        else:
            # If it's a NavigableString or Tag, get its text.
            text = child.get_text(strip=True) if hasattr(child, "get_text") else str(child).strip()
            parts.append(text)
    full_text = " ".join(parts).strip()
    return full_text

def process_html_file(filepath):
    """
    Parses a full-article HTML file and extracts:
      - Title (from a <h3> inside a container like "sub-custom-col" or fallback from <h1>).
      - Publication date text from a <span class="meta-date date updated custom10">.
      - Excerpt text (by processing <p> tags inside a container with class "content-inner" so that 
        line breaks become sentence separators).
      - Image attributes (from an <img> tag inside a container with class "post-featured-img").
      
    Also, it parses the date text (expected in the format "%B %d, %Y") into a datetime object for sorting.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # Look for the main container (e.g. a div with class "container-wrap")
    container = soup.find('div', class_=lambda c: c and 'container-wrap' in c)
    if not container:
        return None

    # --- Extract Title ---
    title = ""
    sub_custom = container.find('div', class_=lambda c: c and 'sub-custom-col' in c)
    if sub_custom:
        h3 = sub_custom.find('h3')
        if h3:
            title = h3.get_text()  # Use title as-is
    if not title:
        h1 = container.find('h1')
        if h1:
            title = h1.get_text()
    if not title:
        return None  # Skip file if no title is found

    # --- Extract Date from the specified <span> ---
    date_span = container.find('span', class_="meta-date date updated custom10")
    if date_span:
        date_text = date_span.get_text(strip=True)
        datetime_attr = date_text  # Using date_text as the datetime attribute
    else:
        date_text = ""
        datetime_attr = ""

    # Parse the date text using the expected format ("%B %d, %Y")
    try:
        date_obj = datetime.strptime(date_text, "%B %d, %Y")
    except Exception:
        date_obj = datetime.min

    # --- Extract Excerpt ---
    excerpt = ""
    excerpt_div = container.find('div', class_=lambda c: c and 'content-inner' in c)
    if excerpt_div:
        paragraphs = excerpt_div.find_all('p')
        excerpt = " ".join(process_paragraph(p) for p in paragraphs)
    
    # --- Extract Image Attributes ---
    img_attrs = {}
    img_span = container.find('span', class_=lambda c: c and 'post-featured-img' in c)
    if img_span:
        img_tag = img_span.find('img')
        if img_tag:
            img_attrs['src'] = img_tag.get('src', '')
            img_attrs['srcset'] = img_tag.get('srcset', '')
            img_attrs['alt'] = img_tag.get('alt', '')
            img_attrs['height'] = img_tag.get('height', '')
            img_attrs['width'] = img_tag.get('width', '')
            img_attrs['sizes'] = img_tag.get('sizes', '')
            img_attrs['decoding'] = img_tag.get('decoding', 'async')
            if img_tag.get('loading'):
                img_attrs['loading'] = img_tag.get('loading')

    return {
        "title": title,
        "date_text": date_text,
        "datetime_attr": datetime_attr,
        "excerpt": excerpt,
        "img_attrs": img_attrs,
        "date_obj": date_obj  # For sorting purposes
    }

def generate_card(data, folder_name):
    """
    Builds an HTML card snippet using the extracted data.
    The link (href) points to the folder where the HTML file was found in the format "./../folder_name/".
    The excerpt is truncated to 36 words with a trailing ellipsis if necessary.
    """
    href = f"./../{folder_name}/"
    
    # Build the image tag based on available attributes
    img = data.get("img_attrs", {})
    img_tag = f'<img alt="{img.get("alt", "")}" class="pt-cv-thumbnail img-none pull-right" decoding="{img.get("decoding", "async")}"'
    if img.get("height"):
        img_tag += f' height="{img.get("height")}"'
    if img.get("loading"):
        img_tag += f' loading="{img.get("loading")}"'
    if img.get("sizes"):
        img_tag += f' sizes="{img.get("sizes")}"'
    if img.get("src"):
        img_tag += f' src="{img.get("src")}"'
    if img.get("srcset"):
        img_tag += f' srcset="{img.get("srcset")}"'
    if img.get("width"):
        img_tag += f' width="{img.get("width")}"'
    img_tag += "/>"

    # Truncate excerpt to 36 words if necessary
    truncated_excerpt = truncate_text(data["excerpt"], max_words=36)

    card_html = (
        f'<div class="col-md-12 col-sm-12 col-xs-12 pt-cv-content-item pt-cv-2-col">\n'
        f'  <div class="pt-cv-ifield">\n'
        f'    <a class="_self pt-cv-href-thumbnail pt-cv-thumb-right" href="{href}" target="_self">\n'
        f'      {img_tag}\n'
        f'    </a>\n'
        f'    <h4 class="pt-cv-title">\n'
        f'      <a class="_self" href="{href}" target="_self">{data["title"]}</a>\n'
        f'    </h4>\n'
        f'    <div class="pt-cv-meta-fields">\n'
        f'      <span class="entry-date">\n'
        f'        <time datetime="{data["datetime_attr"] if data["datetime_attr"] else data["date_text"]}">{data["date_text"]}</time>\n'
        f'      </span>\n'
        f'    </div>\n'
        f'    <div class="pt-cv-content">\n'
        f'      {truncated_excerpt}\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</div>'
    )
    return card_html

def main():
    base_dir = os.getcwd()
    extracted_items = []  # List to store tuples of (data, folder_name)

    # Scan immediate subdirectories (skipping the excluded ones)
    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if os.path.isdir(folder_path) and folder not in EXCLUDED_DIRS:
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(('.html', '.htm')):
                    filepath = os.path.join(folder_path, filename)
                    data = process_html_file(filepath)
                    if data:
                        extracted_items.append((data, folder))
    
    # Sort extracted items by date (using the parsed date from date_text)
    sorted_items = sorted(extracted_items, key=lambda x: x[0]["date_obj"])
    
    # Generate card HTML for each sorted item
    cards = [generate_card(data, folder) for data, folder in sorted_items]
    
    # Build a Python list literal where each card is enclosed in triple quotes
    cards_array_str = "cards = [\n" + ",\n".join("'''{}'''".format(card) for card in cards) + "\n]\n"
    
    output_file = "extracted_cards_array.py"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cards_array_str)
    
    print(f"Extracted {len(cards)} card(s). Output written to {output_file}")

if __name__ == "__main__":
    main()

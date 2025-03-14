import os
from bs4 import BeautifulSoup

def determine_last_page():
    """Determine the highest numbered page file (page_#.html) in the current directory."""
    page = 1
    while os.path.exists(f"page_{page+1}.html"):
        page += 1
    return page

def build_page_numbers(current, total):
    """
    Build a list representing the page numbers (and ellipsis placeholders) for pagination.

    Rules:
      - If total <= 5: list all pages.
      - If current is 1 or 2: show [1, 2, 3, "…", total].
      - If current is 3: show [1, 2, 3, 4, "…", total].
      - If current is near the end (i.e. current >= total - 1): show [1, "…", total-2, total-1, total].
      - Otherwise: show [1, "…", current-1, current, current+1, "…", total].
    """
    if total <= 5:
        return list(range(1, total+1))
    if current <= 2:
        return [1, 2, 3, "...", total]
    elif current == 3:
        return [1, 2, 3, 4, "...", total]
    elif current >= total - 1:
        return [1, "...", total-2, total-1, total]
    else:
        return [1, "...", current-1, current, current+1, "...", total]

def update_pagination_for_page(current, total):
    """Update the pagination block in page_{current}.html based on the current page and total pages."""
    filename = f"page_{current}.html"
    if not os.path.exists(filename):
        print(f"{filename} does not exist. Skipping.")
        return

    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Create a new <ul> for pagination.
    ul = soup.new_tag("ul", **{
        "class": "pt-cv-pagination pt-cv-normal pagination",
        "data-totalpages": str(total),
        "data-currentpage": str(current)
    })

    # Add a left arrow if current page is not the first.
    if current > 1:
        li_prev = soup.new_tag("li")
        a_prev = soup.new_tag("a", role="button")
        a_prev.string = "‹"
        a_prev["onclick"] = f"loadContent('./page_{current-1}.html')"
        li_prev.append(a_prev)
        ul.append(li_prev)

    # Build the page number items.
    page_items = build_page_numbers(current, total)
    for item in page_items:
        li = soup.new_tag("li")
        a = soup.new_tag("a", role="button")
        if item == "...":
            a.string = "…"
            # No onclick for ellipsis.
        else:
            a.string = str(item)
            a["onclick"] = f"loadContent('./page_{item}.html')"
            if item == current:
                li["class"] = "active"
        li.append(a)
        ul.append(li)

    # Add a right arrow if current page is not the last.
    if current < total:
        li_next = soup.new_tag("li")
        a_next = soup.new_tag("a", role="button")
        a_next.string = "›"
        a_next["onclick"] = f"loadContent('./page_{current+1}.html')"
        li_next.append(a_next)
        ul.append(li_next)

    # Replace the old pagination block with the new one.
    wrapper = soup.find("div", class_="pt-cv-pagination-wrapper")
    if wrapper:
        old_ul = wrapper.find("ul", class_="pt-cv-pagination")
        if old_ul:
            old_ul.replace_with(ul)
        else:
            wrapper.append(ul)
    else:
        # If no wrapper exists, create one.
        new_wrapper = soup.new_tag("div", **{"class": "pt-cv-pagination-wrapper"})
        new_wrapper.append(ul)
        if soup.body:
            soup.body.append(new_wrapper)
        else:
            soup.append(new_wrapper)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(soup))
    print(f"Updated pagination in {filename}.")

def update_all_pagination():
    """Update pagination for all page files based on the total number of pages."""
    total = determine_last_page()
    for current in range(1, total+1):
        update_pagination_for_page(current, total)

if __name__ == "__main__":
    update_all_pagination()
    print("Pagination update complete.")

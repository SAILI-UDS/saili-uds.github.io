# import os
# from scholarly import scholarly
# import bibtexparser
# from bibtexparser.bwriter import BibTexWriter
# from bibtexparser.bibdatabase import BibDatabase
# import re

# SCHOLAR_USER_ID = "YSrvU5AAAAAJ"  # Replace this with your actual user ID
# BIB_FILE = "_bibliography/papers.bib"

# def slugify(text):
#     return re.sub(r'\W+', '', text.lower())

# def read_existing_titles(bib_file_path):
#     if not os.path.exists(bib_file_path):
#         return set()
#     with open(bib_file_path, 'r', encoding='utf-8') as f:
#         bib_database = bibtexparser.load(f)
#         return set(entry.get("title", "").strip().lower() for entry in bib_database.entries)

# def fetch_new_publications(user_id, existing_titles):
#     print(f"Fetching publications for user ID: {user_id}")
#     try:
#         author = scholarly.search_author_id(user_id)
#         author = scholarly.fill(author, sections=["publications"])
#     except Exception as e:
#         print(f"Error fetching author profile: {e}")
#         return []

#     new_entries = []
#     for idx, pub in enumerate(author.get("publications", [])):
#         try:
#             filled_pub = scholarly.fill(pub)
#             bib_data = filled_pub.get("bib", {})
#             pub_title = bib_data.get("title", "").strip().lower()

#             if not pub_title or pub_title in existing_titles:
#                 print(f"Skipping existing or empty title: {bib_data.get('title', 'Unknown Title')}")
#                 continue

#             # Ensure required BibTeX fields
#             bib_data["ENTRYTYPE"] = "article"
#             year = bib_data.get("year", "n.d.")
#             author_lastname = bib_data.get("author", "unknown").split(",")[0].split()[-1].lower()
#             bib_data["ID"] = f"{author_lastname}{year}{slugify(bib_data.get('title', '')[:20])}"

#             new_entries.append(bib_data)
#             print(f"New publication found: {bib_data.get('title')}")

#         except Exception as e:
#             print(f"Failed to fetch publication #{idx}: {e}")

#     return new_entries

# def save_new_entries_to_bib(new_entries, output_file):
#     if not new_entries:
#         print("No new publications to add.")
#         return

#     db = BibDatabase()
#     db.entries = new_entries
#     writer = BibTexWriter()
#     writer.indent = '    '

#     with open(output_file, "a", encoding="utf-8") as f:
#         f.write(writer.write(db))

#     print(f"Appended {len(new_entries)} new entries to {output_file}")

# def main():
#     existing_titles = read_existing_titles(BIB_FILE)
#     new_entries = fetch_new_publications(SCHOLAR_USER_ID, existing_titles)
#     save_new_entries_to_bib(new_entries, BIB_FILE)

# if __name__ == "__main__":
#     main()


import os
import re
from scholarly import scholarly
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

# ====== HARDCODE YOUR GOOGLE SCHOLAR USER ID HERE ======
SCHOLAR_USER_ID = "YSrvU5AAAAAJ"  # Replace this with your actual user ID
BIB_FILE = "_bibliography/papers.bib"

def read_existing_titles(bib_file_path):
    if not os.path.exists(bib_file_path):
        return set()
    with open(bib_file_path, 'r', encoding='utf-8') as f:
        bib_database = bibtexparser.load(f)
        return set(entry.get("title", "").strip().lower() for entry in bib_database.entries)

def make_citation_key(title, author, year):
    # Create a sanitized citation key: lastnameYYYYfirstword
    if not title or not author or not year:
        return None
    first_author = author.split(" and ")[0].split()[-1]
    title_token = re.sub(r'\W+', '', title.split()[0].lower())
    return f"{first_author.lower()}{year}{title_token}"

def convert_to_bibtex_entry(pub):
    bib = pub.get("bib", {})
    
    # Extract and clean required fields
    title = str(bib.get("title", "")).strip()
    author = str(bib.get("author", "")).strip()
    year = str(bib.get("pub_year", "")).strip() or str(bib.get("year", "")).strip()
    
    # Try multiple sources for venue information
    venue = (str(bib.get("journal", "")).strip() or 
             str(bib.get("venue", "")).strip() or 
             str(bib.get("booktitle", "")).strip() or
             str(bib.get("publisher", "")).strip() or
             str(bib.get("conference", "")).strip())
    
    url = str(pub.get("pub_url", "")).strip()

    # Skip entries without essential information
    if not title or not author or not year:
        return None

    citation_key = make_citation_key(title, author, year)

    # Create BibTeX entry with all required fields
    bib_entry = {
        "ENTRYTYPE": "article",
        "ID": citation_key or re.sub(r'\W+', '', title.lower())[:20],
        "title": title,
        "author": author,
        "year": year,
        "journal": venue,
        "url": url,
        "html": url,  # For website linking
        "bibtex_show": "true",  # Show BibTeX entry
        "selected": "true",  # Show in selected publications
    }
    
    # Clean up empty fields
    bib_entry = {k: v for k, v in bib_entry.items() if v}

    return bib_entry

def fetch_new_publications(user_id, existing_titles):
    print(f"Fetching publications for user ID: {user_id}")
    try:
        author = scholarly.search_author_id(user_id)
        author = scholarly.fill(author, sections=["publications"])
    except Exception as e:
        print(f"Error fetching author profile: {e}")
        return []

    entries = []
    for idx, pub in enumerate(author.get("publications", [])):
        try:
            filled_pub = scholarly.fill(pub)
            bib_data = filled_pub.get("bib", {})
            pub_title = bib_data.get("title", "").strip().lower()

            # Convert every publication to ensure proper formatting
            bib_entry = convert_to_bibtex_entry(filled_pub)
            if bib_entry:
                entries.append(bib_entry)
                if pub_title not in existing_titles:
                    print(f"Added new publication: {bib_entry['title']}")
                else:
                    print(f"Updated existing: {bib_entry['title']}")

        except Exception as e:
            print(f"Failed to fetch publication #{idx}: {e}")

    return entries

def save_new_entries_to_bib(entries, output_file):
    if not entries:
        print("No publications to save.")
        return

    # Add YAML front matter
    yaml_front_matter = """---
---

"""

    db = BibDatabase()
    db.entries = entries
    writer = BibTexWriter()
    writer.indent = '    '
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(yaml_front_matter)
        f.write(writer.write(db))

    print(f"Saved {len(entries)} entries to {output_file}")

def main():
    existing_titles = read_existing_titles(BIB_FILE)
    new_entries = fetch_new_publications(SCHOLAR_USER_ID, existing_titles)
    save_new_entries_to_bib(new_entries, BIB_FILE)

if __name__ == "__main__":
    main()

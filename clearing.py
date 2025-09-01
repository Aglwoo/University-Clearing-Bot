import requests
from bs4 import BeautifulSoup
import os
import re
import time

top_universities = [
    "university-of-bath","london-school-of-economics", "university-college-london-university-of-london", "kings-college-london-university-of-london",
    "university-of-warwick", "university-of-edinburgh", 
    "university-of-bristol", "university-of-durham", "university-of-nottingham",
    "university-of-birmingham", "university-of-manchester", "university-of-exeter", "university-of-southampton"
]

subject_keywords = {
    'Physics': ['Physics', 'Astrophysics', 'Quantum', 'Space Science'],
    'Computer Science': ['Computer Science', 'Software Engineering', 'Artificial Intelligence', 'Data Science','Compute'],
    'Economics': ['Economics', 'Business Economics', 'International Economics'],
    'Mathematics': ['Mathematics', 'Operational Research', 'Statistics'],
    'Engineering': ['Engineering']
}

for subject in subject_keywords:
    os.makedirs(subject, exist_ok=True)

base_url_template = "https://www.thecompleteuniversityguide.co.uk/clearing/courses/university-search/undergraduate/all/{}?coursetype=full-time&pg={}"

def matches_subject_keywords(title):
    for subject, keywords in subject_keywords.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', title, re.IGNORECASE):
                return subject
    return None

def scrape_university(univ_url_name):
    page = 1
    stop_message = "Sorry there don’t seem to be any results matching your search"
    while True:
        url = base_url_template.format(univ_url_name, page)
        print(f"Scraping {url}")
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Page {page} for {univ_url_name} returned status {resp.status_code}, stopping pagination.")
            break

        soup = BeautifulSoup(resp.text, 'html.parser')

        if stop_message.lower() in soup.get_text(separator=' ').lower():
            print(f"Stop message found on page {page} for {univ_url_name}. Ending pagination.")
            break

        course_links = soup.find_all('a', href=re.compile(r"^/clearing/courses/details/"))
        print(f"Found {len(course_links)} course links on page {page} for {univ_url_name}")

        for link in course_links:
            title = link.get_text(strip=True)
            course_url = "https://www.thecompleteuniversityguide.co.uk" + link['href']

            subject = matches_subject_keywords(title)
            if subject:
                filename = os.path.join(subject, f"{univ_url_name}.txt")
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write(f"{title}\n{course_url}\n\n")
                print(f"Saved offer: {title} under {subject}")

        page += 1
        #time.sleep(1)
        #run if you care about rate limiting (in my experience it isnt needed)

def main():
    for univ in top_universities:
        scrape_university(univ)

if __name__ == "__main__":
    main()

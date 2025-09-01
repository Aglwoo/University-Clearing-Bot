import requests
from bs4 import BeautifulSoup
import os
import re
import time
from lxml import html
#little fix i am trying to add to get ucas points needed currently not working
top_universities = [
    "university-of-oxford", "university-of-cambridge", "imperial-college-london",
    "london-school-of-economics", "university-college-london", "university-of-st-andrews",
    "university-of-warwick", "university-of-edinburgh", "university-of-york",
    "university-of-bristol", "university-of-durham", "university-of-nottingham",
    "university-of-birmingham", "university-of-leeds", "university-of-sheffield",
    "university-of-glasgow", "university-of-exeter", "university-of-southampton",
    "queens-university-belfast", "university-of-essex"
]

subject_keywords = {
    'Physics': ['Physics', 'Astrophysics', 'Quantum', 'Space Science'],
    'Computer Science': ['Computer Science', 'Software Engineering', 'Artificial Intelligence', 'Data Science'],
    'Economics': ['Economics', 'Business Economics', 'International Economics'],
    'Mathematics': ['Mathematics', 'Operational Research', 'Statistics'],
    'Engineering': ['Engineering', 'Mechanical Engineering', 'Civil Engineering', 'Electrical Engineering']
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

def get_ucas_points(course_url):
    resp = requests.get(course_url)
    if resp.status_code != 200:
        print(f"Failed to get course details from {course_url}")
        return "N/A"
    
    soup = BeautifulSoup(resp.content, 'html.parser')
    

    ucas_labels = soup.find_all('p', string=lambda text: text and 'ucas points' in text.lower())
    for label in ucas_labels:
        next_p = label.find_next_sibling('p')
        if next_p:
            return next_p.get_text(strip=True)
    return "Not found"


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
                ucas_points = get_ucas_points(course_url)
                filename = os.path.join(subject, f"{univ_url_name}.txt")
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write(f"{title}\n{course_url}\nUCAS Points: {ucas_points}\n\n")
                print(f"Saved offer: {title} under {subject} with UCAS points: {ucas_points}")

        page += 1
        #time.sleep(1)


def main():
    for univ in top_universities:
        scrape_university(univ)

if __name__ == "__main__":
    main()

from tika import parser 
import regex as re
import string
import os

def main(url = False):
    """
    1. Extracts contents of PDF into XML format.
    2. Splits into paragraphs using recognition of <p> tags. This overcomes line- and page-breaks.
    3. Write to file. 

    Currently, this will incude odd data read from Tika like plot axis labels and legends.
        This is combated by removing paragraphs with length less than 100 characters
    """
    if url:
        raw = parser.from_file(url, xmlContent=True)
    else: 
        raw = parser.from_file('data\mark-billinghurst-data\sample.pdf', xmlContent=True)

    # Remove non ASCII characters
    printables = set(string.printable)
    text = "".join(filter(lambda x: x in printables, raw['content']))

    # Replace tabs with spaces
    text = re.sub(r"\t+", r" ", text)

    # Extract paragraphs of content
    matches, title = extract_content_within_p_tags(text)
    if title != 0:
        # The title can't be too long bc windows bugs out -_-
        name = re.sub(r"\s", "_", title)[0:30]
    else:
        name = re.sub(r"\s", "_", matches[0][:30])

    print(name)
    write_strings_to_file(matches, name, f'data\\mark-billinghurst-data\\outputs\\{name}.txt')

def extract_content_within_p_tags(string):
    """
    Returns list where each entry is one paragraph (or reference)

    Also filters out double spaces and split-line words. 
        GPT-3 seems capable of recognizing incorrectly un-hyphenated words.
    """
    pattern = r'<title>(.*?)</title>'
    match = re.search(pattern, string)

    if len(match)>10:
        title = match.group(1)
    else:
        title = 0

    pattern = r'<p>(.*?)</p>'
    string = re.sub(r'\n(?!\n)', ' ', string)
    matches = re.findall(pattern, string, re.DOTALL)
    # filtered_matches = [match for match in matches if len(match) > 100]

    ### Multiple periods and 
    filtered_matches = [re.sub(r'\s*-\s*', '', re.sub(r"\s+", " ", match)) for match in matches if len(match) > 100]

    return filtered_matches, title

    
def write_string_to_file(string, file_path):
    with open(file_path, 'w') as file:
        file.write(string)

def write_strings_to_file(strings, title, file_path):
    with open(file_path, 'w') as file:
        file.write(title + '\n')
        for string in strings:
            file.write(string + '\n')

# Read the URLs from a file
def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        urls = file.read().splitlines()
    return urls

# Search folder for PDF files and process each file
def search_and_process_pdf_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".pdf"):
                file_path = os.path.join(root, file)
                main(file_path)

# def clean_text(self):
#     """ Extract & clean sentences from raw text of pdf. """
#     # Remove non ASCII characters
#     printables = set(string.printable)
#     self.text = "".join(filter(lambda x: x in printables, self.text))

#     # Replace tabs with spaces
#     self.text = re.sub(r"\t+", r" ", self.text)

#     # Aggregate lines where the sentence wraps
#     fragments = []
#     prev = ""
#     for line in re.split(r"\n+", self.text):
#         if line and (line.startswith(" ") or line[0].islower()
#               or not prev.endswith(".")):
#             prev = f"{prev} {line}"  # make into one line
#         else:
#             fragments.append(prev)
#             prev = line
#     fragments.append(prev)

#     # Clean the lines into sentences
#     sentences = []
#     for line in fragments:
#         # Use regular expressions to clean text
#         url_str = (r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\."
#                    r"([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*")
#         line = re.sub(url_str, r" ", line)  # URLs
#         line = re.sub(r"^\s?\d+(.*)$", r"\1", line)  # headers
#         line = re.sub(r"\d{5,}", r" ", line)  # figures
#         line = re.sub(r"\.+", ".", line)  # multiple periods
        
#         line = line.strip()  # leading & trailing spaces
#         line = re.sub(r"\s+", " ", line)  # multiple spaces
#         line = re.sub(r"\s?([,:;\.])", r"\1", line)  # punctuation spaces
#         line = re.sub(r"\s?-\s?", "-", line)  # split-line words

#         # Use nltk to split the line into sentences
#         for sentence in nltk.sent_tokenize(line):
#             s = str(sentence).strip().lower()  # lower case
#             # Exclude tables of contents and short sentences
#             if "table of contents" not in s and len(s) > 5:
#                 sentences.append(s)
#     return sentences

    
if __name__ == '__main__':   

    # Process remote PDF files
    if 0:
        file_path = 'data\mark-billinghurst-data\pdfs.txt'
        hyperlinks = read_urls_from_file(file_path)

        for lurl in hyperlinks:
            try:
                main(lurl)
            except:
                print(f'{lurl} failed')

    # Process local PDF files
    if 1:
        folder_path = "data\mark-billinghurst-data\pdf_files"

        # Search folder for PDF files and process each file
        search_and_process_pdf_files(folder_path)

    url = 'https://jnnp.bmj.com/content/jnnp/94/7/499.full.pdf'
    main(url)

    # pp = parsePDF(url)
    # pp.extract_contents()
    # sentences = pp.clean_text()
    # write_strings_to_file(sentences, 'data\mark-billinghurst-data\sample.txt')
    # pass

 
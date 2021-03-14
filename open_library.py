import requests
import os
import json

# https://openlibrary.org/developers/api

book_data_folder = os.path.join(os.getcwd(), 'Book Data')
book_cover_folder = os.path.join(os.getcwd(), 'Book Covers')
for folder in [book_data_folder, book_cover_folder]:
    if not os.path.exists(folder):
        os.mkdir(folder)


def book_data(search_term: str, author: str = '', save_data: bool = True):
    url_base = 'http://openlibrary.org/'
    parameters = {'q': search_term.replace(' ', '+')}
    r = requests.get(url_base + 'search.json', params=parameters)
    jr = r.json()
    if author != '':
        for bk in jr['docs']:
            if bk.get('author_name', [''])[0].lower() == author:
                book = bk
    else:
        book = jr['docs'][0]
    if save_data:
        with open(os.path.join(book_data_folder, book.get('title') + '.json'), 'w') as f:
            json.dump(book, f)
    return book


def book_cover(book: dict, save_image: bool = True):
    url_img_base = 'http://covers.openlibrary.org/'
    url_img = f"{url_img_base}b/id/{str(book.get('cover_i'))}-L.jpg"
    r_img = requests.get(url_img)
    if save_image:
        with open(os.path.join(book_cover_folder, book.get('title') + '.jpg'), 'wb') as f:
            f.write(r_img.content)


if __name__ == '__main__':
    book = book_data(search_term='a gentleman in moscow', author='amor towles')
    book_cover(book)

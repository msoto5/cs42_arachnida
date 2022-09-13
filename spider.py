# Import libraries
import argparse
import os
import requests                     
from bs4 import BeautifulSoup
from progress.bar import Bar
import re
import json
from urllib.parse import urljoin, urlparse, ParseResult
import urllib
import validators
import posixpath


def leer_argumentos():
    """
    Declares arguments and returns them
    
    Returns:
        string (website URL)
        bool (True if recursive).
        int (recursion depth limit). Defaut value: 5
        string (path where images have to be stored). Default value: './data/'
    """
    parser = argparse.ArgumentParser(
        description= "Spider extracts all website (URL) images. It is recursived and it can extract the images from subpages with a limited recursive depth."
        )
    
    # Argument 1: website URL (required) (string)
    parser.add_argument(
        "URL",
        help="Website's url where the images will be downloaded."
        )
    
    # Argument 2: Recursive (bool)
    parser.add_argument(
        "-r", "--recursive",
        help="it enables the recursion attribute and downloads images from website and subpages. Its depth limit is established by -l FLAG",
        action = "store_true"
        )
    
    # Argument 3: Recursion depth limit (int). Default value: 5
    parser.add_argument(
        "-l", "--limit",
        help="recursion depth limit. Defaut value: 5. If it -r is not called this flag does nothing.",
        default=5, type=int
        )
    
    # Argument 4: Path where images will be stored (string). Default value: './data/'
    parser.add_argument(
        "-p", "--path",
        help="path where images will be downloaded. Default value: './data/'.",
        default="./data"
        )
    
    arg = parser.parse_args()

    # Returns arguments values
    return arg.URL, arg.recursive, arg.limit, arg.path

def print_dict(mydict):

    print("{:<60} {:<10}". format('URL', 'STATUS'))
    for urld, statusd in mydict.items():
        print("{:<30} {:<10}".format(urld, statusd))

def download_requests(name, url):
    """
    Download an image from its URL.

    Args:
        name: Image's name
        url: Image's URL, where from it will be downloaded
        
    Returns:
        1 if it is downloaded correctly or 0 otherwise.
    """

    # Check if image allready is downloaded
    if not os.path.exists(name):
        # Make the requests to obtain webpage info
        r = requests.get(url)

        # Check is url is the one of an image and the requests was succesful
        if "image" in r.headers['content-type'] and r.status_code == 200:

            # Create file and save image. Open a local file with wb (write binary) permission.
            with open(name, 'wb') as handler:
                handler.write(r.content)

                # Downloaded succesfully
                return 1

    # Image not downloaded
    return 0


def mget_imgs(soup, website_url, path, images_format = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
    """
    Obtain and download an all images from website.
    
    It only downloads images with format in images_format. Default images_format: ('.jpg', '.jpeg', '.png', '.gif', '.bmp').

    Args:
        soup: website html parsed with BeautifulSoup.
        website_url: string with website's url from where images are downloaded.
        path: path where images will be stored.
        images_format: Accepted images format.
    
    Returns:
        (int) total number of downloaded images
        (int) total number of images that couldn't be downloaded. 
    """

    # Find all images in website from parsed html
    soup_img = soup.find_all('img')

    # Create a dynamic loading bar in terminal
    bar = Bar("Comprobando posibles imagenes...", max=len(soup_img))
    
    # Initialize downloaded images counter
    k = 0

    # Loop to iter through every possible image
    for item in soup_img:
        bar.next()

        # Check if item['src'] (image url to be downloaded) ends with image format.
        if item['src'].endswith(images_format):

            # Obtain image url.
            if item['src'].startswith("http"):
                # item['src'] has a complete URL --> we copy it.
                # This makes that we can downloaded images that are stored in other web server but are shown in our website
                image_url = item['src']

            else:
                # item['src'] does not have a complete URL --> we join with website url
                image_url = urljoin(website_url, item['src'])
            
            # Obtain image name. 
            # If '/' is not found it still works as .rfind() returns -1
            image_name = item['src'][item['src'].rfind('/') + 1 : ]

            # Download images and increase counter if they are downloaded
            k += download_requests(path + '/' + image_name, image_url)

    # End dynamic loading bar
    bar.finish()

    # Obtain not downloaded images
    sin_descargar = len(soup_img) - k

    # Returns: downloaded images, not downloaded images
    return k, sin_descargar

def mget_links(soup, website_url):
    """
    Obtains all links within a web page.

    Args:
        soup: website html parsed with BeautifulSoup.
        website_url: string with website's url from where images are downloaded.

    Returns:
        (dictionary) with accepted links found in this website
        (int) total number of possible links (for final resume purpose)
    """

    # Initialize empty list where accepted links will be incluided
    list_links = []

    # Find all referenced link in website from parsed url
    soup_links = soup.find_all("a", href=True)

    # Create a dynamic loading bar in terminal
    bar = Bar("Comprobando posibles subpaginas...", max=len(soup_links))
    
    u_originalwebsite = urlparse(website_url)

    # Loop to iter through every possible link
    for link in soup_links:
        bar.next()
        #print("\n" + link['href'])
        
        u = urlparse(link['href'])
        #print("new_link netloc = " + u.netloc)
        #print("u_original netloc = " + u_originalwebsite.netloc)
        if (re.match("^(www.)?" + u.netloc, u_originalwebsite.netloc) or re.match("^(www.)?" + u_originalwebsite.netloc, u.netloc)) and (u.netloc != "" or u.path != "") and (u.scheme == '' or u.scheme == 'http' or u.scheme == 'https'):
            u2 = ParseResult(u.scheme, u.netloc, u.path, "", "", "").geturl()

            slash = ''
            if not "." in u_originalwebsite.path:
                slash = '/'

            #print("u_original path = " + u_originalwebsite.path)
            #print("u_new path = " + u.path)
            #print("posix = " + posixpath.join(u_originalwebsite.path, u.path))
            #print("urljoin = " + urljoin(u_originalwebsite.geturl(), u.geturl()))
            #print("link que anadimos antes: " + ParseResult(u_originalwebsite.scheme, u_originalwebsite.netloc, posixpath.join(u_originalwebsite.path, u.path), "", "", "").geturl())

            link_url = urljoin(u_originalwebsite.geturl() + slash, u.geturl())
            """
            link_url = urljoin(
                ParseResult(u_originalwebsite.scheme, u_originalwebsite.netloc, 
                    posixpath.join(u_originalwebsite.path, u.path),
                    "", "", "").geturl(),
                u2 + slash)
            """
            list_links.append(link_url)
            #print("La añado")

    bar.finish()

    # Convert list of links to dictionary and define keys as the links and the values as "Not-checked"
    dict_links = dict.fromkeys(list_links, "Not-checked")

    # Return dictionary with links
    return dict_links

def mini_spider(website, path, dict_links, n_limit, headers, n_img = 0):
    """
    Recursive function that downloads images from a web page and its subpages with an specific depth limit.

    Args:
        website: string with website url you want to download the images from
        path: string with the path where images will be stored
        dict_links: dicctionary with 
        n_limit: recursive depth limit. Default value: 1
        headers: requests header
        n_img: (int) total number of images downloaded. Default value: 0

    Returns:
        (int) total number of downloaded images
        (dictionary) with all links and its status
    """

    # The recursive depth limit is reached. It returns input values.
    if n_limit == 0:
        return n_img, dict_links, n_all_links

    # Print some information of current website and recursive depth limit
    print("Web: " + website)
    print(f"Limit: {n_limit} de {limit}")

    # Requests to obtain website information. 
    # Headers are given and stream = True to prevent to be blocked from some pages
    try:
        r = requests.get(website, stream = True, headers = headers, timeout=5)
    except Exception:
        dict_links[website] = "Connection-Error"
        print("Connection Error\n")
        return n_img, dict_links

    print(r.headers['content-type'])

    # Check requests status. If everything is okey r.status_code == 200
    if r.status_code != 200:
        error = "ERROR en la conexion. Status code: " + str(r.status_code)
        print("Connection Error\n")

        # Change website value in dictionary to report error
        dict_links[website] = "Connection-Error"
    
    # Check if webpage is text/html -> this prevents error if, for example, a pdf is included in dictionary with all links
    elif not 'text/html' in r.headers['content-type']:
        error = "URL no es HTML"

        # Change website value in dictionary to report error
        dict_links[website] = "Not-HTML"

    else:
        # Parse the html data. This data cannot be extracted through string processing as is nested.
        # One needs a parser which can create a nested/tree structure of the HTML data -> 'html.parser'
        soup = BeautifulSoup(r.text, 'html.parser')

        # If depth limit is 1 we do not need to obtain website's subpages
        if n_limit > 1:
            # Obtain subpages
            dict_new_links = mget_links(soup, website)
            
            #print_dict(dict_new_links)

            print("Links obtenidos: " + str(len(dict_new_links)))

            # Join together both dictionary with links. The order is important as dict_links values are predominant
            dict_all_links = {**dict_new_links, **dict_links}

        else:
            # Initialized variables created while obtaining new links
            dict_all_links = {}
            dict_new_links = {}
            dict_all_links.update(dict_links)

        # Change website value in dictionary to report it as checked
        dict_all_links[website] = "Checked"
        
        # Download images from current website
        new_img, no_down = mget_imgs(soup, website, path)
        print("Imagenes nuevas descargadas: " + str(new_img))
        print("Imagenes con otro formato: " + str(no_down))
        print("")

        # Update total number of images downloaded & total number of possible links searched
        n_img += new_img

        # Loop that goes through all new links obtained to make the recursive call
        for l in dict_new_links:

            # Checked if link has not been checked already in all link dictionary
            if dict_all_links[l] == "Not-checked":
                n_limit_k = n_limit + 0

                # Recursive call
                n_img, dict_all_links = mini_spider(l, path, dict_all_links, n_limit_k - 1, headers, n_img)
        
        # Returns total downloaded images & dictionary with all links and their satus & total of possible links
        return n_img, dict_all_links
    
    return n_img, dict_links


# MAIN
if __name__ == "__main__":
    # Read arguments
    url, rec, limit, path = leer_argumentos()

    # Checking URL syntax
    if not validators.url(url):
        print("Website URL inserted is not valid")
        exit(1)

    # If path folder does not exist -> it creates it
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except:
            print("ERROR creando carpeta " + path)
            exit(1)

    # Some headers are defined to prevent our requests to be block.
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

    # Create dictionary with all links and include url as "Not-checked"
    dict_links = {url : "Not-checked"}

    # Check if recursion was inserted
    if not rec:
        limit = 1
    
    # Call function that goes recursively through website and downloads its images
    n_img, all_links = mini_spider(url, path, dict_links, limit, headers)

    # Save dictionary with all links as a json file
    a_file = open("data.json", "w")
    json.dump(all_links, a_file)
    a_file.close()
    
    # Print final information in terminal
    print("Numero de imagenes TOTAL descargadas: " + str(n_img))
    print("Numero de ENLACES REVISADOS: " + str(sum(value == "Checked" for value in all_links.values())))
    print("Numero de ENLACES NO HTML: " + str(sum(value == "Not-HTML" for value in all_links.values())))
    print("Numero de ERRORES de CONEXION: " + str(sum(value == "Connection-Error" for value in all_links.values())))
    print("Numero de ENLACES sin REVISAR: " + str(sum(value == "Not-checked" for value in all_links.values())))
    print("")
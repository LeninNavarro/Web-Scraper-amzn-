# import system libraries
import os
import re
from random import randint
from time import sleep
# import external packages with pip/pip3
import pandas as pd
import requests
from bs4 import BeautifulSoup
from ftfy import fix_encoding, fix_text
from fake_useragent import UserAgent


def main(URL):
    #opening dataframe where needed elements will be contained
    df = pd.DataFrame()
    #user_agent: an identity sent by a GET request, along with many other params seen below
    ua = UserAgent()
    #randomizing in order to make it look like it comes from different devices
    uag_rand = ua.random

    HEADERS = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': uag_rand,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'
    }

    webpage = requests.get(URL, headers=HEADERS)

    # Creating the Soup Object containing all data
    souped = BeautifulSoup(webpage.content, "html.parser")
    soup = BeautifulSoup(souped.prettify(), "html.parser")

    # retrieving ASIN-imposibleng wala
    try:
        # retrieve product details table and parse it to string
        prod_deets = str(soup.select('tr > td.prodDetAttrValue'))

        # find ASIN value inside the table with regular expression
        asin_regex = re.search(r"\sB0\w+", prod_deets)

        # remove unnecessary spaces
        asin = asin_regex.group().strip()
    except AttributeError:
        try:
            prod_deets2 = str(soup.select('div[id="detailBulletsWrapper_feature_div"]> div > ul.a-unordered-list'))
            asin_regex2 = re.search(r"\sB0\w+", prod_deets2)
            asin = asin_regex2.group().strip()
        except AttributeError:
            asin = "Not found. Send the html element of this ASIN to be located"
    print("ASIN: " + asin)

    # retrieving main image
    try:
        prod_img = soup.select_one('div#imgTagWrapperId.imgTagWrapper>img[src]')
        image = prod_img.get('src')
    except AttributeError:
        image = "Cannot be scraped"

    # retrieving product title
    try:
        # Outer Tag Object
        title = soup.find("span", attrs={"id": 'productTitle'})

        # Inner NavigableString Object
        title_value = title.string

        # Title as a string value
        title_string = title_value.strip()

    except AttributeError:
        title_string = "NA"

    # product category
    try:
        categori = soup.select_one('div.a-subheader > ul.a-unordered-list').text
        categori = " ".join(categori.split())
        category = fix_text(categori)

    except AttributeError:
        category = 'Cannot be found'

    # retrieving price
    try:
        price = soup.select_one('span.a-price.a-text-price.a-size-medium.apexPriceToPay>span.a-offscreen').text.strip()

    except AttributeError:
        try:
            price = soup.select_one('div#aod-price').text.strip()
        except AttributeError:
            try:
                price = soup.select_one('div.a-fixed-left-grid-col > span.a-price').text.strip().replace('\n', '')
            except AttributeError:
                try:
                    price = soup.select_one(
                        '#corePriceDisplay_desktop_feature_div > div.a-section.a-spacing-none.aok-align-center > span.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay > span.a-offscreen').text.strip().replace(
                        " ", "")
                except:
                    price = "None found. Check buying options"


    # retrieving product rating
    try:
        rating = soup.find("span", attrs={'class': 'a-icon-alt'}).string.strip().replace(',', '')

    except AttributeError:

        try:
            rawRating = soup.select_one('div#averageCustomerReviews').text.strip()
            rating, sep, tail = rawRating.partition(' ')
        except AttributeError:
            rating = 'NA. Check if product is unavailable'

    # number of ratings
    try:
        review_count = soup.find("span", attrs={'id': 'acrCustomerReviewText'}).string.strip().replace(',', '')

    except AttributeError:
        try:
            raw_review_count = soup.select_one('div#averageCustomerReviews').text.strip()
            head, sep, review_count = raw_review_count.partition(' ').replace('out of 5 stars', '').strip()
        except AttributeError:
            review_count = 'NA: Probable-- product unavailable'

    # product Description
    try:
        descSoup = soup.select('div#feature-bullets span.a-list-item')
        del descSoup[0]
        stringedDesc = str(descSoup).replace("</span>", "").replace('<span class="a-list-item">', '').replace('[',
                                                                                                              '').replace(
            ']', '').replace('  ,  ', '\n').replace('<span class="a-list-item a-size-base">', '').strip()
        pDesc = fix_text(stringedDesc).encode('utf-8').decode('utf-8')

    except AttributeError:
        pDesc = "NA"

    # product brand
    try:
        brand = soup.select_one('tr.a-spacing-small.po-brand td.a-span9 span.a-size-base').text.strip()

    except AttributeError:
        try:
            brand = soup.select_one('div.centerColAlign div.a-section.a-spacing-none a.a-link-normal').text.replace(
                "Visit the", '').replace(" Store", "").strip()
        except AttributeError:
            brand = "Not Found"

    # Sold By
    try:
        soldBy = soup.select_one('div.tabular-buybox-text a').text.strip()
    except AttributeError:
        try:
            soldBy = soup.select_one('div.tabular-buybox-text:nth-of-type(4) span.a-size-small').text.strip()

        except AttributeError:
            try:
                soldBy = soup.select_one('span.a-size-small.mbcMerchantName').text.strip()

            except AttributeError:
                soldBy = "No available buybox seller"

    # Coupon
    try:
        coupons = soup.select_one('span.promoPriceBlockMessage > div').text.strip()
        if len(coupons) > 0:
            coupons = "Product has coupon"

    except AttributeError:
        coupons = "No found coupon"

    #putting all the elements inside the called dataframe *.append in pandas is already an outdated method*
    df = df.append(pd.DataFrame(
        {"URL": URL, "ASIN": asin, "Image Link": image, "Full Product Title": title_string, "Category": category,
         "Price": price,
         "Average Rating": rating, "Product Reviews": review_count, "Product Description": fix_encoding(pDesc),
         "Brand": brand,
         "Buybox Seller": soldBy, "Available coupons": coupons}, index=[0]), ignore_index=True)

    output_path = "amazon_scraper.csv"
    # Check if the file exists
    # noinspection PyRedundantParentheses
    if (not os.path.exists(output_path)):
        # Create and append the first data
        df.to_csv(output_path, index=False, encoding='utf-8-sig')  # default write mode
    else:
        # Append the data in the existing file
        df.to_csv(output_path, index=False, mode="a", header=False,
                  encoding='utf-8-sig')  # append mode excluding the header

    delay = randint(60, 87)
    print(str(delay) + ' seconds')
    sleep(delay)


if __name__ == '__main__':
    # opening our url file to access URLs
    file = open("url.txt", "r")

    # iterating over the urls
    for links in file.readlines():
        main(links)
from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import requests
import pymongo
import certifi

application = Flask(__name__)  # instance of flask
app = application


@application.route("/")
@cross_origin()
def home_page():
    return render_template('index.html')


@application.route("/searchresult", methods=["POST"])
@cross_origin()
def DataScrapping():
    if request.method == "POST":
        product_name = request.form['texttosearch'].replace(" ", "")
        # print(f"product name is {product_name}")
        head_url = "https://www.flipkart.com"
        product_url = head_url + "/search?q=" + product_name
        # print(product_url)
        p_url = urlopen(product_url)
        product_url_data = p_url.read()
        p_url.close()
        # print(product_url_data)
        products_html_data = bs(product_url_data, 'html.parser')
        complete_product_data_list = products_html_data.find_all('div', {'class': '_1AtVbE col-12-12'})
        # print(complete_product_data_list)
        # print(len(complete_product_data_list))
        del complete_product_data_list[0:3]
        del complete_product_data_list[-4:]
        # print(len(complete_product_data_list))
        all_review_list = []
        for i in complete_product_data_list:
            try:
                # time.sleep(2)
                items_url = head_url + i.div.div.div.a['href']
                # print(items_url)
                item_data = requests.get(items_url)
                item_html_data = bs(item_data.text, 'html.parser')
                item_namee = item_html_data.find_all("span", {"class": "B_NuCI"})
                item_name = item_namee[0].text
                reviwe_data = item_html_data.find_all("div", {"class": "_16PBlm"})
                # print(len(reviwe_data))
                for j in reviwe_data:
                    try:
                        customer_name = j.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                    except:
                        customer_name = None
                        pass
                    try:
                        item_rating = j.div.div.div.div.text
                    except:
                        item_rating = None
                        pass
                    try:
                        rating_comment = j.div.div.div.p.text
                    except:
                        rating_comment = None
                        pass
                    try:
                        detail_comment = j.div.div.find_all('div', {'class': ''})[0].text
                    except:
                        detail_comment = None
                        pass

                    if customer_name is not None and item_rating is not None and rating_comment is not None and detail_comment is not None:
                        all_review_list.append({'product_name': item_name,
                                                'customer_name': customer_name,
                                                'rating': item_rating,
                                                'comment': rating_comment,
                                                'detail_comment': detail_comment
                                                })
                # print(all_review_dict)
                # uri = "mongodb+srv://manaliilag:keev1234@cluster0.6xk6brk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
                # client = pymongo.MongoClient(uri, tlsCAFile=certifi.where())
                # db = client['flipkart_product_review_db']
                # prod_collection = db['review_data']
                # prod_collection.insert_many(all_review_list)
                break
            except Exception as e:
                print(f"Error is {e}")
        return render_template('results.html', reviews=all_review_list)


if __name__ == '__main__':
    application.run(host='0.0.0.0')

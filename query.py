"""
This module implements a (partial, sample) query interface for elasticsearch movie search. 
You will need to rewrite and expand sections to support the types of queries over the fields in your UI.
"""

import sys
from datetime import datetime

from elasticsearch_dsl import Search
from elasticsearch_dsl.utils import AttrList
from flask import *
from index import Document_COVID_19

app = Flask(__name__)

# Initialize global variables for rendering page
tmp_text = ""
tmp_title = ""
tmp_star = ""
tmp_min = ""
tmp_max = ""
gresults = {}

# display query page
@app.route("/")
def search():
    return render_template('page_query.html')


# display results page for first set of results and "next" sets.
@app.route("/results", defaults={'page': 1}, methods=['GET', 'POST'])
@app.route("/results/<page>", methods=['GET', 'POST'])
def results(page):
    global tmp_text
    global tmp_authors
    global tmp_publish_time
    global tmp_search_mode
    global tmp_min
    global tmp_max
    global gresults

    # convert the <page> parameter in url to integer.
    if type(page) is not int:
        page = int(page.encode('utf-8'))
        # if the method of request is post (for initial query), store query in local global variables
    # if the method of request is get (for "next" results), extract query contents from client's global variables
    if request.method == 'POST':
        text_query = request.form['query']
        authors_query = request.form['authors']
        search_mode = request.form['queryMode']

        mintime_query = request.form['mintime']
        if len(mintime_query) is 0:
            mintime = 0
        else:
            mintime = datetime.strptime(mintime_query, '%b %Y').timestamp()
        maxtime_query = request.form['maxtime']
        if len(maxtime_query) is 0:
            maxtime = sys.maxsize
        else:
            maxtime = datetime.strptime(maxtime_query, '%b %Y').timestamp()

        # update global variable template data
        tmp_text = text_query
        tmp_search_mode = search_mode
        tmp_authors = authors_query
        tmp_min = mintime
        tmp_max = maxtime
    else:
        # use the current values stored in global variables.
        text_query = tmp_text
        authors_query = tmp_authors
        search_mode = tmp_search_mode

        mintime = tmp_min
        if tmp_min > 0:
            mintime_query = tmp_min
        else:
            mintime_query = ""
        maxtime = tmp_max
        if tmp_max < sys.maxsize:
            maxtime_query = tmp_max
        else:
            maxtime_query = ""

    # store query values to display in search boxes in UI
    shows = {}
    shows['text'] = text_query
    shows['authors'] = authors_query
    shows['queryMode'] = search_mode
    shows['maxtime'] = maxtime_query
    shows['mintime'] = mintime_query

    # Create a search object to query our index
    search = Search(index='sample_film_index')

    # Build up your elasticsearch query in piecemeal fashion based on the user's parameters passed in.
    # The search API is "chainable".
    # Each call to search.query method adds criteria to our growing elasticsearch query.
    # You will change this section based on how you want to process the query data input into your interface.

    #Publish_time range query
    try:
        if len(mintime_query)>0 and len(maxtime_query)>0:
            s = search.query('range', publish_time={'gte': mintime,
                                                    'lte': maxtime})
        elif len(maxtime_query)>0:
            s = search.query('range', publish_time={'lte': maxtime})
        elif len(mintime_query)>0:
            s = search.query('range', publish_time={'gte': mintime})
        else:
            s = search.query('range', publish_time={'gte': -1})
    except Exception:
        print('Invalid Format. Please format in accordance to the README')
        s = search.query('range', publish_time={'gte': -1})

    #Exact Phrase Query scenario
    if text_query[0]=='<' and text_query[len(text_query)-1]=='>':
        s = s.query('query_string', query=text_query, fields=['title','abstract'])
    else:
        # Conjunctive or Disjunctive search over multiple fields (title and text) using the text_query passed in
        if len(text_query) > 0 and search_mode == 'Disjunctive':
            # s = s.query('multi_match', query=text_query, type='cross_fields', fields=['title', 'abstract'], operator='or')
            s = s.query('multi_match', query=text_query, type='cross_fields', fields=['title', 'abstract'], operator='or')
        elif len(text_query) > 0:
            s = s.query('multi_match', query=text_query, type='cross_fields', fields=['title', 'abstract'], operator='and')

    # search for matching authors
    if len(authors_query) > 0:
        authors_query = "".join([partName+" " for partName in reversed(authors_query.split(" "))]).strip()
        s = s.query('match', authors=authors_query)

    # highlight
    s = s.highlight_options(pre_tags='<mark>', post_tags='</mark>')
    s = s.highlight('abstract', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('title', fragment_size=999999999, number_of_fragments=1)

    # determine the subset of results to display (based on current <page> value)
    start = 0 + (page - 1) * 10
    end = 10 + (page - 1) * 10

    # execute search and return results in specified range.
    response = s[start:end].execute()

    # insert data into response
    resultList = {}
    for hit in response.hits:
        result = {}
        result['score'] = hit.meta.score
        if 'highlight' in hit.meta:
            if 'title' in hit.meta.highlight:
                result['title'] = hit.meta.highlight.title[0]
            else:
                result['title'] = hit.title
            if 'abstract' in hit.meta.highlight:
                result['abstract'] = hit.meta.highlight.abstract[0]
            else:
                result['abstract'] = hit.abstract
        else:
            result['title'] = hit.title
            result['abstract'] = hit.abstract
        resultList[hit.meta.id] = result

    # make the result list available globally
    gresults = resultList

    # get the total number of matching results
    result_num = response.hits.total['value']

    # if we find the results, extract title and text information from doc_data, else do nothing
    if result_num > 0:
        return render_template('page_SERP.html', results=resultList, res_num=result_num, page_num=page, queries=shows)
    else:
        message = []
        if len(text_query) > 0:
            message.append('Unknown search term: ' + text_query)
        if len(authors_query) > 0:
            message.append('Cannot find author: ' + authors_query)

        return render_template('page_SERP.html', results=message, res_num=result_num, page_num=page, queries=shows)


# display a particular document given a result number
@app.route("/documents/<res>", methods=['GET'])
def documents(res):
    global gresults
    film = gresults[res]
    filmtitle = film['title']
    for term in film:
        if type(film[term]) is AttrList:
            s = "\n"
            for item in film[term]:
                s += item + ",\n "
            film[term] = s
    # fetch the movie from the elasticsearch index using its id
    movie = Document_COVID_19.get(id=res, index='sample_film_index')
    return render_template('page_targetArticle.html', film=film, title=filmtitle)


if __name__ == "__main__":
    app.run()

from elasticsearch_dsl import Search
from elasticsearch_dsl.utils import AttrList
from flask import Flask,render_template,request,app 
from index import Document_COVID_19

app = Flask(__name__)

#global variables
temp_text=""
temp_sypm=""
g_results = {}
#display query page (search method)
@app.route("/")
def search():
    return render_template('home_page.html')


#display results (results method)
@app.route("/results",defaults={'page':1},methods=['GET','POST'])
@app.route("/results/<page>",methods=['GET','POST'])
def results(page):
    global temp_text
    global temp_sypm
    global g_results

    if type(page) is not int:
        page = int(page.encode('utf-8'))
    
    if request.method == 'POST':
        text_q = request.form['freesearch']
        symp = request.form['symptom']

        temp_text = text_q
        if (symp == 'none'):
            temp_sypm = " "
        else:
            temp_sypm = symp

    else:
        text_q = temp_text
        symp = temp_sypm

    docs = {}
    docs['text'] = text_q

    search = Search(index='covid_19_index')

    if len(text_q) > 0:
        s = search.query('multi_match',query=text_q,type='cross_fields',fields=['title','abstract','body_text'])
    

    start = 0 + (page - 1) * 10
    end = 10 + (page - 1) * 10

      # execute search and return results in specified range.
    response = s[start:end].execute()
    result_list = {}

    for hit in response.hits:
        result = {}
        result_list['score'] = hit.meta.score
        result_list['title'] = hit.title
        result_list['abstract'] = hit.abstract
        result_list['text'] = hit.body_text

        results_list[hit.meta.paper_id] = result
    
    g_results = result_list
    num_results = response.hits.total['value']
    if num_results > 0:
        return render_template('results.html',results=result_list,num=num_results,page_num=page,queries=docs)
    else:
        message = []
        if len(text_q) > 0:
            message.append('Unknown search term(s) '+text_q)
        
        return render_template('results.html',results=message,num=num_results,page_num=page,queries=docs)
@app.route("/documents/<res>",methods=['GET'])
def documents(res):
    global g_results
    doc = g_results[res]
    title = doc['title']
    text = doc['body_text']
    return render_template('doc_page.html',doc=doc,title=title,text=text)

if __name__ == "__main__":
    app.run(debug=True)

from elasticsearch_dsl import Search
from elasticsearch_dsl.utils import AttrList
from flask import Flask,render_template,request,app
from index import Document_COVID_19

app = Flask(__name__)

#global variables
temp_text=""
temp_sypm=""
temp_race = ""
temp_topic = ""
g_results = {}
#display query page (search method)
@app.route("/")
def search():
    return render_template('home_page.html')


#display results (results method)
@app.route("/results",defaults={'page':1},methods=['GET','POST'])
@app.route("/results/<page>",methods=['GET','POST'])
def results(page):
    global temp_sypm
    global temp_race
    global temp_topic
    global g_results

    if type(page) is not int:
        page = int(page.encode('utf-8'))

    if request.method == 'POST':

        symp = request.form['symptom']
        race_q = request.form['race']

        if len(symp) == 0 or (symp == 'None'):
            temp_sypm = ""
            symp = ""
        else:
            temp_sypm = symp


        if len(race_q) == 0 or (race_q == 'None'):
            temp_race = ""
            race_q = ""
        else:
            temp_race = race_q
    else:
        symp = temp_sypm
        race_q = temp_race

    docs = {}
    docs['symp'] = symp
    docs['race'] = race_q


    search = Search(index='covid_19_index')
    #something needs to always be in free search for now to avoid errors


    if len(symp) > 0:
        full_query = "risk factors "  + symp
        s = search.query('multi_match',query=full_query,type='cross_fields',fields=['title','abstract','body_text'])
    if len(race_q) > 0:
        full_query = "risk "+race_q
        s = search.query('multi_match',query=full_query,type='cross_fields',fields=['title','abstract','body_text'])
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


        result_list[hit.id] = result

    g_results = result_list
    num_results = response.hits.total['value']

    if num_results > 0:
        rem = num_results % 10
        total_pages = num_results / 10
        if rem > 0:
            total_pages = total_pages + 1
        return render_template('results.html',results=result_list,res_num=num_results,page_num=page,total = total_pages,queries=docs)
    else:
        message = []
        message.append('Cannot formulate results')

        return render_template('results.html',results=message,res_num=num_results,page_num=page,queries=docs)

@app.route("/documents/<res>",methods=['GET'])
def documents(res):
    global g_results
    # doc = g_results[res]
    # text = doc['text']
    full_doc = Document_COVID_19.get(id=res,index="covid_19_index")
    return render_template('doc_page.html',doc=full_doc,title=res['title'])

if __name__ == "__main__":
    app.run(debug=True)

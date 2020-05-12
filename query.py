from elasticsearch_dsl import Search
from elasticsearch_dsl.utils import AttrList
from flask import Flask,render_template,request,app
from Topics import Topics
import pickle
from index import Document_COVID_19

app = Flask(__name__)

#global variables
temp_text=""
temp_sypm=""
temp_race = ""
temp_topic = ""
t_setQuestion = ""
g_results = {}
docsTopicMapping = None
#display query page (search method)

@app.route("/")
def search():
    topics = Topics()
    return render_template('home_page.html', topics=topics.startingTopics())


#display results (results method)
@app.route("/results",defaults={'page':1},methods=['GET','POST'])
@app.route("/results/<page>",methods=['GET','POST'])
def results(page):
    global temp_sypm
    global temp_race
    global temp_topic
    global t_setQuestion
    global g_results



    if type(page) is not int:
        page = int(page.encode('utf-8'))

    if request.method == 'POST':

        symp = request.form['symptom']
        race_q = request.form['race']
        topic = request.form['topic']
        question = request.form['set']
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

        if len(question) != 0 or (question != 'None'):
            t_setQuestion = question

        if len(topic) == 0 or (topic == 'None'):
            temp_topic = ""
            topic = ""
        else:
            temp_topic = topic
    else:
        symp = temp_sypm
        race_q = temp_race
        question = t_setQuestion
        topic = temp_topic

    docs = {}
    docs['symp'] = symp
    docs['race'] = race_q
    docs['topic'] = topic
    docs['question'] = question


    search = Search(index='covid_19_index')

    s=None

    if len(symp) > 0:
        full_query = "risk factors "  + symp
        s = search.query('multi_match',query=full_query,type='cross_fields',fields=['title','abstract','body_text'])
    if len(race_q) > 0:
        full_query = "risk "+race_q
        s = search.query('multi_match',query=full_query,type='cross_fields',fields=['title','abstract','body_text'])
    if len(topic) > 0:
        s = search.query('ids',values=getDocsFromTopic(topic))
    if len(question) > 0 & (question != 'None'):
        s = search.query('multi_match',query=question,type='cross_fields',fields=['title','abstract','body_text'])

    start = 0 + (page - 1) * 10
    end = 10 + (page - 1) * 10

    topicsObj = Topics()

    if s is None:
        return render_template('results.html', results={}, res_num=0, page_num=0,
                               total=0,
                               queries=docs, topics=topicsObj.startingTopics())
      # execute search and return results in specified range.
    response = s[start:end].execute()
    result_list = {}

    for hit in response.hits:
        result = {}
        result_list['score'] = hit.meta.score
        result['title'] = hit.title
        result['abstract'] = hit.abstract

        result['text'] = hit.body_text
        result_list[hit.meta.id] = result

    g_results = result_list
    num_results = response.hits.total['value']


    if num_results > 0:
        rem = num_results % 10
        total_pages = num_results / 10
        if rem > 0:
            total_pages = total_pages + 1
        return render_template('results.html',results=result_list,res_num=num_results,page_num=page,total = total_pages,
                               queries=docs, recommendedTopics=topicsObj.recommendedTopics(topic),
                               topics=topicsObj.startingTopics())
    else:
        message = []
        message.append('Cannot formulate results')


    return render_template('results.html',results=message,res_num=num_results,page_num=page,queries=docs,
                           recommendedTopics=topicsObj.recommendedTopics(topic),
                           topics=topicsObj.startingTopics())

def getDocsFromTopic(keyword):
    paperIds = []
    #Find the topic that the keyword is in
    topics = Topics().populateTopics()
    topicNum = -1
    for i in range(len(topics)):
        if keyword in topics[i]:
            topicNum=i

    #Find documents that have that topic
    for key in docsTopicMapping:
        if topicNum in docsTopicMapping[key]:
            paperIds.append(key)

    return paperIds


def getRecommendations(gresults):
    search = Search(index='covid_19_index')
    title = ''
    abstract = ''
    text = ''
    keys = None

    try:
        keys = gresults.keys()
    except:
        search = Search(index='covid_19_index')
        s = search.query('match',_id=gresults['paper_id'])
        gresults = s[0].execute()
        keys = gresults.hits[0]
        gresults = gresults.hits[0]

    if 'title' in keys:
        title = gresults['title']
    if 'abstract' in keys:
        abstract = gresults['abstract']
    if 'text' in keys:
        text = gresults['text']
    s = search.query('more_like_this', fields=['title','abstract','text'], like=title+abstract+text)
    #Top 5 most similar documents
    response = s[0:3].execute()
    ids = []
    for hit in response.hits:
        if hit.title != gresults['title']:
            ids.append(hit)
    return ids

@app.route("/documents/<res>",methods=['GET'])
def documents(res):
    global g_results
    doc = None
    try:
        doc = g_results[res]
    except:
        search = Search(index='covid_19_index')
        s = search.query('match',_id=res)
        doc = s[0].execute().hits[0]
    recommendations = getRecommendations(doc)
    doc_title = doc['title']
    doc_abstract = doc['abstract']
    try:
        doc_text = doc['body_text']
    except:
        doc_text = doc['text']
    return render_template('doc_page.html',title=doc_title,abstract=doc_abstract,text=doc_text,
                           recommendations=recommendations)

if __name__ == "__main__":
    f = open('topic_dict.pkl','rb')
    docsTopicMapping = pickle.load(f)
    f.close()
    app.run(debug=True)

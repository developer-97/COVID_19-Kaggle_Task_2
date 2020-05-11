from elasticsearch_dsl import Search
from elasticsearch_dsl.utils import AttrList
from flask import Flask,render_template,request,app
from index import Document_COVID_19


def getRecommendations(search,gresults):
    s = search.query('more_like_this', fields=['title','abstract','body_text'], like=gresults['title']+gresults['abstract']+gresults['body_text'])

    #Top 5 most similar documents
    response = s[0:4].execute()

    ids = []
    for hit in response.hits:
        if hit.title != gresults['title']:
            ids.append(hit)

    return ids


class RecommendationTest:
    if __name__ == "__main__":
        search = Search(index='covid_19_index')
        s = search.query('multi_match',query="diabetes heart disease smoking",type='cross_fields',fields=['title','abstract','body_text'])
        start = 0 + (1 - 1) * 10
        end = 10 + (1 - 1) * 10
        response = s[start:end].execute()

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
            result['body_text'] = hit.body_text
            resultList[hit.meta.id] = result

        #jNBvAXIBhjijlB3kfaq5 for testing purposes
        getRecommendations(search,resultList['jNBvAXIBhjijlB3kfaq5'])





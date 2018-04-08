import datetime
from haystack import indexes
from debates.models import Debate


class DebateIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    owner = indexes.CharField(model_attr='owner')
    topic = indexes.CharField(model_attr='topic')
    created_on = indexes.DateTimeField(model_attr='created_on')
    approved_on = indexes.DateTimeField(model_attr='approved_on')

    def get_model(self):
        return Debate

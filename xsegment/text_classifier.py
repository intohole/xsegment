#coding=utf-8

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
from sklearn.pipeline import Pipeline
from b2 import str2
from b2 import exceptions2


class ChineseTextClassifier(object):
    """ text classifier for chinese
    """

    def __init__(self, model_path=None):
        self._model = None
        if model_path:
            exceptions2.judge_type(model, basestring)
            self.model = self._load(model_path)

    def _load(self, model_path):
        self._model = joblib.load(model_path)

    def save(self, model_path):
        return joblib.dump(self._model, model_path)

    def _init_model(self):
        vetorizer = TfidfVectorizer()
        classifier = MultinomialNB()
        self._model = Pipeline([('vector', vetorizer), ('classifier',
                                                        classifier)])

    def train(self, docs, target):
        self._init_model()
        self._model.fit(docs, target)

    def predict(self, docs):
        if self._model is None:
            raise ValueError("model not init , you can train model")
        return self._model.predict(docs)


if __name__ == '__main__':
    classifier = ChineseTextClassifier()
    from sklearn.datasets import fetch_20newsgroups
    news20 = fetch_20newsgroups(subset='train')

    classifier.train(news20.data, news20.target)
    print classifier.predict([news20.data[0]])

from wsgiref.simple_server import make_server
import falcon
import json
from sentence_transformers import SentenceTransformer, util

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

import sentences_data

MODEL_PATH = './huggingface-models/'
Large_SEARCHER_Model = 'all-MiniLM-L6-v2'
SMALL_SEARCHER_Model = 'paraphrase-albert-small-v2'

ERR_NOT_SUPPORTED = {"status": falcon.HTTP_404,
                     "code": 10, "title": "Not Supported"}

ERR_UNKNOWN = {"status": falcon.HTTP_500,
               "code": 500, "title": "Unknown Error"}


class Greeting:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_JSON
        resp.media = {'message': "Hello World!"}


class Searcher:
    def __init__(self, model_name):
        self.model_name = model_name
        print(f'{model_name} -> Model is loaded!')
        self.model = SentenceTransformer(MODEL_PATH + model_name)
        print(f'{model_name} -> sentences are transforming...')
        self.sentences_embeddings = self.model.encode(
            sentences_data.sentences, convert_to_tensor=True)
        print(f'{model_name} -> sentences are transformed success!')

    def search(self, query):
        print(query)
        queries = [
            query
        ]
        query_embedding = self.model.encode(queries, convert_to_tensor=True)
        cosine_scores = util.cos_sim(
            self.sentences_embeddings, query_embedding)
        selected = sorted(range(len(cosine_scores)),
                          key=lambda i: cosine_scores[i], reverse=True)[:10]

        return {'top10': [sentences_data.sentences[i] for i in selected]}


class LargeSearcher(Searcher):
    def __init__(self):
        super().__init__(Large_SEARCHER_Model)


class SmallSearcher(Searcher):
    def __init__(self):
        super().__init__(SMALL_SEARCHER_Model)
        print(self.model_name)


large_searcher = LargeSearcher()
small_searcher = SmallSearcher()


class SearchController:

    def on_post(self, req, resp):
        model = req.get_param("model", required=True)
        query = req.media['query']

        if query is None:
            raise NotSupportedError

        if "small" == model:
            resp.media = large_searcher.search(query)
        elif "large" == model:
            resp.media = small_searcher.search(query)
        else:
            resp.media = {"message": "No Model Found"}

        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_JSON


class AppError(Exception):
    def __init__(self, error=ERR_UNKNOWN, description=None):
        self.error = error
        self.error["description"] = description

    @property
    def code(self):
        return self.error["code"]

    @property
    def title(self):
        return self.error["title"]

    @property
    def status(self):
        return self.error["status"]

    @property
    def description(self):
        return self.error["description"]

    @staticmethod
    def handle(exception, req, res, error=None):
        res.status = exception.status
        meta = OrderedDict()
        meta["code"] = exception.code
        meta["message"] = exception.title
        if exception.description:
            meta["description"] = exception.description
        res.body = json.dumps({"meta": meta})


class NotSupportedError(AppError):
    def __init__(self, method=None, url=None):
        super().__init__(ERR_NOT_SUPPORTED)
        if method and url:
            self.error["description"] = "method: %s, url: %s" % (method, url)


greeting = Greeting()

search_controller = SearchController()


def create_app():
    app = falcon.App(middleware=[
    ])
    app.add_route('/', greeting)
    app.add_route('/search', search_controller)
    return app

# app.add_error_handler(falcon.HTTPNotFound, NotSupportedError.handle)


if __name__ == '__main__':
    with make_server('', 8000, create_app()) as httpd:
        print('Serving on port 8000...')

        # Serve until process is killed
        httpd.serve_forever()

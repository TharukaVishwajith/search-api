from wsgiref.simple_server import make_server
import falcon
import json

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

import sentences_data

Large_SEARCHER_Model = 'all-MiniLM-L6-v2'
SMALL_SEARCHER_Model = 'paraphrase-albert-small-v2'

ERR_NOT_SUPPORTED = {"status": falcon.HTTP_404,
                     "code": 10, "title": "Not Supported"}

ERR_UNKNOWN = {"status": falcon.HTTP_500,
               "code": 500, "title": "Unknown Error"}

app = falcon.App(middleware=[
])


class Greeting:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_JSON
        resp.media = {'message': "Hello World!"}


class Searcher:
    def __init__(self, model_name):
        self.model = model_name

    def search(self, query):
        print(query)
        return {'model': self.model}


class LargeSearcher(Searcher):
    def __init__(self):
        super().__init__(Large_SEARCHER_Model)


class SmallSearcher(Searcher):
    def __init__(self):
        super().__init__(SMALL_SEARCHER_Model)


large_searcher = LargeSearcher()
small_searcher = SmallSearcher()


class SearchController:
    # def on_get(self, req, resp):
    #     print(req.params['model'])
    #     if "small" == req.params['model']:
    #         resp.media = large_searcher.search("test")
    #     elif "large" == req.params['model']:
    #         resp.media = small_searcher.search("test")
    #     else:
    #         resp.media = {"message": "No Model Found"}
    #     resp.status = falcon.HTTP_200
    #     resp.content_type = falcon.MEDIA_JSON

    def on_post(self, req, resp):
        model = req.get_param("model", required=True)
        query = req.media['query']

        if "small" == model:
            resp.media = large_searcher.search(query)
        elif "large" == model:
            resp.media = small_searcher.search(query)
        else:
            resp.media = {"message": "No Model Found"}

        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_JSON


# class AppError(Exception):
#     def __init__(self, error=ERR_UNKNOWN, description=None):
#         self.error = error
#         self.error["description"] = description

#     @property
#     def code(self):
#         return self.error["code"]

#     @property
#     def title(self):
#         return self.error["title"]

#     @property
#     def status(self):
#         return self.error["status"]

#     @property
#     def description(self):
#         return self.error["description"]

#     @staticmethod
#     def handle(exception, req, res, error=None):
#         res.status = exception.status
#         meta = OrderedDict()
#         meta["code"] = exception.code
#         meta["message"] = exception.title
#         if exception.description:
#             meta["description"] = exception.description
#         res.body = json.dumps({"meta": meta})


# class NotSupportedError(AppError):
#     def __init__(self, method=None, url=None):
#         super().__init__(ERR_NOT_SUPPORTED)
#         if method and url:
#             self.error["description"] = "method: %s, url: %s" % (method, url)


greeting = Greeting()

search_controller = SearchController()

app.add_route('/', greeting)
app.add_route('/search', search_controller)

# app.add_error_handler(falcon.HTTPNotFound, NotSupportedError.handle)

if __name__ == '__main__':
    with make_server('', 8000, app) as httpd:
        print('Serving on port 8000...')

        # Serve until process is killed
        httpd.serve_forever()

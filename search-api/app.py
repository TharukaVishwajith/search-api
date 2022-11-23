from wsgiref.simple_server import make_server
import falcon

import sentences_data

app = falcon.App(middleware=[
])


class Greeting:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_JSON
        resp.media = {'message': "Hello World!"}


greeting = Greeting()

app.add_route('/', greeting)

if __name__ == '__main__':
    with make_server('', 8000, app) as httpd:
        print('Serving on port 8000...')

        # Serve until process is killed
        httpd.serve_forever()

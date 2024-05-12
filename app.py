from flask import Flask
from flask_restful import Api
from config import config
from models import *
from API.api import Section_api, Book_api, Graph_api


app = Flask(__name__)
app.config.from_object(config['development'])

initialize_db(app)

api = Api(app)


from controllers import * 
api.add_resource(Section_api, "/api/section", "/api/section/<int:section_id>")
api.add_resource(Book_api, "/api/book/<int:section_id>", "/api/book/<int:section_id>/<int:book_id>")
api.add_resource(Graph_api, "/api/graph/<string:parameter>", "/api/graph" )

if __name__ == '__main__':

  app.run(host='0.0.0.0',debug= True, port=5000)
  
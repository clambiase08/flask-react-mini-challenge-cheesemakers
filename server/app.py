from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from flask_migrate import Migrate
from models import Cheese, Producer, db
from flask_restful import Api, Resource, abort

# from flask_restful import Api, Resource


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False


CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class Producers(Resource):
    def get(self):
        producers = [p.to_dict(rules=("-cheeses",)) for p in Producer.query.all()]
        return make_response(producers, 200)


api.add_resource(Producers, "/producers")


class ProducerById(Resource):
    def get(self, id):
        producer = Producer.query.get_or_404(
            id, description="Resource not found"
        ).to_dict()
        return make_response(producer, 200)

    def delete(self, id):
        producer = Producer.query.get_or_404(id, description="Resource not found")
        db.session.delete(producer)
        db.session.commit()
        return make_response("", 204)


api.add_resource(ProducerById, "/producers/<int:id>")


class Cheeses(Resource):
    def post(self):
        data = request.get_json()
        try:
            producer_id = data.get("producer_id")
            producer = Producer.query.get_or_404(producer_id)
            new_cheese = Cheese(
                kind=data["kind"],
                is_raw_milk=data["is_raw_milk"],
                production_date=data["production_date"],
                image=data["image"],
                price=data["price"],
                producer_id=producer.id,
            )
        except Exception as e:
            abort(406, errors=["validation errors"])
        db.session.add(new_cheese)
        db.session.commit()
        return make_response(new_cheese.to_dict(), 201)


api.add_resource(Cheeses, "/cheeses")


class CheeseById(Resource):
    def patch(self, id):
        data = request.get_json()
        try:
            cheese = Cheese.query.get_or_404(id)
            for attr, value in data.items():
                setattr(cheese, attr, value)
        except Exception as e:
            abort(406, errors=["validation errors"])
        db.session.add(cheese)
        db.session.commit()
        return make_response(cheese.to_dict(rules=("-producer",)), 202)

    def delete(self, id):
        cheese = Cheese.query.get_or_404(id, description="Resource not found")
        db.session.delete(cheese)
        db.session.commit()
        return make_response("", 204)


api.add_resource(CheeseById, "/cheeses/<int:id>")


if __name__ == "__main__":
    app.run(port=5555, debug=True)

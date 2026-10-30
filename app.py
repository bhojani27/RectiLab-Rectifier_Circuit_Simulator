from flask import Flask, render_template
from routes.simulation_routes import simulation_blueprint


def create_app():
    app = Flask(__name__)
    app.register_blueprint(simulation_blueprint)

    @app.get("/")
    def home():
        return render_template("index.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

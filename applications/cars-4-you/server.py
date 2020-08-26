import os
from flask import Flask, send_from_directory, request, jsonify, logging
from wml_utils import WMLHelper
from nlu_utils import NLUUtils
from get_vcap import get_wml_vcap, get_cos_vcap, get_vcap

app = Flask(__name__, static_url_path='/static')

wml_vcap = get_wml_vcap()
wml_client = WMLHelper(wml_vcap)


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/stylesheets/<path:path>')
def send_styles(path):
    return send_from_directory('static/stylesheets', path)


@app.route('/scripts/<path:path>')
def send_js(path):
    return send_from_directory('static/scripts', path)


@app.route('/staticImages/<path:path>')
def send_img(path):
    return send_from_directory('static/images', path)


@app.route('/analyze/area', methods=['POST'])
def anayze_area():
    payload = request.get_json(force=True)
    app.logger.debug("Area request: {}".format(payload))
    try:
        response = wml_client.analyze_business_area(payload)
        return jsonify(response), 200
    except Exception as e:
        return str(e), 500


@app.route('/analyze/satisfaction', methods=['POST'])
def analyze_satisfaction():
    comment = request.get_data().decode('utf-8')
    app.logger.debug("Comment to analyze: {}".format(comment))
    try:
        satisfaction = wml_client.analyze_satisfaction(comment)
        app.logger.debug("Predicted satisfaction: {}".format(satisfaction))
        return satisfaction
    except Exception as e:
        return str(e), 500


@app.route('/functions/satisfaction', methods=['GET'])
def functions_satisfaction():
    deployment_array = wml_client.get_function_deployments(keyword="satisfaction")
    app.logger.debug("Satisfaction functions: {}".format(deployment_array))
    response = {
        "deployments": deployment_array
    }
    return jsonify(response)


@app.route('/functions/area', methods=['GET'])
def functions_area():
    deployment_array = wml_client.get_function_deployments(keyword="area")
    app.logger.debug("Area functions: {}".format(deployment_array))
    response = {
        "deployments": deployment_array
    }
    return jsonify(response)


@app.route('/functions', methods=['POST'])
def functions():
    models = request.get_json(force=True)
    app.logger.info("Request to anayze: ")
    app.logger.info(models)
    try:
        wml_client.update_scoring_functions(deployments=models)
        return jsonify("ok"), 200
    except Exception as e:
        app.logger.info(str(e))
        return jsonify(str(e)), 500


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))

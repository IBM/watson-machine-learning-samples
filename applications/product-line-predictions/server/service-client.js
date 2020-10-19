/*
   Copyright 2020 IBM Corp.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

'use strict';

const request = require('request');
const log4js = require('../utils/log4js-logger-util');
const logger = log4js.getLogger('server/service-client');
const debug = require('debug')('sample');
const tokenEndpoint = 'https://iam.cloud.ibm.com/oidc/token';  // authorization endpoint

const modelInfo = require('../config/model.json');
const schema = modelInfo['model-schema'].map(obj => obj.name);

/**
 * getTokenFromTokenEndpoint takes only one argument.
 * The return value is 'token' in all successful cases, in other cases error will be raised.
 * @param {string} apiKey - an API key to your IBM Cloud account or to your IBM Cloud service
 */
function getTokenFromTokenEndpoint (apiKey) {
  debug('getTokenFromTokenEndpoint', tokenEndpoint);
  return new Promise((resolve, reject) => {
    request.post(tokenEndpoint, {
      form: {
        grant_type: 'urn:ibm:params:oauth:grant-type:apikey',
        apikey: apiKey
      }
    }, function (err, res, body) {
      if (err) {
        reject(err);
      }
      debug('got response:', body);
      if (!res || !res.statusCode) {
        reject(new Error('Token Endpoint failure'));
      } else {
        switch (res.statusCode) {
          case 200:
            resolve(JSON.parse(res.body).access_token);
            break;
          default:
            reject(new Error(`Token Endpoint returned ${res.statusCode}.
              Make sure the user is privileged to perform REST API calls.`));
        }
      }
    });
  });
}

// Initialize ServiceClient with service credentials (apikey and url) and space_id for deployments
const ServiceClient = module.exports = function (service) {
  if (service) {
    this.credentials = service.credentials;
    this.space_id = service.space_id;
  }
};

/**
 * ServiceClient makes and manages all calls to the REST API of WML
 */
ServiceClient.prototype = {
  /**
   * isAvailable checks if user provided all necessary information about her/his WML instance
   */
  isAvailable: function () {
    return (this.credentials != null);
  },
  /**
   * performRequest takes specific request options and function callback, it creates needed authorization
   * header by generating authorization token firstly, then performs the user request
   * @param {object} options - options to be passed to request
   * @param {function} callback - callback function to be called on response
   */
  performRequest: function (options, callback) {
    getTokenFromTokenEndpoint(
        this.credentials.apikey
    )
    .then((token) => {
      options.headers = {Authorization: 'Bearer ' + token};
      options.uri = options.uri.startsWith('http') ? options.uri : this.credentials.url + options.uri;
      debug(`url: ${options.uri}`);
      request(options, callback);
    })
    .catch((err) => {
      callback && callback(err);
    });
  },
  /**
   * getScore sends data for prediction to WML scoring endpoint and return predictions.
   * @param {string} href - href / url of the scoring endpoint for specific deployment
   * @param {object} data - data for scoring
   * @param {function} callback - callback function to be called on response
   */
  getScore: function (href, data, callback) {
    logger.enter('getScore()', 'href: ' + href + ', data: ' + data);
    let options = {
      method: 'POST',
      uri: href,
      headers: {'content-type': 'application/json'},
      qs: {
        version: '2020-08-01',
        space_id: this.space_id
      }
    };
    // prepare request body with data to score
    let body = JSON.stringify({input_data: [{values: [data], fields: schema.slice(0, schema.length - 1)}]});
    debug(body);
    options.body = body;

    this.performRequest(options, function (error, response, body) {
      if (!error && response.statusCode === 200) {
        var scoreResponse = JSON.parse(body);
        // fetch scoring probability
        var index = scoreResponse.predictions[0].fields.indexOf('probability');
        scoreResponse['probability'] = {values: scoreResponse.predictions[0].values[0][index]};

        logger.info('getScore()', `successfully finished scoring for scoringHref ${href}`);
        callback && callback(null, scoreResponse);
      } else if (error) {
        logger.error(error);
        callback && callback(JSON.stringify(error.message));
      } else {
        let error = JSON.stringify('Service error code: ' + response.statusCode);
        if (typeof response.body !== 'undefined') {
          try {
            error = JSON.stringify(JSON.parse(response.body).message);
          } catch (e) {
            // suppress
          }
        }
        logger.error(`getScore() error during scoring for scoringHref: ${href}, msg: ${error}`);
        debug(error, 'body: ', response.body);
        callback && callback(error);
      }
    });
  },
  /**
   * _extendDeploymentWithModel check if there is correct model connected with selected deployment
   * and extend deployment information with their model information for main page view
   * @param {array} deployments - array with all fetched deployments
   * @param {function} callback - callback function to be called on response
   */
  _extendDeploymentWithModel: function (deployments, callback) {
    if (deployments.length === 0) {
      callback(null, deployments);
      return;
    }

    let options = {
      method: 'GET',
      uri: '/ml/v4/models',
      qs: {
        version: '2020-08-01',
        space_id: this.space_id
      }
    };
    this.performRequest(options, (error, response, body) => {
      if (!error && response.statusCode === 200) {
        let models = JSON.parse(body).resources;
        let result = deployments.map((item) => {
          let {entity} = item;
          let {metadata} = item;
          // try to find models connected with specific deployments
          let model = models.find(m => m.metadata.id === entity.asset.id);
          return {
            name: metadata.name,
            status: entity.status.state,
            createdAt: metadata.created_at,
            scoringHref: entity.status.online_url.url,
            id: metadata.id,
            model: {
              author: model.metadata.owner,
              input_data_schema: model.entity.training_data_references[0].schema,
              softwareSpecID: model.entity.software_spec.id,
              name: model.metadata.name
            }
          };
        });
        return callback(null, result);
      } else if (error) {
        logger.error('_extendDeploymentWithModel()', error);
        return callback(error.message);
      } else {
        error = new Error('Service error code: ' + response.statusCode);
        logger.error('_extendDeploymentWithModel()', error);
        return callback(error.message);
      }
    });
  },
  /**
   * getDeployments fetche all available deployments and create data with deployment / model information for main view
   * @param {function} callback - callback function to be called on response
   */
  getDeployments: function (callback) {
    logger.enter('getDeployments()');
    let options = {
      method: 'GET',
      uri: '/ml/v4/deployments',
      qs: {
        version: '2020-08-01',
        space_id: this.space_id
      }
    };

    this.performRequest(options, (error, response, body) => {
      if (!error && response.statusCode === 200) {
        let deployments = JSON.parse(body);
        deployments = deployments && deployments.resources;
        debug('all deployments =>', deployments);
        this._extendDeploymentWithModel(deployments, (err, result) => {
          if (err) {
            return callback(err);
          }
          debug('adjusted deployments: ', result);
          return callback(null, result);
        });
      } else if (error) {
        logger.error('getDeployments()', error);
        return callback(error.message);
      } else {
        error = new Error('Service error code: ' + response.statusCode);
        logger.error('getDeployments()', error);
        return callback(error.message);
      }
    });
  }
};

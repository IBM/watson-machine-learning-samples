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

// express server
var express = require('express');
// Error handler for development mode
var morganLogger = require('../utils/morgan-logger-util')('combined');
var log4js = require('../utils/log4js-logger-util');
var logger = log4js.getLogger('server/index');
// cfenv provides access to your Cloud Foundry environment
// (https://www.npmjs.com/package/cfenv)
var cfenv = require('cfenv');
// FileSystem module
var fs = require('fs');
// Request body parser
var bodyParser = require('body-parser');
// load application routes
var routes = require('./routes');

// create a new express server
var app = express();

var port = process.env.PORT ? process.env.PORT : '6001';

var devMode = ('development' === app.get('env'));
var testMode = ('test' === app.get('env'));
var cfAppOptions = {};

try {
  if (devMode) {
    let filePath = './config/local.json';
    fs.accessSync(filePath, fs.constants.R_OK);
    try {
      let localEnv = JSON.parse(fs.readFileSync(filePath));
      cfAppOptions.vcap = {
        services: localEnv
      };
      logger.info(`Using local CF environment read from ${filePath}`);
    } catch (err) {
      logger.warn(`Config file ${filePath} is not a valid JSON file and will not be used.`);
    }
  }
} catch (err) {
  logger.debug(`Failed to read the dev config file: ${err}`);
}

// get the app environment from Cloud Foundry
var appEnv = cfenv.getAppEnv(cfAppOptions);
var pmServiceName = process.env.PA_SERVICE_LABEL ? process.env.PA_SERVICE_LABEL : 'pm-20';
var pmServiceEnv = appEnv.services[pmServiceName] && appEnv.services[pmServiceName][0];

app.set('app env', appEnv);
if (pmServiceEnv) {
  app.set('pm service env', pmServiceEnv);
} else if (!testMode) {
  logger
      .warn('Service is not linked with your application!');
  logger.warn('Running application with limited functionallity.');
}

// development only
if (devMode) {
  let errorhandler = require('errorhandler');
  app.use(errorhandler());
}

// serve the files out of ./public/build as our main files
app.use(express.static(__dirname + '/../public/build'));
app.use(express.static(__dirname + '/../app/static'));
app.use(bodyParser.urlencoded({
  extended: false
}));
app.use(bodyParser.json());
app.use(morganLogger);

app.use('/env', routes.env);

function start() {
  // start server on the specified port and binding host
  app.listen(port, appEnv.host, function () {
    // print a message when the server starts listening
    logger.info('Server listening on port ' + port);
  });
}

exports.app = app;
exports.start = start;

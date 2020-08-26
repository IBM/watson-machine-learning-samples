/* eslint-env node

   Copyright 2016 IBM Corp.

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

var log4js = require('log4js');
log4js.configure({
  appenders: [
    {type: 'console'},
    {
      type: 'file',
      filename: 'log/scoring_app.log',
      level: 'ALL',
      maxLogSize: 20480,
      backups: 10
    }
  ]
});

var typesOfLogging = ['info', 'warn', 'error', 'fatal', 'trace', 'debug'];

function log(logger, level, param1, param2) {
  if (typeof param2 === 'undefined') {
    // what happened
    logger[level](param1);
  } else {
    // where, what happened
    logger[level]('inside ' + param1 + ', ' + param2);
  }
}

var customLogger = {
  getLogger: function (name) {
    var logger = log4js.getLogger(name);

    logger.setLevel('INFO');

    var createdLogger = {
      enter: function (where, args) {
        if (typeof args === 'undefined')
          log(logger, 'debug', 'entering ' + where);
        else
          log(logger, 'debug',
                'entering ' + where + ', arg(s): ' + args);
      },
      return: function (where, returnValue) {
        if (typeof returnValue === 'undefined')
          log(logger, 'debug', 'returning from ' + where);
        else
          log(logger, 'debug',
                'returning from ' + where + ', return: ' + returnValue);
      }
    };

    typesOfLogging.forEach(function (logType) {
      createdLogger[logType] = function (where, what) {
        log(logger, logType, where, what);
      };
    });

    return createdLogger;
  }
};

module.exports = customLogger;

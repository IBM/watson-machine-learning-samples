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

var express = require('express');
var envRouter = express.Router();
var PMClient = require('../service-client');

/**
 * GET on deployments endpoint, to fetched all available and matching deployments with models.
 */
envRouter.get('/deployments', function (req, res) {
  var pmEnv = req.app.get('pm service env');
  var pmClient = new PMClient(pmEnv);
  if (!pmClient.isAvailable()) {
    let err = `To use this sample application, you must bind it with the instance of the
      IBM Watson Machine Learning service and use the proper model from this service.`;
    res.status(404).send(err);
  } else {
    pmClient.getDeployments(function (err, result) {
      if (err) {
        res.status(500).json({errors: err});
      } else {
        console.log(result);
        res.json(result);
      }
    });
  }
});

/**
 * POST on scoring endpoint, to compute predictions.
 */
envRouter.post('/score', function (req, res) {
  let scoringHref = req.body.scoringHref;
  let scoringData = req.body.scoringData;
  try {
    scoringData = JSON.parse(scoringData);

    var pmEnv = req.app.get('pm service env');
    var pmClient = new PMClient(pmEnv);

    pmClient.getScore(scoringHref, scoringData, function (errors, score) {
      res.json({errors: errors, score: score});
    });
  } catch (err) {
    res.status(500).json({errors: ['Provided scoring input is not valid']});
  }
});

exports.env = envRouter;

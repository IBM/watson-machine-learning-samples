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

import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import classNames from 'classnames';
import styles from './style.scss';

const predictionsMapping = require('../../../config/model.json')['model-prediction-mapping'];

class Result extends Component {
  constructor (props) {
    super(props);
    this.handleClose = this.handleClose.bind(this);
  }

  componentDidMount () {
    location.href = '#scoringResult';
  }

  handleClose() {
    this.props.onClose && this.props.onClose();
  }

  render () {
    let {probability} = this.props;
    // translate index to a product, remove 0% probabilities and sort descendingly
    probability = probability
    .map((val, index) => ({product: predictionsMapping[index], value: Math.round(val * 100)}))
    .filter(a => a.value > 0)
    .sort((a, b) => b.value - a.value);
    let best = probability.shift();
    return (
      <div id="scoringResult" className={styles['scoring-result']}>
        <div className={styles['scoring-result-left']}>
          <img src={'images/predictions/' + best.product[1]}/>
        </div>

        <div className={styles['scoring-result-middle']}>
          <h1>{best.value}% {best.product[0]}</h1>
          <p className={styles['scoring-paragraph']}>Based
          on your selection of <span className={classNames(styles['bold'], 'markWithColor')}>{this.props.deployment}</span> and
          your customer, it is predicted
          that <span className={classNames(styles['bold'], 'markWithColor')}>{this.props.id}</span> is {best.value}% certain to
          buy <span className={classNames(styles['bold'], 'markWithColor')}>{best.product[0]}</span>.
          </p>
        </div>

        <div className={styles['scoring-result-right']}>
          <div>
            <h1>Additional Recommendations</h1>
            {probability.map(p => <p><span className={styles['bold']}>{p.value}%</span> {p.product[0]}</p>)}
          </div>
          <div style={{display:'flex', alignItems: 'center'}}>
            <img src='/images/close.png' onClick={this.handleClose} style={{cursor: 'pointer'}}/>
          </div>
        </div>

      </div>
    );
  }
}

module.exports = Result;

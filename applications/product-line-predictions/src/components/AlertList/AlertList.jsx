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
import styles from './style.css';

class Alert extends Component {
  constructor (props) {
    super(props);
    this.state = {
      show: true
    };
    this.handleClose = this.handleClose.bind(this);
  }

  handleClose () {
    this.setState({
      show: false
    });
  }

  componentDidMount() {
    location.href = `#${this.props.id}`;
  }

  render () {
    let {text} = this.props;
    if (!this.state.show || text == null || text.length === 0) {
      return null;
    } else {
      let msgs = Array.isArray(text) ? text : [text];
      return (
        <div className={styles.alertBox} id={this.props.id}>
          <div>
            <p className={styles.title}>Warning!</p>
            {msgs.map((entry, index) => <p className={styles.details} key={index}>{entry}</p>)}
          </div>
          <a onClick={this.handleClose} data-dismiss="alert" aria-label="close">
            <img src='images/close.png' style={{cursor: 'pointer'}}/>
          </a>
        </div>
      );
    }
  }
}

function AlertList (props) {
  let {alerts} = props;
  return (
    <div className={styles.alertList}>
      {alerts.map(alert => <Alert text={alert.message} key={alert.id} id={'alert_' + alert.id}/>)}
    </div>
  );
}

module.exports = AlertList;

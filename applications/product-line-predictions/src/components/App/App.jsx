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
import AlertList from '../AlertList';
import Scoring from '../Scoring';
import styles from './style.css';

let counter = 0;

class App extends Component {
  constructor (props) {
    super(props);
    this.state = {
      alerts: []
    };
    this.showAlert = this.showAlert.bind(this);
  }

  showAlert (message) {
    let {alerts} = this.state;
    let exists = false;
    alerts.map(a => {
      if (a.message === message) {
        a.id = counter++;
        exists = true;
      };
      return a;
    });
    if (!exists) {
      alerts =  [...this.state.alerts, {message: message, id: counter++}];
    }
    this.setState({
      alerts
    });
  }

  render () {
    let ctx = this;
    return (
      <div>
        <div className={styles.mainContainer}>
          <AlertList alerts={this.state.alerts}/>
          <Scoring onAlert={this.showAlert}/>
        </div>
      </div>
    );
  }
}

module.exports = App;

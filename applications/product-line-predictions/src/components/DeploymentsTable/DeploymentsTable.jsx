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
import styles from './style.scss';
import classNames from 'classnames';

const propTypes = {
  data: React.PropTypes.arrayOf(React.PropTypes.shape({
    name: React.PropTypes.string,
    status: React.PropTypes.string,
    createdAt: React.PropTypes.string,
    model: React.PropTypes.shape({
      name: React.PropTypes.string,
      author: React.PropTypes.string,
      softwareSpecID: React.PropTypes.string,
    })
  }))
};

class DeploymentsTable extends Component {
  constructor (props) {
    super(props);
    this.handleSelect = this.handleSelect.bind(this);
    this.statusKeys = {
      'DEPLOY_IN_PROGRESS': 'Deployment In Progress',
      'ready': 'Deployment Successful',
      'failed': 'Deployment Failed',
      'UPDATE_IN_PROGRESS': 'Update In Progress',
      'UPDATE_SUCCESS': 'Update Successful',
      'UPDATE_FAILURE': 'Update Failed'
    };
  }
  handleSelect (e) {
    let rawDeployment = e.target.parentNode.getAttribute('value');
    let deployment = JSON.parse(rawDeployment);
    if (deployment.disabled) {
      return;
    };
    this.props.onChoose && this.props.onChoose(deployment.name, deployment.scoringHref);
  };
  render () {
    let ctx = this;
    return (
      <div className={classNames(styles['deployment-table'], this.props.className)}>
        <table style={{width: '100%'}}>
          <thead className={styles['table-header']}>
            <tr>
              <th className={styles['name']}><span>NAME</span></th>
              <th className={styles['status']}><span>STATUS</span></th>
              <th className={styles['date-created']}><span>CREATED</span></th>
              <th className={styles['model-name']}><span>MODEL NAME</span></th>
              <th className={styles['model-author']}><span>MODEL AUTHOR</span></th>
              <th className={styles['model-runtime']}><span>MODEL Software Spec ID</span></th>
            </tr>
          </thead>
          <tbody>
            {this.props.data.map((entry) => {
              return (
                <tr
                  key={entry.id}
                  value={JSON.stringify(entry)}
                  onClick={ctx.handleSelect}
                  className={classNames(entry.disabled ? [styles.disableRow] : styles.enableRow)}
                  title={entry.disabled ? "Data schema of this model is incompatible with data schema expected by this application." : ''}>
                  <td className={classNames({[styles.enabledRowName]: !entry.disabled, markWithColor: ctx.props.selected === entry.name}, styles.name)}>{entry.name}</td>
                  <td className={styles['status']}>{this.statusKeys[entry.status]}</td>
                  <td className={styles['date-created']}>{entry.createdAt}</td>
                  <td className={styles['model-name']}>{entry.model.name}</td>
                  <td className={styles['model-author']}>{entry.model.author}</td>
                  <td className={styles['model-runtime']}>{entry.model.softwareSpecID}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {this.props.data.length === 0 &&
          <div style={{padding: '3% 20%', color: '#797979'}}>To work with this application, you need to have online deployment of Product Line Prediction model created in your WML service instance.
          For more information check application <a href='https://github.com/pmservice/product-line-prediction/blob/master/README.md' target='_blank'>readme</a>.</div>
        }
      </div>
    );
  }
}

DeploymentsTable.propTypes = propTypes;

module.exports = DeploymentsTable;

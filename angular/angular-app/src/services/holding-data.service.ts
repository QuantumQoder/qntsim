import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class HoldingDataService {
  homepageData = [{
    appId: 1, appName: 'E91', image: 'assets/images/qkd.jpg', content: 'Quantum Key Distribution'
  },
  {
    appId: 2, appName: 'E2E', image: 'assets/images/e2e.png', content: 'End-to-End Entanglements'
  }, {
    appId: 3, appName: 'Teleportation', image: 'assets/images/teleportation1.png', content: 'Quantum Teleportation from one node to another'
  }, {
    appId: 4, appName: 'GHZ', image: 'assets/images/GHZ2.png', content: 'Create GHZ state'
  }, {
    appId: 5, appName: 'Seminal QSDC', image: 'assets/images/QSDC.png', content: 'A high capacity QKD scheme with EPR pairs'
  }, {
    appId: 6, appName: 'QSDC Ping-Pong', image: 'assets/images/Crypt2.png', content: 'A Deterministic secure direct communication scheme using Entanglement'
  }, {
    appId: 7, appName: 'Arbitrary basis QSDC', image: 'assets/images/Crypt4.png', content: 'An arbitrary basis QSDC scheme with mutual user authentication'
  }, {
    appId: 8, appName: 'Single Photon-QD', image: 'assets/images/spqd.jpeg', content: 'A node-to-node dialogue protocol using batches of single photons'
  }, {
    appId: 9, appName: 'QSDC with Controlled Teleportation', image: 'assets/images/qtel.jpeg', content: 'A controlled teleportation scheme for QSDC'
  }, {
    appId: 10, appName: 'IP2', image: 'assets/images/Crypt4.png', content: ''
  },]
  spqd = {
    "application": {
      "input_message1": "Hello",
      "input_message2": "World",
      "attack": "None",
      "output_message1": "x-dln",
      "output_message2": "g'zle",
      "error": 0
    }
  }
  qsdct = {
    "application": {
      "input_message": "Hello World",
      "output_message": "F"
    },
    "graph": {
      "latency": [
        -1,
        -1,
        -1,
        -1,
        -1,
        0.1265044625099998,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1
      ],
      "fidelity": [
        -1,
        -1,
        -1,
        -1,
        -1,
        0.706,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1
      ],
      "throughput": {
        "fully_complete": [
          0,
          0,
          0,
          0,
          0,
          100.0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "partially_complete": [
          0,
          0,
          0,
          0,
          0,
          0.0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        "rejected": [
          0,
          0,
          0,
          0,
          0,
          0.0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ]
      },
      "time": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20
      ]
    }
  };
  constructor() { }
  getQSDCT() {
    return this.qsdct;
  }
  getSpqd() {
    return this.spqd;
  }
  getHomePageData() {
    return this.homepageData
  }

}

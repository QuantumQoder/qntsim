import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class HoldingDataService {
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

}

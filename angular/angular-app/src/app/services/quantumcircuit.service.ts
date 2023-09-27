import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";

import { BehaviorSubject } from "rxjs";
import { environment } from "src/environments/environment";
@Injectable({
  providedIn: "root",
})
export class QuantumcircuitService {

  private subject = new BehaviorSubject<any>("")
  result = this.subject.asObservable()

  constructor(private http: HttpClient) { }

  

  getGates() {
    return this.http.get(environment.apiUrl + "/quantum_gates");
  }

  getGatesLocal() {
    return [
      {
        id: 1,
        gate_name: "I",
        gate_description: "Identity Gate",
      },
      {
        id: 2,
        gate_name: "H",
        gate_description: "Hadamard Gate",
      },
      {
        id: 3,
        gate_name: "X",
        gate_description: "X Gate",
      },
      {
        id: 4,
        gate_name: "Y",
        gate_description: "Y Gate",
      },
      {
        id: 5,
        gate_name: "Z",
        gate_description: "Z Gate",
      },
      {
        id: 6,
        gate_name: "S",
        gate_description: "S Gate",
      },
      {
        id: 7,
        gate_name: "T",
        gate_description: "T Gate",
      },
      {
        id: 13,
        gate_name: "Control",
        gate_description: "Control Gate",
      },
      {
        id: 14,
        gate_name: "SWAP",
        gate_description: "SWAP Gate",
      },
      {
        id: 15,
        gate_name: "RX",
        gate_description: "Rotation X",
      },
      {
        id: 16,
        gate_name: "RY",
        gate_description: "Rotation Y",
      },
      {
        id: 17,
        gate_name: "RZ",
        gate_description: "Rotation Z",
      },
      {
        id: 18,
        gate_name: "U",
        gate_description: "U Gate",
      },
    ].map(({ id, ...rest }) => rest);
  }

  optimization;

  getOptimizationAlogorithm() {
    return this.optimization;
  }
  setOptimizationAlgorithm(data) {
    this.optimization = data;
  }

  getCircuitsForOptimization(algorithm) {
    console.log(this.circuitsForOptimization);
    return this.circuitsForOptimization[algorithm];
  }

  circuitsForOptimization = {
    "QAOA": [
      {
        "header": "Initialization Circuit",
        "value": "initialization"
      },
      {
        "header": "Cost Circuit",
        "value": "cost"
      },
      {
        "header": "Mixer Circuit",
        "value": "mixer"
      },
      {
        "header": "Expectation Circuit",
        "value": "expectation"
      }
    ],
    "VQE": [
      // {
      //   "header": "Initialization Circuit",
      //   "value": "initialization"
      // },
      {
        "header": "Ansatz Circuit",
        "value": "ansatz"
      },
      {
        "header": "Expectation Circuit",
        "value": "expectation"
      }
    ],
    "VQC": [
      {
        "header": "Feature Map Circuit",
        "value": "feature_map"
      },
      {
        "header": "Ansatz Circuit",
        "value": "ansatz"
      }
    ]
  }

  results;

  getResults() {
    return this.results
  }

  setResults(data) {
    this.results = data
  }

}

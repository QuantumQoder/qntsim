import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";

import { environment } from "src/environments/environment";
@Injectable({
  providedIn: "root",
})
export class QuantumcircuitService {
  constructor(private http: HttpClient) {}

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
    QAOA: [
      "Initialization Circuit",
      "Cost Circuit",
      "Mixer Circuit",
      "Expectation Circuit",
    ],
    VQE: ["Initialization Circuit", "Ansatz Circuit", "Expectation Circuit"],
    VQC: ["Feature Map Circuit", "Ansatz Circuit"],
  };
}

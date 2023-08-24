import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { env } from "process";
import { environment } from "src/environments/environment";
@Injectable({
  providedIn: "root",
})
export class QuantumcircuitService {
  constructor(private http: HttpClient) {}

  getGates() {
    return this.http.get(environment.apiUrl + "/quantum_gates");
  }
}

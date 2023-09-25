import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CircuitResultsService {

  constructor(private _http: HttpClient) { }

  results;

  getResults() {
    return this.results
  }

  setResults(data) {
    this.results = data
  }

  execute(data) {
    return this._http.post(environment.apiUrl + "circuit/", data)
  }
}

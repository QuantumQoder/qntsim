import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ConditionsService {
  public app_id: number = 2
  public app: string
  currentSection: any;
  public selectedAppResult = new Subject();
  public _result = this.selectedAppResult.asObservable();
  constructor(private http: HttpClient) { }
  updateNode(value: any) {
    this.selectedAppResult.next(value)
  }
  public result: any
  // = {
  //   "application": { "sender": [[0, "n1", "n2", 0.85, 1.02025048751, 0.020250487510000026, "ENTANGLED"], [1, "n1", "n2", 0.85, 1.02175051251, 0.02175051250999993, "ENTANGLED"], [2, "n1", "n2", 0.85, 1.03225068751, 0.03225068750999993, "ENTANGLED"], [3, "n1", "n2", 0.85, 1.01575041251, 0.01575041251000009, "ENTANGLED"], [4, "n1", "n2", 0.85, 1.04350133751, 0.04350133750999996, "ENTANGLED"], [5, "n1", "n2", 0.85, 1.03525073751, 0.03525073750999996, "ENTANGLED"]], "receiver": [[0, "n2", "n1", 0.85, 1.02025048751, 0.020250487510000026, "ENTANGLED"], [1, "n2", "n1", 0.85, 1.02175051251, 0.02175051250999993, "ENTANGLED"], [2, "n2", "n1", 0.85, 1.03225068751, 0.03225068750999993, "ENTANGLED"], [3, "n2", "n1", 0.85, 1.01575041251, 0.01575041251000009, "ENTANGLED"], [4, "n2", "n1", 0.85, 1.04350133751, 0.04350133750999996, "ENTANGLED"], [5, "n2", "n1", 0.85, 1.03525073751, 0.03525073750999996, "ENTANGLED"]] }, "graph": { "latency": [-1, 0.03525073750999996, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], "fidelity": [-1, 0.85, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], "throughput": { "fully_complete": [0, 100.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "partially_complete": [0, 0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "rejected": [0, 0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] }, "time": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20] }, "performance": {
  //     "latency": 0.06975193750999997,
  //     "fidelity": 0.85,
  //     "throughput": 100.0,
  //     "execution_time": 3
  //   }
  // }
  getResult() {
    return this.result;
  }
  setResult(value: any) {
    this.result = value
  }
  getapp_id() {
    return this.app_id
  }
  setapp_id(app_id: number) {
    this.app_id = app_id
  }
  getApp() {
    return this.app
  }
  setApp(app: string) {
    this.app = app
  }
  jsonUrl(type: any, level: any) {
    return {
      url: type.toLowerCase() + '_' + level + '.json',
      type: type.toLowerCase()
    }
  }
  getJson(url: string, type: any) {
    return this.http.get('../assets/preload-topologies/' + type + '/' + url)
  }
  getAppList() {
    return this.http.get('../assets/app-infos/appList.json')
  }
  getAppSetting() {
    return this.http.get('../assets/app-infos/appSettings.json')
  }
  getMemory() {
    return { "frequency": 2000, "expiry": 2000, "efficiency": 0, "fidelity": 0.93 }
  }

}

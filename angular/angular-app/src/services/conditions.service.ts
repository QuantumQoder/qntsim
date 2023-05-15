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
    return { "frequency": 2000, "expiry": -1, "efficiency": 1, "fidelity": 0.93 }
  }

}

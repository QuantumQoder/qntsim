import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ConditionsService {
  public app_id: number
  public app: string
  currentSection: any;
  public selectedAppResult = new Subject();
  public _result = this.selectedAppResult.asObservable();
  constructor() { }
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
}

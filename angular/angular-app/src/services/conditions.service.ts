import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ConditionsService {
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

}

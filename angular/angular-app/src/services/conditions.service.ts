import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ConditionsService {
  currentSection: any;
  public selectedApp = new Subject();
  public _node = this.selectedApp.asObservable();
  constructor() { }
  updateNode(value: any) {
    this.selectedApp.next(value);
  }

}

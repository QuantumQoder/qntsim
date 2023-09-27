import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class OptimizationService {

  constructor() { }
  private results = new BehaviorSubject<any>(null);
  currentResults = this.results.asObservable()




  setResults(data) {
    this.results.next(data)
  }
}

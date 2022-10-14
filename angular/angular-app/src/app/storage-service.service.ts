import { Injectable, OnDestroy } from '@angular/core';
import { share } from 'rxjs/internal/operators/share';
import { Subject } from 'rxjs/internal/Subject';

@Injectable({
  providedIn: 'root'
})
export class StorageServiceService implements OnDestroy {
  private onSubject = new Subject<{ key: string, value: any }>();
  public changes = this.onSubject.asObservable().pipe(share());

  constructor() {
    this.start();
  }

  ngOnDestroy() {
    this.stop();
  }

  public getStorage() {
    let s = [];
    for (let i = 0; i < sessionStorage.length; i++) {
      s.push({
        key: sessionStorage.key(i),
        value: JSON.parse(sessionStorage.getItem(sessionStorage.key(i)))
      });
    }
    return s;
  }

  public store(key: string, data: any): void {
    sessionStorage.setItem(key, JSON.stringify(data));
    this.onSubject.next({ key: key, value: data })
  }

  public clear(key: any) {
    sessionStorage.removeItem(key);
    this.onSubject.next({ key: key, value: null });
  }


  private start(): void {
    window.addEventListener("storage", this.storageEventListener.bind(this));
  }

  private storageEventListener(event: StorageEvent) {
    if (event.storageArea == sessionStorage) {
      let v;
      try { v = event.newValue; }
      catch (e) { v = event.newValue; }
      this.onSubject.next({ key: event.key, value: v });
    }
  }
  private stop(): void {
    window.removeEventListener("storage", this.storageEventListener.bind(this));
    this.onSubject.complete();
  }
}

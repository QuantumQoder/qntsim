import { Injectable } from '@angular/core';
import { Http2Stream } from 'http2';

@Injectable({
  providedIn: 'root'
})
export class ApiServiceService {

  constructor(private _http: Http2Stream) { }
}

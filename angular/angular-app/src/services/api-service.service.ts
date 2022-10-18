import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
//import { Http2Stream } from 'http2';
import { CookieService } from 'ngx-cookie-service';
@Injectable({
  providedIn: 'root'
})
export class ApiServiceService {

  constructor(private _http: HttpClient, private cookieService: CookieService) { }
  get getAccessToken() {
    return this.cookieService.get('access');
  }
  set setAccessToken(data: any) {
    this.cookieService.set('access', data)
  }
  get getRefreshToken() {
    return this.cookieService.get('refresh');
  }
  set setRefreshToken(data: any) {
    this.cookieService.set('refresh', data)
  }
  accessToken(data: any) {
    return this._http.post(environment.apiUrl + 'api/token/', data);
  }
  runApplication(data: any) {
    var token = localStorage.getItem('access')
    var httpHeader = new HttpHeaders().set('Authorization', 'Bearer ' + token)
    return this._http.post(environment.apiUrl + 'run/', data, { headers: httpHeader })
  }
}

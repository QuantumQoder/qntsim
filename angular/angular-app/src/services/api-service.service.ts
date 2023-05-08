import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { CookieService } from 'ngx-cookie-service';
@Injectable({
  providedIn: 'root'
})
export class ApiServiceService {
  public e2e: any
  public qsdc1: any
  public ghz: any
  ip1: any
  public pingpong: any
  constructor(private _http: HttpClient, private cookieService: CookieService) { }
  get getAccessToken() {
    return this.cookieService.get('access');
  }
  set setAccessToken(data: any) {
    this.cookieService.set('access', data);
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
  runApplication(data: any, apiUrl: string) {
    return this._http.post(apiUrl + 'run/', data)
  }
  ghz1() {
    return this.ghz
  }
  gete2e() {
    return this.e2e
  }
  getqsdc1() {
    return this.qsdc1;
  }
  getip1() {
    return this.ip1
  }
  getPingPong() {
    return this.pingpong
  }
  getCredentials() {
    return {
      "username": "admin",
      "password": "qwerty"
    }
  }
  getSavedModel() {
    return this._http.get('/assets/preload-topologies/advanced/savedModel.json');
  }
}

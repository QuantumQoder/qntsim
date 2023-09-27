import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { CookieService } from "ngx-cookie-service";
import { Observable, Subject } from "rxjs";
import { environment } from "src/environments/environment";

@Injectable({
  providedIn: "root",
})
export class ApiServiceService {
  private subject = new Subject<any>();
  public e2e: any;
  public qsdc1: any;
  public ghz: any;
  ip1: any;
  public pingpong: any;
  constructor(
    private _http: HttpClient,
    private cookieService: CookieService
  ) { }
  get getAccessToken() {
    return this.cookieService.get("access");
  }
  set setAccessToken(data: any) {
    this.cookieService.set("access", data);
  }
  get getRefreshToken() {
    return this.cookieService.get("refresh");
  }
  set setRefreshToken(data: any) {
    this.cookieService.set("refresh", data);
  }
  accessToken(data: any) {
    return this._http.post(environment.apiUrl + "api/token/", data);
  }
  runApplication(data: any, apiUrl: string): Observable<any> {
    return this._http.post(apiUrl + "run/", data);
  }
  optimization(algorithm, data) {
    return this._http.post(`http://192.168.0.52:8001/optimization/${algorithm.toLowerCase()}/`, data)
  }
  advancedRunApplication(data: any, apiUrl: string): Observable<any> {
    // const token = localStorage.getItem("access");
    // const headers = new HttpHeaders().set("Authorization", `Bearer ${token}`);


    // observable.subscribe(() => this.startStream(apiUrl));
    return this._http.post(apiUrl + "run/", data);
  }

  async startStream(url: string) {
    const response = await fetch(`${url}/logs`);
    const reader = response.body.getReader();
    let text = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      text += new TextDecoder().decode(value);
      console.log(text);
      this.subject.next(text);
    }
  }

  getStream(): Observable<any> {
    return this.subject.asObservable();
  }
  ghz1() {
    return this.ghz;
  }
  gete2e() {
    return this.e2e;
  }
  getqsdc1() {
    return this.qsdc1;
  }
  getip1() {
    return this.ip1;
  }
  getPingPong() {
    return this.pingpong;
  }
  getCredentials() {
    return {
      username: "admin",
      password: "qwerty",
    };
  }
  getSavedModel() {
    return this._http.get(
      "/assets/preload-topologies/advanced/savedModel.json"
    );
  }

  request;

  getRequest() {
    return this.request;
  }
  setRequest(data) {
    this.request = data;
  }

  execute(data) {
    console.log(environment.apiUrl + "circuit/", data)
    return this._http.post(environment.apiUrl + "circuit/", data)
  }
}

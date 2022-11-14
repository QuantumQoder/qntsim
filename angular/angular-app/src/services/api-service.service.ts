import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
//import { Http2Stream } from 'http2';
import { CookieService } from 'ngx-cookie-service';
@Injectable({
  providedIn: 'root'
})
export class ApiServiceService {
  public e2e: any = {
    "sender": [
      [
        0,
        "n1",
        "n2",
        0.85,
        1.03525073751,
        0.03525073750999996,
        "ENTANGLED"
      ],
      [
        1,
        "n1",
        "n2",
        0.85,
        1.02625058751,
        0.02625058751000009,
        "ENTANGLED"
      ],
      [
        2,
        "n1",
        "n2",
        0.85,
        1.04725126251,
        0.04725126250999989,
        "ENTANGLED"
      ],
      [
        3,
        "n1",
        "n2",
        0.85,
        1.00675026251,
        0.0067502625099999936,
        "ENTANGLED"
      ],
      [
        4,
        "n1",
        "n2",
        0.85,
        1.01575041251,
        0.01575041251000009,
        "ENTANGLED"
      ],
      [
        5,
        "n1",
        "n2",
        0.85,
        1.04125083751,
        0.04125083751000003,
        "ENTANGLED"
      ]
    ],
    "receiver": [
      [
        0,
        "n2",
        "n1",
        0.85,
        1.03525073751,
        0.03525073750999996,
        "ENTANGLED"
      ],
      [
        1,
        "n2",
        "n1",
        0.85,
        1.02625058751,
        0.02625058751000009,
        "ENTANGLED"
      ],
      [
        2,
        "n2",
        "n1",
        0.85,
        1.04725126251,
        0.04725126250999989,
        "ENTANGLED"
      ],
      [
        3,
        "n2",
        "n1",
        0.85,
        1.00675026251,
        0.0067502625099999936,
        "ENTANGLED"
      ],
      [
        4,
        "n2",
        "n1",
        0.85,
        1.01575041251,
        0.01575041251000009,
        "ENTANGLED"
      ],
      [
        5,
        "n2",
        "n1",
        0.85,
        1.04125083751,
        0.04125083751000003,
        "ENTANGLED"
      ]
    ]
  }
  public ghz: any = {

    "initial_alice_state": "[-0.70710678+0.j  0.        +0.j  0.        +0.j -0.70710678+0.j]",
    "initial_bob_state": "[-0.70710678+0.j  0.        +0.j  0.        +0.j -0.70710678+0.j]",
    "initial_charlie_state": "[-0.70710678+0.j  0.        +0.j  0.        +0.j -0.70710678+0.j]",
    "final_alice_state": "[ 0.        +0.j  0.        +0.j  0.        +0.j -0.70710678+0.j\n  0.70710678+0.j  0.        +0.j  0.        +0.j  0.        +0.j]",
    "final_bob_state": "[ 0.        +0.j  0.        +0.j  0.        +0.j -0.70710678+0.j\n  0.70710678+0.j  0.        +0.j  0.        +0.j  0.        +0.j]",
    "final_charlie_state": "[ 0.        +0.j  0.        +0.j  0.        +0.j -0.70710678+0.j\n  0.70710678+0.j  0.        +0.j  0.        +0.j  0.        +0.j]",
    "alice_state": "[ 0.        +0.j  0.        +0.j  0.        +0.j -0.70710678+0.j\n  0.70710678+0.j  0.        +0.j  0.        +0.j  0.        +0.j]",
    "bob_state": "[ 0.        +0.j  0.        +0.j  0.        +0.j -0.70710678+0.j\n  0.70710678+0.j  0.        +0.j  0.        +0.j  0.        +0.j]",
    "charlie_state": "[ 0.        +0.j  0.        +0.j  0.        +0.j -0.70710678+0.j\n  0.70710678+0.j  0.        +0.j  0.        +0.j  0.        +0.j]",
    "ghz_state": "[0.+0.j 1.+0.j]"

  }
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
  runApplication(data: any) {
    var token = localStorage.getItem('access')
    var httpHeader = new HttpHeaders().set('Authorization', 'Bearer ' + token)
    return this._http.post(environment.apiUrl + 'run/', data, { headers: httpHeader })
  }
  ghz1() {
    return this.ghz
  }
  gete2e() {
    return this.e2e
  }

}

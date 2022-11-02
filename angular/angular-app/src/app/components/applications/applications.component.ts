//import { animate, style, transition, trigger, useAnimation } from '@angular/animations';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MenuItem } from 'primeng/api/menuitem';
import { ApiServiceService } from 'src/services/api-service.service';
import { ConditionsService } from 'src/services/conditions.service';


@Component({
  selector: 'app-applications',
  templateUrl: './applications.component.html',
  styleUrls: ['./applications.component.less'],
})
export class ApplicationsComponent implements OnInit {
  token: any
  responsiveOptions: any
  items: MenuItem[] = [
    { label: 'Home', routerLink: ['/'] },
    { label: 'Application', routerLink: ['applications'] },

  ];

  constructor(private conService: ConditionsService, private _router: Router, private apiService: ApiServiceService) { }

  ngOnInit(): void {
    var data = {
      "username": 'admin',
      "password": 'qwerty'
    }
    this.apiService.accessToken(data).subscribe((res: any) => {
      this.token = res
      localStorage.setItem('access', this.token.access)
    })
    this.conService.currentSection = 'applications'
    this.responsiveOptions = [
      {
        breakpoint: '1024px',
        numVisible: 3,
        numScroll: 3
      },
      {
        breakpoint: '768px',
        numVisible: 2,
        numScroll: 2
      },
      {
        breakpoint: '560px',
        numVisible: 1,
        numScroll: 1
      }
    ];

  }
  e2e() {
    sessionStorage.setItem('app_id', '2')
    this._router.navigate(['/intro'])
  }
  e91() {
    sessionStorage.setItem('app_id', '1')
    this._router.navigate(['/intro'])
  }
  teleportation() {
    sessionStorage.setItem('app_id', '4')
    this._router.navigate(['/intro'])
  }
  ghz() {
    sessionStorage.setItem('app_id', '3')
    this._router.navigate(['/intro'])
  }
  qsdc_epr() {
    sessionStorage.setItem('app_id', '5')
    this._router.navigate(['/intro'])
  }
  pingpong() {
    sessionStorage.setItem('app_id', '6')
    this._router.navigate(['/intro'])
  }
  qsdc_mutual_auth() {
    sessionStorage.setItem('app_id', '7')
    this._router.navigate(['/intro'])
  }

}

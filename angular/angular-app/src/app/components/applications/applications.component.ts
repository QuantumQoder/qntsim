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
  }
  app(app_id: any, app: string) {

    this.conService.setapp_id(app_id);
    localStorage.setItem('app_id', app_id)
    this.conService.setApp(app)
    localStorage.setItem('app', app)
    this._router.navigate(['/intro'])

  }
  app1(app_id: any, app: string) {

    this.conService.setapp_id(app_id);
    localStorage.setItem('app_id', app_id)
    this.conService.setApp(app)
    localStorage.setItem('app', app)
    var currenturl = this._router.url
    var introurl = currenturl.replace('applications', 'intro')
    console.log(introurl)
    window.open(introurl, "_blank")
  }
}

//import { animate, style, transition, trigger, useAnimation } from '@angular/animations';
import { AfterViewInit, Component, OnInit } from '@angular/core';
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
  token: any;
  pageNumber: number;
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
    this.conService.currentSection = 'applications';
    this.pageNumber = 1;
    var prev = document.getElementById("prev")!;
    prev.classList.add("disabled");
    let id1 = document.getElementById("1");
    let id2 = document.getElementById("2");
    let id3 = document.getElementById("3");
    id1?.classList.add("active");
    id2?.classList.remove("active");
    id3?.classList.remove("active");
  }
  app(app_id: any, app: string) {
    if (app_id != 9 || app_id != 8) {
      this.conService.setapp_id(app_id);
      localStorage.setItem('app_id', app_id)
      this.conService.setApp(app)
      localStorage.setItem('app', app)
      this._router.navigate(['/intro'])
    }
    if (app_id == 9 || app_id == 8) {
      this.conService.setapp_id(app_id);
      localStorage.setItem('app_id', app_id)
      this.conService.setApp(app)
      localStorage.setItem('app', app);
      this._router.navigate(['/drag2']);
    }
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
  drag(app_id: any, app: string) {
    this.conService.setapp_id(app_id);
    localStorage.setItem('app_id', app_id)
    this.conService.setApp(app)
    localStorage.setItem('app', app)
    var currenturl = this._router.url
    var introurl = currenturl.replace('applications', 'drag2');
    window.open(introurl, "_blank")
  }
  clicked() {
    console.log('clicked');
  }
  move(data: string) {
    console.log("Move:" + this.pageNumber);
    var prev = document.getElementById("prev");
    let id1 = document.getElementById("1");
    let id2 = document.getElementById("2");
    let id3 = document.getElementById("3");
    if (data == 'prev' && this.pageNumber != 1) {
      this.pageNumber -= 1;
    }
    if (data == 'next' && this.pageNumber != 3) {
      this.pageNumber += 1;
    }
    if (this.pageNumber != 1) {

      prev?.classList.remove("disabled");
    }
    switch (this.pageNumber) {
      case 1:
        id1?.classList.add("active");
        id2?.classList.remove("active");
        id3?.classList.remove("active");
        break;
      case 2:
        id1?.classList.remove("active");
        id2?.classList.add("active");
        id3?.classList.remove("active");
        break;
      case 3:
        id1?.classList.remove("active");
        id2?.classList.remove("active");
        id3?.classList.add("active");
        break;
    }

    // if (this.pageNumber != 3) {

    // }
    // if (this.pageNumber = 1) {
    //   var prev = document.getElementById("prev")!;
    //   prev.classList.add("disabled");
    // }
    console.log("Move:" + this.pageNumber);
  }
  page(data: number) {
    this.pageNumber = data;
    console.log(this.pageNumber)
    if (this.pageNumber != 1) {
      var prev = document.getElementById("prev")!;
      prev.classList.remove("disabled");
    }
    // if (this.pageNumber = 1) {
    //   var prev = document.getElementById("prev")!;
    //   prev.classList.add("disabled");
    // }  
    let id1 = document.getElementById("1");
    let id2 = document.getElementById("2");
    let id3 = document.getElementById("3");
    switch (this.pageNumber) {
      case 1:
        id1?.classList.add("active");
        id2?.classList.remove("active");
        id3?.classList.remove("active");
        break;
      case 2:
        id1?.classList.remove("active");
        id2?.classList.add("active");
        id3?.classList.remove("active");
        break;
      case 3:
        id1?.classList.remove("active");
        id2?.classList.remove("active");
        id3?.classList.add("active");
        break;
    }
  }
}

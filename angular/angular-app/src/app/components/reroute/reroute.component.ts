import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-reroute',
  templateUrl: './reroute.component.html',
  styleUrls: ['./reroute.component.less']
})
export class RerouteComponent implements OnInit {

  constructor() { }

  ngOnInit(): void {
    var route = sessionStorage.getItem('route')
    if (route != null)
      switch (route) {
        case 'facebook':
          window.location.href = 'www.facebook.com';
          break
        case 'twitter':
          window.location.href = 'www.twitter.com';
          break;
        case 'instagram':
          window.location.href = 'www.twitter.com';
          break;
      }
  }

}

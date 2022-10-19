import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-logs',
  templateUrl: './logs.component.html',
  styleUrls: ['./logs.component.less']
})
export class LogsComponent implements OnInit {
  items: MenuItem[];
  activeItem: MenuItem;
  constructor(private _router: Router) { }
  @ViewChild('menuItems') menu: MenuItem[];
  ngOnInit(): void {
    this.items = [
      { label: 'Graph', icon: 'pi pi-fw pi-home' },
      { label: 'Logs', icon: 'pi pi-fw pi-file' },
    ];
    this.activeItem = this.items[1]
  }
  activateMenu() {
    //console.log(this.activeItem.label)
    this.activeItem = this.menu['activeItem'];
    if (this.activeItem.label === 'Graph') {
      var route = 'network-results';

    }
    else {
      var route = 'logs'
    }
    this._router.navigate([route])
    // if (this.activeItem.label === 'Graph1') {
    //   this.graph1 = true
    // }
    // if (this.activeItem.label === 'Graph2') {
    //   this.graph1 = true
    // }
    // if (this.activeItem.label === 'Graph3') {
    //   this.graph1 = true
    // }
  }

}

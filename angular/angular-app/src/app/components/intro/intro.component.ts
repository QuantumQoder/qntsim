import { Component, OnInit } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { Router } from '@angular/router';
@Component({
  selector: 'app-intro',
  templateUrl: './intro.component.html',
  styleUrls: ['./intro.component.less']
})
export class IntroComponent implements OnInit {
  items: MenuItem[]
  app: any
  constructor(private router: Router) { }

  ngOnInit(): void {
    this.app = sessionStorage.getItem('app_id')
    this.items = [
      {
        label: 'Run the Application', icon: 'pi pi-refresh', command: () => {
          this.router.navigate(['/drag2'])
        }
      },
      // {
      //   label: 'Delete', icon: 'pi pi-times',
      // },
      {
        label: 'How To Use', icon: 'pi pi-info', command: () => {
          this.router.navigate(['/how-to-use'])
        }
      },
      // { separator: true },
      // { label: 'Setup', icon: 'pi pi-cog', routerLink: ['/setup'] }
    ];
  }

}

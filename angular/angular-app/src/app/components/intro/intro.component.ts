import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { Router } from '@angular/router';
@Component({
  selector: 'app-intro',
  templateUrl: './intro.component.html',
  styleUrls: ['./intro.component.less'],
  encapsulation: ViewEncapsulation.None
})
export class IntroComponent implements OnInit {
  items: MenuItem[]
  activeIndex: number = 0;
  app: any
  tel = new Teleportation();
  constructor(private router: Router) { }
  goto() {
    this.router.navigate(['/drag2'])
  }
  ngOnInit(): void {
    this.app = sessionStorage.getItem('app_id')
    if (this.app == '1') {
      this.items = [
        {
          label: 'SHARING BELL STATES', command: () => {
            console.log(1)
          }
        },
        {
          label: 'MEASURE AND RECORD RESULTS', command: () => {
            console.log(2)
          }
        },
        {
          label: 'REVEALING THE BASES', command: () => {
            console.log(3)
          }
        }
        // { separator: true },
        // { label: 'Setup', icon: 'pi pi-cog', routerLink: ['/setup'] }
      ];
    }
    if (this.app == '3') {
      this.items = [
        {
          label: 'CHOOSE SOURCE , DESTINATION AND CENTRAL NODES', command: () => {
            console.log(1)
          }
        },
        {
          label: ' TWO PARTY BELL STATES', command: () => {
            console.log(2)
          }
        },
        {
          label: 'GHZ MEASUREMENT​', command: () => {
            console.log(3)
          }
        }
        // { separator: true },
        // { label: 'Setup', icon: 'pi pi-cog', routerLink: ['/setup'] }
      ];
    }
    if (this.app == '2') {
      this.items = [
        {
          label: 'REQUEST ARISING & PATH FINDING', command: () => {
            console.log(1)
          }
        },
        {
          label: 'RESOURCE ALLOCATION, ENTANGLEMENT GENERATION , PURIFICATION, SWAPPING', command: () => {
            console.log(2)
          }
        },
        {
          label: 'END TO END ENTANGLEMENT GENERATION​', command: () => {
            console.log(3)
          }
        }
        // { separator: true },
        // { label: 'Setup', icon: 'pi pi-cog', routerLink: ['/setup'] }
      ];
    }
    if (this.app == '4') {
      this.items = [
        {
          label: 'END TO END ENTANGLEMENT BETWEEN ALICE & BOB​', command: () => {
            console.log(1)
          }
        },
        {
          label: "BELL-STATE MEASUREMENT AT ALICE'S END", command: () => {
            console.log(2)
          }
        },
        {
          label: 'UNITARY OPERATIONS BASED ON ALICE RESULTS​', command: () => {
            console.log(3)
          }
        },

        // { separator: true },
        // { label: 'Setup', icon: 'pi pi-cog', routerLink: ['/setup'] }
      ];
      this.tel.tel1 = 'End to end entanglement between Alice & Bob​'
      this.tel.tel2 = 'Bell-state measurement at Alice end​'
      this.tel.tel3 = 'Unitary operations based on Alice results'
    }
  }
  previous() {
    this.activeIndex = this.activeIndex - 1
  }
  next() {
    this.activeIndex = this.activeIndex + 1
  }

}
export class Teleportation {
  tel1: string;
  tel2: string;
  tel3: string;
}

import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { Router } from '@angular/router';
import { ConditionsService } from 'src/services/conditions.service';
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
  e2e = new E2E();
  constructor(private router: Router, private conService: ConditionsService) { }
  goto() {
    this.router.navigate(['/drag2'])
  }
  ngOnInit(): void {
    this.app = this.conService.getapp_id()
    if (this.app == 1) {
      this.items = [
        {
          label: '', command: () => {
            console.log(1)
          }
        },
        {
          label: '', command: () => {
            console.log(2)
          }
        },
        {
          label: '', command: () => {
            console.log(3)
          }
        }
      ];
    }
    if (this.app == 3) {
      this.items = [
        {
          label: '', command: () => {
            console.log(1)
          }
        },
        {
          label: '', command: () => {
            console.log(2)
          }
        },
        {
          label: '​', command: () => {
            console.log(3)
          }
        }
      ];
    }
    if (this.app == 2) {
      this.items = [
        {
          label: '', command: () => {
            console.log(1)
          }
        },
        {
          label: '', command: () => {
            console.log(2)
          }
        },
        {
          label: '​', command: () => {
            console.log(3)
          }
        }
      ];
      this.e2e.e2e1 = 'Request arising & Path finding';
      this.e2e.e2e2 = 'Resource allocation,entanglement generation,purification,Swapping';
      this.e2e.e2e3 = 'End to End entanglement generation'
    }
    if (this.app == 4) {
      this.items = [
        {
          label: '​', command: () => {
            console.log(1)
          }
        },
        {
          label: "", command: () => {
            console.log(2)
          }
        },
        {
          command: () => {
            console.log(3)
          }
        },
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
export class E2E {
  e2e1: string;
  e2e2: string;
  e2e3: string;
}

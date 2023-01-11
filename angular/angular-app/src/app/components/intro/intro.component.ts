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
  step: number = 1
  currentUrl: string
  tel = new Teleportation();
  e2e = new E2E();
  constructor(private router: Router, private conService: ConditionsService) { }
  goto() {
    this.router.navigate(['/drag2'])
  }
  ngOnInit(): void {
    this.app = localStorage.getItem('app_id')
    if (this.app == 1) {
      this.items = [
        {
          label: 'Sharing Bell States', command: () => {
            console.log(1)
          }
        },
        {
          label: 'Measurement', command: () => {
            console.log(2)
          }
        },
        {
          label: 'Revealing the bases', command: () => {
            console.log(3)
          }
        }
      ];
    }
    if (this.app == 3) {
      this.items = [
        {
          label: 'Entanglement establishment', command: () => {
            console.log(1)
          }
        },
        {
          label: 'Sharing EPR pairs', command: () => {
            console.log(2)
          }
        },
        {
          label: 'GHZ measurement​', command: () => {
            console.log(3)
          }
        }
      ];
    }
    if (this.app == 2) {
      this.items = [
        {
          label: 'Request and Routing', command: () => {
            console.log(1)
          }
        },
        {
          label: 'Establishment', command: () => {
            console.log(2)
          }
        },
        {
          label: 'E2E generation​', command: () => {
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
          label: 'Entanglement between nodes​', command: () => {
            console.log(1)
          }
        },
        {
          label: "Bell state measurement", command: () => {
            console.log(2)
          }
        },
        {
          label: 'Unitary operations',
          command: () => {
            console.log(3)
          }
        },
      ];
      this.tel.tel1 = 'End to end entanglement between Alice & Bob​'
      this.tel.tel2 = 'Bell-state measurement at Alice end​'
      this.tel.tel3 = 'Unitary operations based on Alice results'
    }
    if (this.app == 5) {
      this.items = [
        {
          label: 'Encoding​', command: () => {
            console.log(1)
          }
        },
        {
          label: "Transmission", command: () => {
            console.log(2)
          }
        },
        {
          label: 'Security Check',
          command: () => {
            console.log(3)
          }
        }, {
          label: 'Decoding'
        },
      ];
    }
    if (this.app == 6) {
      this.items = [
        {
          label: 'Encoding', command: () => {
            this.step = 1
          }
        },
        {
          label: 'Security and Authenticity check', command: () => {
            this.step = 1
          }
        },
        {
          label: 'Decoding'
        }
      ]
    }
    if (this.app == 7) {
      this.items = [
        {
          label: 'Ping​', command: () => {
            console.log(1)
          }
        },
        {
          label: "Transformation", command: () => {
            console.log(2)
          }
        },
        {
          label: 'Pong',
          command: () => {
            console.log(3)
          }
        }]
    }
    if (this.app == 8) {
      this.items = [
        {
          label: 'Encoding of first message​', command: () => {
            console.log(1)
          }
        },
        {
          label: "Security check of the channels", command: () => {
            console.log(2)
          }
        },
        {
          label: 'Encoding of second message and decoding',
          command: () => {
            console.log(3)
          }
        }
      ]
    }
    if (this.app == 9) {
      this.items = [
        {
          label: 'Preparing Shared Entanglement​', command: () => {
            console.log(1)
          }
        },
        {
          label: "Alice Encodes the message", command: () => {
            console.log(2)
          }
        },
        {
          label: 'Measurement and Decoding',
          command: () => {
            console.log(3)
          }
        }
      ]
    }
  }
  previous() {
    this.activeIndex = this.activeIndex - 1;
    this.step = 2;
    window.scroll({
      top: 0,
      behavior: 'smooth'
    });
  }
  next() {
    this.activeIndex = this.activeIndex + 1;
    this.step = 1;
    window.scroll({
      top: 0,
      behavior: 'smooth'
    });
  }
  quant_ph(url: string) {
    this.currentUrl = this.router.url;
    window.open(url, "_blank");
    // this.router.navigate([this.currentUrl])
  }
  nextStep() {
    this.step = this.step + 1;
    console.log(this.step)
    window.scroll({
      top: 0,
      behavior: 'smooth'
    });
  }
  previousStep() {
    this.step = this.step - 1;
    window.scroll({
      top: 0,
      behavior: 'smooth'
    });
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
export class qsdc1 {
  qsdc1_1: string;
  qsdc1_2: string;
  qsdc1_3: string;
  qsdc1_4: string;
}

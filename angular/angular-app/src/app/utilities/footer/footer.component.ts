import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.less']
})
export class FooterComponent implements OnInit {

  constructor() { }

  ngOnInit(): void {
  }
  route(route: string) {
    switch (route) {
      case 'facebook': window.open('https://www.' + route + '.com/people/Qulabs/100076856962480/', "_blank");
        break;
      case 'twitter': window.open('https://www.' + route + '.com/Qulabs1', "_blank");
        break;
      case 'linkedin': window.open('https://in.linkedin.com/company/qulabs-software-india', "_blank");
        break;
    }
  }

}

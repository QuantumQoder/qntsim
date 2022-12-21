import { Component, HostListener } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.less']
})
export class AppComponent {
  title = 'QNTSim';
  width: any;
  height: any;

  onActivate($event: any) {
    window.scroll({
      top: 0,
      behavior: 'smooth'
    });

  }
}

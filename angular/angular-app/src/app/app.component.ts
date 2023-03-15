import { AfterViewChecked, AfterViewInit, Component, HostListener } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.less']
})
export class AppComponent implements AfterViewInit {
  navBarList: any[] = [{
    header: 'Home',
    link: '/'
  }, {
    header: 'Get Started',
    link: '/minimal/'
  }, {
    header: 'Applications',
    link: '/applications'
  }]
  ngAfterViewInit(): void {
    var img = document.body.getElementsByTagName('img');
    console.log(img);
    for (var i = 0; i < img.length; i++) {
      img[i].setAttribute('loading', 'lazy');
    }
  }
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

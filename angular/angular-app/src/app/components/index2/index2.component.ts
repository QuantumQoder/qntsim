import { Component, OnInit } from '@angular/core';
import { NavbarComponent } from 'src/app/utilities/navbar/navbar.component';

@Component({
  selector: 'app-index2',
  templateUrl: './index2.component.html',
  styleUrls: ['./index2.component.scss']
})
/**
 * Index-2 component
 */
export class Index2Component implements OnInit {

  constructor(private nav: NavbarComponent) { }

  currentSection = 'home';

  ngOnInit(): void {
    this.nav.currentSection = 'home';
  }

  /**
   * Window scroll method
   */
  // tslint:disable-next-line: typedef
  windowScroll() {
    const navbar = document.getElementById('navbar')!;
    if (document.body.scrollTop > 40 || document.documentElement.scrollTop > 40) {
      navbar.style.backgroundColor = '#1a1a1a';
      navbar.style.padding = '15px 0px';
    }
    else {
      navbar.style.backgroundColor = '';
      navbar.style.padding = '20px';
    }
  }

  /**
   * Toggle navbar
   */
  toggleMenu() {
    document.getElementById('navbarCollapse')!.classList.toggle('show');
  }

  /**
   * Section changed method
   * @param sectionId specify the current sectionID
   */
  onSectionChange(sectionId: any) {
    this.currentSection = sectionId;
  }
}

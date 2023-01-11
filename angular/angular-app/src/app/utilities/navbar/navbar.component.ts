import { AfterViewInit, Component, HostListener, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ConditionsService } from 'src/services/conditions.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.less']
})
export class NavbarComponent implements OnInit, AfterViewInit {
  // loggedIn: boolean
  currentSection: any = this.conService.currentSection
  constructor(private conService: ConditionsService, private router: Router) { }
  ngAfterViewInit(): void {

    // const parallax = window.document.getElementById("navbar-parallax")!;

    // // Parallax Effect for DIV 1
    // window.addEventListener("scroll", function () {
    //   console.log(parallax);
    //   let offset = window.pageYOffset;
    //   parallax.style.top = "-" + offset * 0.01 + "px";
    //   // DIV 1 background will move slower than other elements on scroll.
    // })
  }


  late = "0px 8px 8px -6px rgba(0, 0, 0, .5)"
  ngOnInit(): void {
    // if (this.currentSection === "home") {
    //   this.loggedIn = true
    // }
    // if (this.currentSection === 'applications') {
    //   this.loggedIn = false
    // }
    // window.addEventListener('scroll', this.scroll, true)
  }
  home() {
    this.router.navigate(['/']);
  }
  // @HostListener("window:scroll", [])
  // onWindowsScroll() {
  //   let navbar = <HTMLElement>document.getElementById('nav-inner');
  //   if (document.body.scrollTop > 40 || document.documentElement.scrollTop > 40) {
  //     //console.log(window.scrollY)

  //     navbar.style.backgroundColor = 'transparent'

  //   }
  // }
  // scroll = (): void => {

  //   let scrollHeigth;

  //   if (window.innerWidth < 350) {
  //     scrollHeigth = 150;
  //   } else if (window.innerWidth < 500 && window.innerWidth > 350) {
  //     scrollHeigth = 250;
  //   } else if (window.innerWidth < 700 && window.innerWidth > 500) {
  //     scrollHeigth = 350;
  //   } else if (window.innerWidth < 1000 && window.innerWidth > 700) {
  //     scrollHeigth = 500;
  //   } else {
  //     scrollHeigth = 650;
  //   }

  //   if (window.scrollY >= 0) {
  //     document.body.style.setProperty('--navbar-scroll', "transparent");
  //     document.body.style.setProperty('--navbar-scroll-text', "black");
  //     document.body.style.setProperty('--navbar-scroll-shadow', "none");
  //   } else if (window.scrollY < scrollHeigth) {
  //     document.body.style.setProperty('--navbar-scroll', "black");
  //     document.body.style.setProperty('--navbar-scroll-text', "white");
  //     document.body.style.setProperty('--navbar-scroll-shadow', "0px 6px 12px -5px #000000");
  //   }
  // }

}

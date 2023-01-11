import { AfterViewInit, Component, OnInit } from '@angular/core';
import { ConditionsService } from 'src/services/conditions.service';

@Component({
  selector: 'app-home-page',
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.less']
})
export class HomePageComponent implements OnInit, AfterViewInit {

  constructor(private conService: ConditionsService) { }

  ngOnInit(): void {
    this.conService.currentSection = 'home'
  }
  ngAfterViewInit(): void {
    const parallax = document.getElementById("parallax")!;

    // Parallax Effect for DIV 1
    window.addEventListener("scroll", function () {
      let offset = window.pageYOffset;
      parallax.style.backgroundPositionY = offset * 0.4 + "px";
      // DIV 1 background will move slower than other elements on scroll.
    })
  }
}

import { Component, OnInit } from '@angular/core';
import { ConditionsService } from 'src/services/conditions.service';

@Component({
  selector: 'app-home-page',
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.less']
})
export class HomePageComponent implements OnInit {

  constructor(private conService: ConditionsService) { }

  ngOnInit(): void {
    this.conService.currentSection = 'home'
  }

}

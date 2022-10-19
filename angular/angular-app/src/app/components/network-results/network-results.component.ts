import { Component, OnInit, ViewChild } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { MenuItem } from 'primeng/api/menuitem';
import { Chart, registerables } from 'chart.js';
import { Router } from '@angular/router';
@Component({
  selector: 'app-network-results',
  templateUrl: './network-results.component.html',
  styleUrls: ['./network-results.component.less']
})
export class NetworkResultsComponent implements OnInit {
  chart: any
  chart2: any
  chart3: any
  items: MenuItem[];
  activeItem: MenuItem;
  graph1: boolean;
  graph2: boolean;
  graph3: boolean;
  constructor(private _formBuilder: FormBuilder, private _router: Router) {
    Chart.register(...registerables)
  }
  @ViewChild('menuItems') menu: MenuItem[];
  ngOnInit(): void {
    this.items = [
      { label: 'Graph', icon: 'pi pi-fw pi-home' },
      { label: 'Logs', icon: 'pi pi-fw pi-file' },
    ];
    this.activeItem = this.items[0]
    this.graph1 = true
    console.log(this.activeItem.label)
    this.createChart()

  }
  activateMenu() {
    //console.log(this.activeItem.label)
    this.activeItem = this.menu['activeItem'];
    if (this.activeItem.label === 'Logs') {
      var route = 'logs';
    }
    else {
      var route = 'network-results'
      //this._router.navigate([''])
    }
    this._router.navigate([route])
  }
  createChart() {

    this.chart = new Chart("MyChart", {
      type: 'line', //this denotes tha type of chart

      data: {// values on X-Axis
        labels: ['2022-05-10', '2022-05-11', '2022-05-12', '2022-05-13',
          '2022-05-14', '2022-05-15', '2022-05-16', '2022-05-17',],
        datasets: [
          {
            label: "Sales",
            data: ['467', '576', '572', '79', '92',
              '574', '573', '576'],
            backgroundColor: 'blue'
          },
          {
            label: "Profit",
            data: ['542', '542', '536', '327', '17',
              '0.00', '538', '541'],
            backgroundColor: 'limegreen'
          }
        ]
      },
      options: {
        aspectRatio: 2.5
      }

    });
    this.chart2 = new Chart("MyChart1", {
      type: 'line', //this denotes tha type of chart

      data: {// values on X-Axis
        labels: ['2022-05-10', '2022-05-11', '2022-05-12', '2022-05-13',
          '2022-05-14', '2022-05-15', '2022-05-16', '2022-05-17',],
        datasets: [
          {
            label: "Sales",
            data: ['467', '576', '572', '79', '92',
              '574', '573', '576'],
            backgroundColor: 'blue'
          },
          {
            label: "Profit",
            data: ['542', '542', '536', '327', '17',
              '0.00', '538', '541'],
            backgroundColor: 'limegreen'
          }
        ]
      },
      options: {
        aspectRatio: 2.5
      }

    });
    this.chart3 = new Chart("MyChart2", {
      type: 'line', //this denotes tha type of chart

      data: {// values on X-Axis
        labels: ['2022-05-10', '2022-05-11', '2022-05-12', '2022-05-13',
          '2022-05-14', '2022-05-15', '2022-05-16', '2022-05-17',],
        datasets: [
          {
            label: "Sales",
            data: ['467', '576', '572', '79', '92',
              '574', '573', '576'],
            backgroundColor: 'blue'
          },
          {
            label: "Profit",
            data: ['542', '542', '536', '327', '17',
              '0.00', '538', '541'],
            backgroundColor: 'limegreen'
          }
        ]
      },
      options: {
        aspectRatio: 2.5
      }

    });
  }

}

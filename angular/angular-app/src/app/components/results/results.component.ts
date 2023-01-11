import { ViewEncapsulation } from '@angular/core';
import { AfterViewInit, Component, OnChanges, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';


import { MenuItem } from 'primeng/api';
import { ApiServiceService } from 'src/services/api-service.service';
import { ConditionsService } from 'src/services/conditions.service';
import { HoldingDataService } from 'src/services/holding-data.service';
@Component({
  selector: 'app-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.less'],
  encapsulation: ViewEncapsulation.None
})
export class ResultsComponent implements OnInit, AfterViewInit {
  match: any = []
  alice_r: any
  app_id: any
  items: MenuItem[];
  activeItem: MenuItem;
  data: any
  keyGen: boolean
  keyBits: boolean
  e91: any
  e2e: any
  tel: any
  cols: any
  ghz: any;
  info1: boolean;
  info2: boolean;
  qsdc1: any;
  pingpong: any;
  ip1: any;
  infoqsdc: boolean;
  qsdct: any;
  spqd: any;
  ip2: any;
  app: string;
  constructor(private _formBuilder: FormBuilder, private con: ConditionsService, public api: ApiServiceService, private holdingData: HoldingDataService,
    private router: Router) { }
  ngAfterViewInit(): void {
    if (this.app_id == 1) {
      // var e2e = this.con.getResult();
      this.createTableforE2E()
    }
  }
  @ViewChild('menuItems') menu: MenuItem[];
  ngOnInit(): void {

    this.app_id = this.con.getapp_id()
    // this.app_id = 8
    if (!this.app_id) {
      this.router.navigate(['/applications'])
    }

    switch (this.app_id) {
      case 2:
        var e91 = this.con.getResult()
        this.e91 = e91.application
        console.log(this.e91)
        var length = this.e91.sender_basis_list.length
        for (i = 0; i < length; i++) {
          let x = this.e91.sender_basis_list[i];
          let y = this.e91.receiver_basis_list[i];
          if (x == y) {
            this.match.push(i);
          }
        }
        console.log(this.match)
        var senderKeys: any = []
        var receiverKeys: any = []
        for (var i = 0; i < this.e91.sender_keys.length; i++) {
          senderKeys.push(this.e91.sender_keys[i])
        }
        for (var i = 0; i < this.e91.receiver_keys.length; i++) {
          receiverKeys.push(this.e91.receiver_keys[i])
        }
        // console.log(senderKeys.join(''))
        this.e91.sender_keys = senderKeys.join('')
        this.e91.receiver_keys = receiverKeys.join('')
        this.items = [
          { label: 'Key Bits', icon: 'pi pi-fw pi-home' },
          // { label: 'Statistics', icon: 'pi pi-fw pi-pencil' },
          { label: 'Key Generation', icon: 'pi pi-fw pi-calendar' }
        ];
        this.activeItem = this.items[0]
        break;
      case 1:
        var e2e = this.con.getResult();
        this.e2e = e2e.application;
        break;
      case 3:
        var tele = this.con.getResult();
        this.tel = tele.application;
        break;
      case 4:
        var ghz = this.con.getResult();
        this.ghz = ghz.application;
        break;
      case 5:
        this.qsdc1 = this.con.getResult();
        break;
      case 6:
        this.pingpong = this.con.getResult();
        break;
      case 7:
        var ip1 = this.api.getip1()
        console.log("ip1")
        this.ip1 = this.con.getResult();
        var alice = "Alice_r" + " "
        this.alice_r = this.ip1[alice]
        break;
      case 8:
        this.spqd = this.con.getResult().application;
        console.log(this.spqd)
        break;
      case 9:
        this.qsdct = this.con.getResult().application;
        console.log(this.qsdct)
        break;
      case 10:
        this.ip2 = this.con.getResult().application;
        console.log(this.ip2);
        break;
    }
    // this.data = ['Alice', 'Bob', 'Eve']
    this.keyGen = false
    this.keyBits = true
  }
  info(data: string) {
    switch (data) {
      case 'qsdct':
        this.qsdct = true;
        break;
    }
  }
  info_1() {
    this.info2 = false;
    this.info1 = true;
  }
  info_2() {
    this.info1 = false;
    this.info2 = true;
  }
  info_qsdc() {
    this.infoqsdc = true
  }
  info_qsdc_1(data: string) {
    this.infoqsdc = true;
    this.app = data;
  }
  senderbasis(index: any) {
    var bool = this.match.includes(index)
    return bool ? "table-success" : "";
  }
  createTableforE2E() {
    var table1 = document.getElementById("table1")!;
    var tbody = document.createElement("tbody");
    this.e2e.sender.forEach(function (items: any) {
      var row = document.createElement("tr");
      items.forEach(function (item: any) {
        var cell = document.createElement("td");
        cell.textContent = item;
        row.appendChild(cell);
      });
      tbody.appendChild(row);
      table1.appendChild(tbody)
    });
    var table2 = document.getElementById("table2")!;  // set this to your table
    var tbody = document.createElement("tbody");
    this.e2e.receiver.forEach(function (items: any) {
      var row = document.createElement("tr");
      items.forEach(function (item: any) {
        var cell = document.createElement("td");
        cell.textContent = item;
        row.appendChild(cell);
      });
      tbody.appendChild(row);
      table2.appendChild(tbody)
    });
  }
  activateMenu() {
    this.activeItem = this.menu['activeItem'];
    if (this.activeItem.label == 'Key Generation') {
      this.keyGen = true
      this.keyBits = false
    }
    if (this.activeItem.label == 'Key Bits') {
      this.keyBits = true;
      this.keyGen = false
    }
  }
}

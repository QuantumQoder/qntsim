import { Component, OnChanges, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';

import { MenuItem } from 'primeng/api';
import { ConditionsService } from 'src/services/conditions.service';
@Component({
  selector: 'app-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.less']
})
export class ResultsComponent implements OnInit, OnDestroy {
  app_id: any
  items: MenuItem[];
  activeItem: MenuItem;
  data: any
  keyGen: boolean
  keyBits: boolean
  e91: any
  cols: any
  constructor(private _formBuilder: FormBuilder, private con: ConditionsService) { }
  @ViewChild('menuItems') menu: MenuItem[];
  ngOnInit(): void {
    this.app_id = sessionStorage.getItem('app_id')
    var e91 = this.con.getResult()
    this.e91 = e91.application
    console.log(this.e91)
    var senderKeys: any = []
    var receiverKeys: any = []
    for (var i = 0; i < this.e91.sender_keys.length; i++) {
      senderKeys.push(this.e91.sender_keys[i])
    }
    for (var i = 0; i < this.e91.receiver_keys.length; i++) {
      receiverKeys.push(this.e91.receiver_keys[i])
    }
    console.log(senderKeys.join(''))
    this.e91.sender_keys = senderKeys.join('')
    this.e91.receiver_keys = receiverKeys.join('')
    this.items = [
      { label: 'Key Generation', icon: 'pi pi-fw pi-home' },
      { label: 'Key Bits', icon: 'pi pi-fw pi-calendar' },
      { label: 'Error', icon: 'pi pi-fw pi-pencil' }
      // { label: 'Documentation', icon: 'pi pi-fw pi-file' },
      // { label: 'Settings', icon: 'pi pi-fw pi-cog' }
    ];

    this.data = ['Alice', 'Bob', 'Eve']
    this.activeItem = this.items[0]
    this.keyGen = true
    this.keyBits = false
  }
  ngOnDestroy(): void {

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

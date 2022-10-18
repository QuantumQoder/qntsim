import { Component, OnChanges, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';

import { MenuItem } from 'primeng/api';
@Component({
  selector: 'app-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.less']
})
export class ResultsComponent implements OnInit, OnDestroy {
  items: MenuItem[];
  activeItem: MenuItem;
  data: any
  keyGen: boolean
  keyBits: boolean
  constructor(private _formBuilder: FormBuilder) { }
  @ViewChild('menuItems') menu: MenuItem[];
  ngOnInit(): void {

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

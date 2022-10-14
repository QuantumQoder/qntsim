import { Component, OnChanges, OnDestroy, OnInit } from '@angular/core';
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

  constructor(private _formBuilder: FormBuilder) { }

  ngOnInit(): void {

    this.items = [
      { label: 'Key Generation', icon: 'pi pi-fw pi-home' },
      { label: 'Key Bits', icon: 'pi pi-fw pi-calendar' },
      { label: 'Error', icon: 'pi pi-fw pi-pencil' }
      // { label: 'Documentation', icon: 'pi pi-fw pi-file' },
      // { label: 'Settings', icon: 'pi pi-fw pi-cog' }
    ];
    this.activeItem = this.items[0]
  }
  ngOnDestroy(): void {

  }

}

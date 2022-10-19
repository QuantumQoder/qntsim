import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Index2Component } from '../index2/index2.component';
import { Index12Component } from '../index12/index12.component';



@NgModule({
  declarations: [//Index2Component
    Index12Component],
  imports: [
    CommonModule,

  ],
  exports: [Index12Component]
})
export class ComponentsModule { }

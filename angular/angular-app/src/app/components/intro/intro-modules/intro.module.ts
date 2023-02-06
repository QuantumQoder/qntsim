import { CUSTOM_ELEMENTS_SCHEMA, NgModule, NO_ERRORS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IntroRoutingModule } from './intro-routing.modue';
import { IntroComponent } from '../intro.component';
import { FormsModule } from '@angular/forms';
import { StepsModule } from 'primeng/steps';



@NgModule({

  imports: [
    CommonModule,
    IntroRoutingModule,
    StepsModule
    // FormsModule
  ],
  declarations: [IntroComponent],
  schemas: [NO_ERRORS_SCHEMA]
})
export class IntroModule { }

import { CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MinimalRoutingModule } from './minimal-routing.module';
import { InputNumberModule } from 'primeng/inputnumber';

import { ReactiveFormsModule } from '@angular/forms';
import { DialogModule } from 'primeng/dialog';
import { RadioButtonModule } from 'primeng/radiobutton';
import { MinimalComponent } from '../minimal.component';
import { SliderModule } from 'primeng/slider';
import { TooltipModule } from 'primeng/tooltip';
@NgModule({
    imports: [
        CommonModule,
        MinimalRoutingModule,
        SliderModule,
        ReactiveFormsModule,
        DialogModule,
        InputNumberModule,
        RadioButtonModule,
        TooltipModule
    ],
    declarations: [MinimalComponent],
    schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class MinimalModule { }
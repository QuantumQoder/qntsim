import { CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MinimalRoutingModule } from './minimal-routing.module';

import { scheduled } from 'rxjs';
import { ElementSchemaRegistry } from '@angular/compiler';
import { SidebarModule } from 'primeng/sidebar';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { DialogModule } from 'primeng/dialog';
import { StyleClassModule } from 'primeng/styleclass';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { MinimalComponent } from '../minimal.component';
import { SliderModule } from 'primeng/slider';
@NgModule({
    imports: [
        CommonModule,
        MinimalRoutingModule,
        SliderModule,
        ReactiveFormsModule
    ],
    declarations: [MinimalComponent],
    schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class MinimalModule { }
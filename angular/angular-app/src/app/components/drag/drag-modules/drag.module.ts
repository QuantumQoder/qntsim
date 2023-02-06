import { CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DragRoutingModule } from './drag-routing.module';
import { DragComponent } from '../drag.component';
import { scheduled } from 'rxjs';
import { ElementSchemaRegistry } from '@angular/compiler';
import { SidebarModule } from 'primeng/sidebar';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { DialogModule } from 'primeng/dialog';
import { StyleClassModule } from 'primeng/styleclass';
import { ConfirmDialogModule } from 'primeng/confirmdialog';

@NgModule({
    imports: [
        CommonModule,
        DragRoutingModule,
        SidebarModule,
        FormsModule,
        ReactiveFormsModule,
        DialogModule,
        StyleClassModule,
        ConfirmDialogModule,
    ],
    declarations: [DragComponent],
    schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class DragModule { }
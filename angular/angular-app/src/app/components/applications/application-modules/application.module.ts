import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApplicationRoutingModule } from './application-routing.module';
import { ApplicationsComponent } from '../applications.component';

@NgModule({
    imports: [
        CommonModule,
        ApplicationRoutingModule
    ],
    declarations: [ApplicationsComponent]
})
export class ApplicationModule { }
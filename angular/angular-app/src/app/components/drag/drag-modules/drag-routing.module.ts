import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { DragComponent } from '../drag.component';



const routes: Routes = [
    {
        path: '',
        component: DragComponent
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class DragRoutingModule { }
import { RouterModule, Routes } from "@angular/router";
import { CodeEditorComponent } from "../codeeditor.component";
import { NgModule } from "@angular/core";

const routes: Routes = [
    {
        path: '',
        component: CodeEditorComponent
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class CodeEditorRoutingModule { }
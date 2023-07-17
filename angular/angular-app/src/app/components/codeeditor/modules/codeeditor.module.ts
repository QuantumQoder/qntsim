import { CommonModule } from "@angular/common";
import { CodeEditorComponent } from "../codeeditor.component";
import { NgModule } from "@angular/core";
import { MonacoEditorModule } from 'ngx-monaco-editor'
import { FormsModule } from "@angular/forms";
@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        MonacoEditorModule.forRoot(),
    ],
    declarations: []
})

export class CodeEditorModule {

}
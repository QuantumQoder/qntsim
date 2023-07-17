import { Component, ViewChild } from "@angular/core";
import {
  MonacoEditorComponent,
  MonacoEditorConstructionOptions,
} from "@materia-ui/ngx-monaco-editor";
@Component({
  selector: "app-codeeditor",
  templateUrl: "./codeeditor.component.html",
  styleUrls: ["./codeeditor.component.less"],
})
export class CodeEditorComponent {
  @ViewChild(MonacoEditorComponent, { static: false })
  monacoComponent: MonacoEditorComponent;
  editorOptions: MonacoEditorConstructionOptions = {
    language: "python", // java, javascript, python, csharp, html, markdown, ruby
    theme: "vs-dark", // vs, vs-dark, hc-black
    automaticLayout: true,
    wordBasedSuggestionsOnlySameLanguage: true,
  };
  code = this.getCode();

  getCode() {
    return 'print("hello")\n';
  }
}

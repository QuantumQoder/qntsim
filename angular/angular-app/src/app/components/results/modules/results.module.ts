import { NgModule } from "@angular/core";
import { ResultsRoutingModule } from "./results.routing.module";
import { ResultsComponent } from "../results.component";

@NgModule({
    imports: [ResultsRoutingModule],
    declarations: [ResultsComponent]
})
export class ResultsModule { }
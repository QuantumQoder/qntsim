import { CommonModule } from "@angular/common";
import { HTTP_INTERCEPTORS, HttpClientModule } from "@angular/common/http";
import {
  CUSTOM_ELEMENTS_SCHEMA,
  NO_ERRORS_SCHEMA,
  NgModule,
} from "@angular/core";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { BrowserModule } from "@angular/platform-browser";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { RouterModule } from "@angular/router";
import { NgbPopoverModule } from "@ng-bootstrap/ng-bootstrap";
import { ScrollToModule } from "@nicky-lenaers/ngx-scroll-to";
import { CookieService } from "ngx-cookie-service";
import { NgxTypedJsModule } from "ngx-typed-js";
import { AccordionModule } from "primeng/accordion";
import { CarouselModule } from "primeng/carousel";
import { ProgressSpinnerModule } from "primeng/progressspinner";
import { ScrollPanelModule } from "primeng/scrollpanel";
import { SliderModule } from "primeng/slider";
import { SplitButtonModule } from "primeng/splitbutton";
import { StyleClassModule } from "primeng/styleclass";
import { TooltipModule } from "primeng/tooltip";
import { HomePageComponent } from "src/app/components/home-page/home-page.component";
import { DiagramBuilderService } from "src/app/services/diagram-builder.service";
import { DiagramStorageService } from "src/app/services/diagram-storage.service";
import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { JwtInterceptor } from "./auth/jwt.interceptor";
import { ResultsComponent } from "./components/results/results.component";
import { CtrlClickDirective } from "./directives/ctrl-click";
import { FooterComponent } from "./utilities/footer/footer.component";
import { NavbarComponent } from "./utilities/navbar/navbar.component";
import { ConditionsService } from "src/app/services/conditions.service";
import { HoldingDataService } from "src/app/services/holding-data.service";
import { ApiServiceService } from "src/app/services/api-service.service";
import { CodeEditorComponent } from "./components/codeeditor/codeeditor.component";
// import { MonacoEditorModule } from 'ngx-monaco-editor';
import { MonacoEditorModule, MONACO_PATH } from "@materia-ui/ngx-monaco-editor";
import { StoreModule } from "@ngrx/store";
import { minimalReducer } from "./store/minimal.reducer";
import { StoreDevtoolsModule } from "@ngrx/store-devtools";
import { TopologyLoaderService } from "./services/loadTopology.service";

@NgModule({
  schemas: [CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA],
  declarations: [
    ResultsComponent,
    AppComponent,
    HomePageComponent,
    NavbarComponent,
    FooterComponent,
    CtrlClickDirective,
    CodeEditorComponent,
  ],
  imports: [
    SplitButtonModule,
    RouterModule,
    ProgressSpinnerModule,
    HttpClientModule,
    FormsModule,
    AccordionModule,
    FormsModule,
    ReactiveFormsModule,
    StyleClassModule,
    SliderModule,
    ReactiveFormsModule,
    ScrollPanelModule,
    AccordionModule,
    CommonModule,
    ScrollToModule.forRoot(),
    NgxTypedJsModule,
    CarouselModule,
    BrowserModule,
    AppRoutingModule,
    StyleClassModule,
    BrowserAnimationsModule,
    NgbPopoverModule,
    TooltipModule,
    MonacoEditorModule,
    StoreModule.forRoot({ minimal: minimalReducer }),
    // StoreDevtoolsModule.instrument({
    //   maxAge: 25,
    // }),
    // AceEditorModule
  ],
  providers: [
    CookieService,
    DiagramStorageService,
    DiagramBuilderService,
    ConditionsService,
    HoldingDataService,
    ApiServiceService,
    TopologyLoaderService,
    { provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true },
    {
      provide: MONACO_PATH,
      useValue: "https://unpkg.com/monaco-editor@0.36.1/min/vs",
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}

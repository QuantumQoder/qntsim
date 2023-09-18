import { QuantumcircuitService } from "./components/quantum-circuit/quantumcircuit.service";
import { CommonModule } from "@angular/common";
import { HTTP_INTERCEPTORS, HttpClientModule } from "@angular/common/http";
import {
  CUSTOM_ELEMENTS_SCHEMA,
  NO_ERRORS_SCHEMA,
  NgModule, isDevMode,
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

// import { MonacoEditorModule } from 'ngx-monaco-editor';
import { MonacoEditorModule, MONACO_PATH } from "@materia-ui/ngx-monaco-editor";
import { StoreModule } from "@ngrx/store";
import { minimalReducer } from "./store/minimal.reducer";
// import { StoreDevtoolsModule } from "@ngrx/store-devtools";
import { TopologyLoaderService } from "./services/loadTopology.service";
import { CheckboxModule } from "primeng/checkbox";
import { InputTextModule } from "primeng/inputtext";
import { DialogModule } from "primeng/dialog";
import { MultiSelectModule } from "primeng/multiselect";
import { DropdownModule } from "primeng/dropdown";
import { QuantumCircuitComponent } from "./components/quantum-circuit/quantum-circuit.component";
import { TableModule } from "primeng/table";
import { StepsModule } from "primeng/steps";
import { TabMenuModule } from "primeng/tabmenu";
import { OptimizationComponent } from './components/optimization/optimization.component';
import { ServiceWorkerModule } from '@angular/service-worker';
import { OptimizationResultsComponent } from './components/optimization-results/optimization-results.component';
import { OptimizationService } from "./services/optimization.service";
import { NgApexchartsModule } from 'ng-apexcharts'
// import { OptimizationResultsComponent } from './optimization-results/optimization-results.component';
// import { AccordionModule } from "primeng/accordion";
@NgModule({
  schemas: [CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA],
  declarations: [
    ResultsComponent,
    AppComponent,
    HomePageComponent,
    NavbarComponent,
    FooterComponent,
    CtrlClickDirective,
    QuantumCircuitComponent,
    OptimizationComponent,
    OptimizationResultsComponent,

  ],
  imports: [
    NgApexchartsModule,
    CheckboxModule,
    TabMenuModule,
    StepsModule,
    TableModule,
    DialogModule,
    DropdownModule,
    InputTextModule,
    MultiSelectModule,
    // QuantumGatesModule,
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
    ServiceWorkerModule.register('ngsw-worker.js', {
      enabled: !isDevMode(),
      // Register the ServiceWorker as soon as the application is stable
      // or after 30 seconds (whichever comes first).
      registrationStrategy: 'registerWhenStable:30000'
    }),
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
    QuantumcircuitService,
    OptimizationService,
    { provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true },
    {
      provide: MONACO_PATH,
      useValue: "https://unpkg.com/monaco-editor@0.36.1/min/vs",
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule { }

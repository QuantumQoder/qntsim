import { NgModule, NO_ERRORS_SCHEMA } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ButtonModule } from 'primeng/button'
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomePageComponent } from 'src/app/components/home-page/home-page.component';
import { ScrollToModule } from '@nicky-lenaers/ngx-scroll-to';
import { NgxTypedJsModule } from 'ngx-typed-js';
import { NgParticlesModule } from 'ng-particles';
import { NavbarComponent } from './utilities/navbar/navbar.component';
import { BreadcrumbModule } from 'primeng/breadcrumb';
import { CardModule } from 'primeng/card'
import { StyleClassModule } from 'primeng/styleclass';
import { DividerModule } from 'primeng/divider';
import { SplitterModule } from 'primeng/splitter';
import { FieldsetModule } from 'primeng/fieldset';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AccordionModule } from 'primeng/accordion'
import { CommonModule } from '@angular/common';
import { StepsModule } from 'primeng/steps';
import { FooterComponent } from './utilities/footer/footer.component';
import { CarouselModule } from 'primeng/carousel';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { TableModule } from 'primeng/table';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { DragComponent } from './components/drag/drag.component';
import { TabMenuModule } from 'primeng/tabmenu';
import { ResultsComponent } from './components/results/results.component';
import { ToastModule } from 'primeng/toast';
import { SidebarModule } from 'primeng/sidebar';
import { DialogModule } from 'primeng/dialog';
import { SpeedDialModule } from 'primeng/speeddial';
import { DropdownModule } from 'primeng/dropdown';
import { CookieService } from 'ngx-cookie-service';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { BlockUIModule } from 'primeng/blockui';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { IntroComponent } from './components/intro/intro.component';
import { SplitButtonModule } from 'primeng/splitbutton';
// import { HowtouseComponent } from './components/howtouse/howtouse.component';
import { NgbPopoverModule } from '@ng-bootstrap/ng-bootstrap';
import { CtrlClickDirective } from './directives/ctrl-click';
import { JwtInterceptor } from './auth/jwt.interceptor';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { MinimalComponent } from './components/minimal/minimal.component';

// import { GameComponent } from './components/game/game.component';
// import { ToastModule } from 'primeng/toast';
// import { Alert } from '@ng-bootstrap/ng-bootstrap';
//import { AngularAnimationsLibraryModule } from 'angular-animations-library'
@NgModule({
  schemas: [CUSTOM_ELEMENTS_SCHEMA,
    NO_ERRORS_SCHEMA
  ],
  declarations: [
    AppComponent,
    HomePageComponent,
    NavbarComponent,
    FooterComponent,
    DragComponent,
    ResultsComponent,
    CtrlClickDirective,
    // MinimalComponent
  ],
  imports: [SplitButtonModule,
    ProgressSpinnerModule,
    BlockUIModule,
    HttpClientModule,
    FormsModule,
    DropdownModule,
    SpeedDialModule,


    SidebarModule,
    FormsModule,
    ReactiveFormsModule,
    DialogModule,
    StyleClassModule,
    ConfirmDialogModule,

    ToastModule,
    TabMenuModule,
    ReactiveFormsModule,
    TableModule,
    ScrollPanelModule,
    AccordionModule,

    // ComponentsModule,
    CommonModule,
    ScrollToModule.forRoot(),
    NgxTypedJsModule,
    NgParticlesModule,
    CarouselModule,
    BrowserModule,
    AppRoutingModule,
    ButtonModule,
    BreadcrumbModule,
    StyleClassModule,
    CardModule,
    DividerModule,
    SplitterModule,
    FieldsetModule,
    BrowserAnimationsModule,
    NgbPopoverModule,

    //NgbModule,
  ],
  providers: [CookieService,
    { provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true }],
  bootstrap: [AppComponent]
})
export class AppModule { }

import { NgModule, NO_ERRORS_SCHEMA } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ButtonModule } from 'primeng/button'
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomePageComponent } from 'src/app/components/home-page/home-page.component';
import { ScrollToModule } from '@nicky-lenaers/ngx-scroll-to';
import { NgxTypedJsModule } from 'ngx-typed-js';

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

import { FooterComponent } from './utilities/footer/footer.component';
import { CarouselModule } from 'primeng/carousel';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { TableModule } from 'primeng/table';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AdvancedComponent } from './components/drag/advanced.component';
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
import { SplitButtonModule } from 'primeng/splitbutton';
import { NgbPopoverModule } from '@ng-bootstrap/ng-bootstrap';
import { CtrlClickDirective } from './directives/ctrl-click';
import { JwtInterceptor } from './auth/jwt.interceptor';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CheckboxModule } from 'primeng/checkbox';
import { SliderModule } from 'primeng/slider';


@NgModule({
  schemas: [CUSTOM_ELEMENTS_SCHEMA,
    NO_ERRORS_SCHEMA
  ],
  declarations: [
    AppComponent,
    HomePageComponent,
    NavbarComponent,
    FooterComponent,
    // AdvancedComponent,
    ResultsComponent,
    CtrlClickDirective
  ],
  imports: [SplitButtonModule,
    ProgressSpinnerModule,
    BlockUIModule,
    HttpClientModule,
    FormsModule,
    DropdownModule,
    SpeedDialModule,
    CheckboxModule,
    AccordionModule,
    SidebarModule,
    FormsModule,
    ReactiveFormsModule,
    DialogModule,
    StyleClassModule,
    ConfirmDialogModule,
    SliderModule,
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

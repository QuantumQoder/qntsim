import { NgModule, NO_ERRORS_SCHEMA, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomePageComponent } from 'src/app/components/home-page/home-page.component';
import { ScrollToModule } from '@nicky-lenaers/ngx-scroll-to';
import { NgxTypedJsModule } from 'ngx-typed-js';
import { NavbarComponent } from './utilities/navbar/navbar.component';
import { StyleClassModule } from 'primeng/styleclass';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AccordionModule } from 'primeng/accordion'
import { CommonModule } from '@angular/common';
import { FooterComponent } from './utilities/footer/footer.component';
import { CarouselModule } from 'primeng/carousel';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CookieService } from 'ngx-cookie-service';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { SplitButtonModule } from 'primeng/splitbutton';
import { NgbPopoverModule } from '@ng-bootstrap/ng-bootstrap';
import { CtrlClickDirective } from './directives/ctrl-click';
import { JwtInterceptor } from './auth/jwt.interceptor';
import { SliderModule } from 'primeng/slider';
import { RouterModule } from '@angular/router';
import { ResultsComponent } from './components/results/results.component';
import { TooltipModule } from 'primeng/tooltip';
import { DiagramStorageService } from 'src/services/diagram-storage.service';
@NgModule({
  schemas: [CUSTOM_ELEMENTS_SCHEMA,
    NO_ERRORS_SCHEMA
  ],
  declarations: [
    ResultsComponent,
    AppComponent,
    HomePageComponent,
    NavbarComponent,
    FooterComponent,
    CtrlClickDirective
  ],
  imports: [SplitButtonModule,
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
    NgbPopoverModule, TooltipModule
  ],
  providers: [CookieService,
    DiagramStorageService,
    { provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true }],
  bootstrap: [AppComponent]
})
export class AppModule { }

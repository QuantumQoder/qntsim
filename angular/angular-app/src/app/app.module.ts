import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ButtonModule } from 'primeng/button'
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomePageComponent } from 'src/app/components/home-page/home-page.component';
import { ScrollToModule } from '@nicky-lenaers/ngx-scroll-to';
import { NgxTypedJsModule } from 'ngx-typed-js';
import { NgParticlesModule } from 'ng-particles';
import { NavbarComponent } from './utilities/navbar/navbar.component';
import { ApplicationsComponent } from './components/applications/applications.component';
import { BreadcrumbModule } from 'primeng/breadcrumb';
import { CardModule } from 'primeng/card'
import { StyleClassModule } from 'primeng/styleclass';
import { DividerModule } from 'primeng/divider';
import { SplitterModule } from 'primeng/splitter';
import { FieldsetModule } from 'primeng/fieldset';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AccordionModule } from 'primeng/accordion'
import { Index2Component } from './components/index2/index2.component';
import { CommonModule } from '@angular/common';
import { ComponentsModule } from './components/module/components.module';
import { FooterComponent } from './utilities/footer/footer.component';
import { CarouselModule } from 'primeng/carousel';
import { ScrollPanelModule } from 'primeng/scrollpanel';
import { ApplicationPageComponent } from './components/application-page/application-page.component';
import { TableModule } from 'primeng/table';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { DraggableLinkComponent } from './components/draggable-link/draggable-link.component';
import { DragComponent } from './components/drag/drag.component';
import { TabMenuModule } from 'primeng/tabmenu';
//import { MenuItem } from 'primeng/api';
import { ResultsComponent } from './components/results/results.component';
import { NetworkResultsComponent } from './components/network-results/network-results.component';
import { LogsComponent } from './components/logs/logs.component';
import { ToastModule } from 'primeng/toast';
import { SidebarModule } from 'primeng/sidebar';
import { DialogModule } from 'primeng/dialog';
import { SpeedDialModule } from 'primeng/speeddial';
import { DropdownModule } from 'primeng/dropdown';
import { CookieService } from 'ngx-cookie-service';
import { HttpClientModule } from '@angular/common/http';
// import { Alert } from '@ng-bootstrap/ng-bootstrap';
//import { AngularAnimationsLibraryModule } from 'angular-animations-library'
@NgModule({
  declarations: [
    AppComponent,
    HomePageComponent,
    NavbarComponent,
    ApplicationsComponent,
    Index2Component,
    FooterComponent,
    ApplicationPageComponent,
    DraggableLinkComponent,
    DragComponent,
    ResultsComponent,
    NetworkResultsComponent,
    LogsComponent
    //ButtonModule
    //AngularAnimationsLibraryModule
  ],
  imports: [
    HttpClientModule,
    FormsModule,
    DropdownModule,
    SpeedDialModule,
    DialogModule,
    SidebarModule,
    ToastModule,
    TabMenuModule,
    ReactiveFormsModule,
    TableModule,
    ScrollPanelModule,
    AccordionModule,
    ComponentsModule,
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
    BrowserAnimationsModule
    //NgbModule,
  ],
  providers: [CookieService],
  bootstrap: [AppComponent]
})
export class AppModule { }

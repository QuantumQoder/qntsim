import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
// import { ApplicationPageComponent } from './components/application-page/application-page.component';
import { ApplicationsComponent } from './components/applications/applications.component';
// import { DraggableLinkComponent } from './components/draggable-link/draggable-link.component';
import { HomePageComponent } from './components/home-page/home-page.component';
// import { Index2Component } from './components/index2/index2.component'
import { LogsComponent } from './components/logs/logs.component';
import { NetworkResultsComponent } from './components/network-results/network-results.component';
import { ResultsComponent } from './components/results/results.component';
import { DragComponent } from './components/drag/drag.component';
import { IntroComponent } from './components/intro/intro.component';
import { RerouteComponent } from './components/reroute/reroute.component';
// import { HowtouseComponent } from './components/howtouse/howtouse.component';
//import { HomeComponent } from './components/home/home.component';

const routes: Routes = [
  { path: '', component: HomePageComponent },
  { path: 'applications', component: ApplicationsComponent },
  // { path: 'home', component: Index2Component }
  // { path: 'drag', component: DraggableLinkComponent },
  { path: 'drag2', component: DragComponent },
  { path: 'results', component: ResultsComponent },
  { path: 'network-results', component: NetworkResultsComponent },
  { path: 'logs', component: LogsComponent },
  { path: 'intro', component: IntroComponent },
  { path: 'route', component: RerouteComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

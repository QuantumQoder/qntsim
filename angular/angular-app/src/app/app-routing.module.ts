import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomePageComponent } from './components/home-page/home-page.component';
import { ResultsComponent } from './components/results/results.component';

const routes: Routes = [
  { path: '', component: HomePageComponent },
  { path: 'applications', loadChildren: () => import('./components/applications/application-modules/application.module').then(m => m.ApplicationModule) },
  { path: 'advanced', loadChildren: () => import('./components/drag/modules/advanced.module').then(m => m.ApplicationModule) },
  { path: 'results', component: ResultsComponent },
  { path: 'intro', loadChildren: () => import('./components/intro/intro-modules/intro.module').then(m => m.IntroModule) },
  { path: 'minimal', loadChildren: () => import('./components/minimal/modules/minimal.module').then(m => m.MinimalModule) },
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { HomePageComponent } from "./components/home-page/home-page.component";
import { ResultsComponent } from "./components/results/results.component";

import { QuantumCircuitComponent } from "./components/quantum-circuit/quantum-circuit.component";
import { OptimizationComponent } from "./components/optimization/optimization.component";
import { OptimizationResultsComponent } from "./components/optimization-results/optimization-results.component";
import { CircuitResultsComponent } from "./components/circuit-results/circuit-results.component";

const routes: Routes = [
  { path: "", component: HomePageComponent, title: "QNTSIM" },
  {
    path: "applications",
    loadChildren: () =>
      import(
        "./components/applications/application-modules/application.module"
      ).then((m) => m.ApplicationModule),
    title: "Applications",
  },
  {
    path: "advanced",
    loadChildren: () =>
      import("./components/advanced/modules/advanced.module").then(
        (m) => m.AdvancedModule
      ),
    title: "Advanced",
  },
  { path: "results", component: ResultsComponent, title: "Results" },
  {
    path: "intro",
    loadChildren: () =>
      import("./components/intro/intro-modules/intro.module").then(
        (m) => m.IntroModule
      ),
    title: "Intro",
  },
  {
    path: "minimal",
    loadChildren: () =>
      import("./components/minimal/modules/minimal.module").then(
        (m) => m.MinimalModule
      ),
    title: "Minimal",
  },
  {
    path: "circuit",
    component: QuantumCircuitComponent,
    title: "Quantum Circuit",
  }, {
    path: "optimization",
    component: OptimizationComponent,
    title: "Optimization"
  },
  {
    path: 'optimization-results',
    component: OptimizationResultsComponent,
    title: "Optimization Results",
  },
  {
    path: "circuit-results",
    component: CircuitResultsComponent,
    title: "Circuit Results"
  },
  { path: "**", redirectTo: "" },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule { }
